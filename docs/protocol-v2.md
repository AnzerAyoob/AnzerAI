# AnzerAI GitHub intake protocol v2

Send requests over HTTPS. Set `Authorization: Bearer <GitHub Actions OIDC token>` with audience `urn:anzerai:github-actions:v2`. A static v1 credential cannot authenticate to v2.

Send `POST /v2/jobs` with `Content-Type: application/json`. The body accepts exactly these fields and is limited to 4096 bytes.

~~~json
{"repository":"example/project","kind":"issue","number":42}
~~~

Repository names are case-insensitive and returned in lowercase. Kind is `issue` or `pull_request`. Number is a positive integer up to 2147483647. Core checks the reference against the verified GitHub workflow run. Omit the v1 `Idempotency-Key` header. Core deduplicates by immutable repository ID and run ID.

HTTP 201 means a new authorized receipt. Identical retries that still pass verification return the same receipt with HTTP 200. `GET /v2/jobs/{id}` returns the same shape for a token from the same verified run if authorization and target evidence still match.

~~~json
{"id":"9f4a5e4b-3d8a-4fca-9d08-e31f1b20a8a1","status":"authorized","repository":"example/project","kind":"issue","number":42}
~~~

Authorized means Core verified the request at intake. To schedule a separate lifecycle check, use [protocol v3](protocol-v3.md).

| HTTP status | Error codes |
| --- | --- |
| 400 | `invalid_request`, `unexpected_idempotency_key` |
| 401 | `unauthorized` |
| 403 | `forbidden` |
| 404 | `not_found` |
| 408 | `request_timeout` |
| 409 | `submission_conflict`, such as a PR head changed after the original receipt |
| 413 | `request_too_large` |
| 415 | `unsupported_media_type` |
| 503 | `verification_unavailable`, `storage_unavailable` |

Errors use `{"error":"code"}`. No client-supplied actor, role, event name, run ID, or PR metadata is accepted. See [authorization](AUTHORIZATION.md) for supported sources and [security](SECURITY.md) for credential handling.
