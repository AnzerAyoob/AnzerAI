"""Request an OIDC token from the GitHub Actions runner."""

import json
import re
from collections.abc import Mapping
from http.client import HTTPException
from urllib.error import HTTPError
from urllib.parse import parse_qsl, urlencode, urlsplit
from urllib.request import ProxyHandler, Request, build_opener

from anzerai_client.api import OIDC_TOKEN, ClientError, NoRedirect

AUDIENCE = "urn:anzerai:github-actions:v2"
ACTIONS_HOST = re.compile(r"(?:[a-z0-9-]+\.)+actions\.githubusercontent\.com")
RUNNER_TOKEN = re.compile(r"[-a-zA-Z0-9._~+/=]{1,16000}")
MAX_TOKEN_RESPONSE = 16384


def get_workflow_token(env: Mapping[str, str]) -> str:
    endpoint = env.get("ACTIONS_ID_TOKEN_REQUEST_URL", "")
    credential = env.get("ACTIONS_ID_TOKEN_REQUEST_TOKEN", "")
    try:
        url = urlsplit(endpoint)
        if (
            not RUNNER_TOKEN.fullmatch(credential)
            or len(endpoint) > 8192
            or any(char.isspace() or ord(char) < 32 for char in endpoint)
            or "\\" in endpoint
            or url.scheme != "https"
            or not url.hostname
            or not ACTIONS_HOST.fullmatch(url.hostname)
            or url.username is not None
            or url.port not in (None, 443)
            or "#" in endpoint
            or any(
                key.lower() == "audience"
                for key, _ in parse_qsl(url.query, max_num_fields=128)
            )
        ):
            raise ValueError
    except ValueError:
        raise ClientError(
            "GitHub Actions OIDC requires a trusted runner with id-token: write"
        ) from None

    query = urlencode({"audience": AUDIENCE})
    query = f"{url.query}&{query}" if url.query else query
    request = Request(
        url._replace(query=query).geturl(),
        headers={"Authorization": f"Bearer {credential}", "Accept": "application/json"},
    )
    opener = build_opener(NoRedirect(), ProxyHandler({}))
    try:
        with opener.open(request, timeout=10) as response:
            raw = response.read(MAX_TOKEN_RESPONSE + 1)
        if len(raw) > MAX_TOKEN_RESPONSE:
            raise ValueError
        result = json.loads(raw.decode("utf-8"))
        token = result.get("value") if isinstance(result, dict) else None
        if (
            not isinstance(token, str)
            or len(token) > 12000
            or not OIDC_TOKEN.fullmatch(token)
        ):
            raise ValueError
    except HTTPError as error:
        error.close()
        raise ClientError("GitHub Actions did not issue an OIDC token") from None
    except (OSError, HTTPException, ValueError, RecursionError):
        raise ClientError("GitHub Actions did not issue an OIDC token") from None
    return token
