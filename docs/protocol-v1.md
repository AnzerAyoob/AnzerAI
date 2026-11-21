# AnzerAI intake protocol v1

> Legacy loopback development protocol. Core enables v1 only when ANZERAI_ENABLE_LEGACY_INTAKE=1 and GitHub mode is unconfigured. V1 receipts remain unverified and cannot be read or promoted through v2. For GitHub workflows, use [protocol v2](protocol-v2.md).

The public client authenticates to the service using the Authorization header with the Bearer scheme. The credential is issued for a single repository. ANZERAI_API_KEY is a service credential. BYOK provider credentials are handled separately in the planned execution flow.

Send POST /v1/jobs with Content-Type application/json and an Idempotency-Key of 1–128 ASCII letters, digits, underscores, or hyphens. The JSON object accepts exactly these fields.

~~~json
{"repository":"example/project","kind":"issue","number":42}
~~~

Repository names are returned in lowercase. The kind must be issue or pull_request. The number must be an integer between 1 and 2147483647 inclusive. The request body is limited to 4096 bytes.

A successful response is HTTP 201 for a new submission or HTTP 200 when the same repository reuses the key with the same reference. A successful GET /v1/jobs/{id} returns HTTP 200 with the same shape.

~~~json
{"id":"9f4a5e4b-3d8a-4fca-9d08-e31f1b20a8a1","status":"received","repository":"example/project","kind":"issue","number":42}
~~~

Received means that the reference was recorded. It gives no assurance about the referenced GitHub object, actor, or execution eligibility. GET /healthz returns HTTP 200 with {"status":"ok"} for local liveness checks.

| HTTP status | Meaning |
| --- | --- |
| 400 | Malformed request or idempotency key |
| 401 | Missing or invalid service credential |
| 403 | The submission names a repository outside the credential's scope |
| 404 | Unknown route, missing receipt, or receipt outside the credential's scope |
| 408 | Reading the request timed out |
| 409 | A key was previously used for a different reference in the same repository |
| 413 | The request body exceeds the byte limit |
| 415 | The request uses an unsupported content type |
| 503 | The service could not access receipt storage |

The intake accepts references only. Workflows should keep provider credentials, GitHub write tokens, issue text, and repository contents out of these requests.
