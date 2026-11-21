"""Client for the version 1 AnzerAI intake protocol."""

import ipaddress
import json
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

    def _request(
        self, path: str, body: dict | None = None, key: str | None = None
    ) -> dict:
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
        request = Request(self.endpoint + path, data, headers)
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
            job = json.loads(raw.decode("utf-8"))
        except (ValueError, RecursionError):
            raise ClientError("service returned invalid JSON") from None
        if (
            not isinstance(job, dict)
            or job.keys() != {"id", "status", "repository", "kind", "number"}
            or not isinstance(job["id"], str)
            or not JOB_ID.fullmatch(job["id"])
            or job["status"] != self.expected_status
            or not isinstance(job["repository"], str)
            or not REPOSITORY.fullmatch(job["repository"])
            or job["repository"].split("/")[1] in {".", ".."}
            or job["repository"] != job["repository"].lower()
            or job["kind"] not in ("issue", "pull_request")
            or type(job["number"]) is not int
            or not 1 <= job["number"] <= 2**31 - 1
        ):
            raise ClientError("service returned an invalid job record")
        return job
