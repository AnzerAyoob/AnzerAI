"""Client for AnzerAI receipt and lifecycle protocols."""

import ipaddress
import json
import math
import re
from http.client import HTTPException
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

TOKEN = re.compile(r"[a-zA-Z0-9_-]{43,128}")
OIDC_TOKEN = re.compile(r"[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+")
JOB_ID = re.compile(r"[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}")
IDEMPOTENCY_KEY = re.compile(r"[a-zA-Z0-9_-]{1,128}")
REPOSITORY = re.compile(r"[a-z0-9][a-z0-9-]{0,38}/[a-z0-9_.-]{1,100}", re.ASCII | re.I)
MAX_RESPONSE_BYTES = 8192
JOB_STATES = {
    "queued",
    "scheduled",
    "claimed",
    "running",
    "retry_wait",
    "cancelling",
    "cancelled",
    "succeeded",
    "failed",
    "expired",
}
JOB_TIMES = {
    "created_at",
    "scheduled_at",
    "started_at",
    "completed_at",
    "cancel_requested_at",
    "cancelled_at",
}
JOB_FAILURES = {
    "authorization_denied",
    "admission_revoked",
    "verification_unavailable",
    "lease_expired",
    "runtime_expired",
    "job_age_exceeded",
    "queue_wait_exceeded",
    "worker_shutdown",
    "internal_error",
}


class ClientError(Exception):
    """A request failed without exposing headers or an upstream response body."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(
        self,
        endpoint: str,
        token: str,
        *,
        allow_loopback_http: bool = False,
        github: bool = False,
    ):
        try:
            url = urlsplit(endpoint)
            port = url.port
            if (
                not url.hostname
                or port == 0
                or url.netloc.endswith(":")
                or url.netloc != url.netloc.strip()
                or any(char.isspace() or ord(char) < 32 for char in endpoint)
                or url.username is not None
                or "\\" in endpoint
                or url.path not in ("", "/")
                or "?" in endpoint
                or "#" in endpoint
            ):
                raise ValueError
            if url.scheme == "http" and allow_loopback_http:
                if not ipaddress.ip_address(url.hostname).is_loopback:
                    raise ValueError
            elif url.scheme != "https":
                raise ValueError
        except ValueError:
            raise ClientError(
                "ANZERAI_API_URL must be an HTTPS service origin"
            ) from None
        if github:
            if len(token) > 12000 or not OIDC_TOKEN.fullmatch(token):
                raise ClientError("GitHub Actions OIDC token is required")
        elif not TOKEN.fullmatch(token):
            raise ClientError("ANZERAI_API_KEY must be a valid client credential")
        self.github = github
        self.jobs_url = "/v2/jobs" if github else "/v1/jobs"
        self.expected_status = "authorized" if github else "received"
        self.endpoint = f"{url.scheme}://{url.netloc}"
        self.token = token
        self.opener = build_opener(NoRedirect(), ProxyHandler({}))

    def submit(
        self,
        repository: str,
        kind: str,
        number: int,
        idempotency_key: str | None = None,
    ) -> dict:
        if not REPOSITORY.fullmatch(repository) or repository.split("/")[1] in {
            ".",
            "..",
        }:
            raise ClientError("invalid repository")
        if (
            kind not in ("issue", "pull_request")
            or type(number) is not int
            or not 1 <= number <= 2**31 - 1
        ):
            raise ClientError("invalid issue or pull request reference")
        if self.github and idempotency_key is not None:
            raise ClientError("GitHub submissions are deduplicated by workflow run")
        if not self.github and not IDEMPOTENCY_KEY.fullmatch(idempotency_key or ""):
            raise ClientError("invalid idempotency key")
        body = {"repository": repository.lower(), "kind": kind, "number": number}
        job = self._request(self.jobs_url, body, idempotency_key)
        if any(job[key] != value for key, value in body.items()):
            raise ClientError("service returned a different request reference")
        return job

    def status(self, job_id: str) -> dict:
        if not JOB_ID.fullmatch(job_id):
            raise ClientError("invalid job ID")
        job = self._request(f"{self.jobs_url}/{job_id}")
        if job["id"] != job_id:
            raise ClientError("service returned a different job ID")
        return job

    def enqueue(self, receipt_id: str, delay_seconds: int = 0) -> dict:
        self._require_lifecycle_id(receipt_id)
        if type(delay_seconds) is not int or not 0 <= delay_seconds <= 86400:
            raise ClientError("invalid schedule delay")
        result = self._lifecycle(
            "/v3/jobs", {"receipt_id": receipt_id, "delay_seconds": delay_seconds}
        )
        if result["receipt_id"] != receipt_id:
            raise ClientError("service returned a different admission receipt")
        return result

    def job(self, job_id: str) -> dict:
        return self._job_action(job_id, "")

    def cancel(self, job_id: str) -> dict:
        return self._job_action(job_id, "/cancel")

    def _require_lifecycle_id(self, value: str) -> None:
        if not self.github or not JOB_ID.fullmatch(value):
            raise ClientError("lifecycle operations require a valid ID and GitHub OIDC")

    def _job_action(self, job_id: str, suffix: str) -> dict:
        self._require_lifecycle_id(job_id)
        result = self._lifecycle(
            f"/v3/jobs/{job_id}{suffix}", method="POST" if suffix else "GET"
        )
        if result["id"] != job_id:
            raise ClientError("service returned a different job ID")
        return result

    def _lifecycle(
        self, path: str, body: dict | None = None, *, method: str | None = None
    ) -> dict:
        result = self._exchange(path, body, method=method)
        fields = {
            "id",
            "receipt_id",
            "repository",
            "kind",
            "number",
            "job_type",
            "status",
            "attempt_count",
            "max_attempts",
            "failure_category",
        } | JOB_TIMES
        if (
            not isinstance(result, dict)
            or result.keys() != fields
            or not all(
                isinstance(result[k], str) and JOB_ID.fullmatch(result[k])
                for k in ("id", "receipt_id")
            )
            or not valid_reference(result)
            or result["job_type"] != "lifecycle_check"
            or not isinstance(result["status"], str)
            or result["status"] not in JOB_STATES
            or not all(
                type(result[k]) is int for k in ("attempt_count", "max_attempts")
            )
            or not 0 <= result["attempt_count"] <= result["max_attempts"] <= 10
            or result["max_attempts"] < 1
            or (
                result["failure_category"] is not None
                and (
                    not isinstance(result["failure_category"], str)
                    or result["failure_category"] not in JOB_FAILURES
                )
            )
            or not all(valid_timestamp(result[k]) for k in JOB_TIMES)
            or result["created_at"] is None
            or result["scheduled_at"] is None
        ):
            raise ClientError("service returned an invalid lifecycle record")
        return result

    def _exchange(
        self,
        path: str,
        body: dict | None = None,
        key: str | None = None,
        *,
        method: str | None = None,
    ) -> object:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        data = None
        if body is not None:
            headers["Content-Type"] = "application/json"
            if key is not None:
                headers["Idempotency-Key"] = key
            data = json.dumps(body).encode("utf-8")
        request = Request(self.endpoint + path, data, headers, method=method)
        try:
            with self.opener.open(
                request, timeout=45 if self.github else 10
            ) as response:
                allowed_status = {200} if body is None else {200, 201}
                if response.status not in allowed_status:
                    raise ClientError("service returned an unexpected status")
                if response.headers.get_content_type() != "application/json":
                    raise ClientError("service returned an unexpected content type")
                raw = response.read(MAX_RESPONSE_BYTES + 1)
        except HTTPError as error:
            error.close()
            raise ClientError(
                f"service rejected the request (HTTP {error.code})"
            ) from None
        except (URLError, OSError, HTTPException, UnicodeError):
            raise ClientError("could not reach the AnzerAI service") from None
        if len(raw) > MAX_RESPONSE_BYTES:
            raise ClientError("service response exceeded the size limit")
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, RecursionError):
            raise ClientError("service returned invalid JSON") from None

    def _request(
        self, path: str, body: dict | None = None, key: str | None = None
    ) -> dict:
        job = self._exchange(path, body, key)
        if (
            not isinstance(job, dict)
            or job.keys() != {"id", "status", "repository", "kind", "number"}
            or not isinstance(job["id"], str)
            or not JOB_ID.fullmatch(job["id"])
            or job["status"] != self.expected_status
            or not valid_reference(job)
        ):
            raise ClientError("service returned an invalid job record")
        return job


def valid_reference(record: dict) -> bool:
    repository = record["repository"]
    return (
        isinstance(repository, str)
        and bool(REPOSITORY.fullmatch(repository))
        and repository.split("/")[1] not in {".", ".."}
        and repository == repository.lower()
        and record["kind"] in ("issue", "pull_request")
        and type(record["number"]) is int
        and 1 <= record["number"] <= 2**31 - 1
    )


def valid_timestamp(value: object) -> bool:
    return value is None or (
        type(value) in (int, float)
        and 0 <= value <= 253402300799
        and math.isfinite(value)
    )
