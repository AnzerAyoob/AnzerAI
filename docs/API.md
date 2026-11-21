# Public API contracts

- [Legacy receipt protocol v1](protocol-v1.md)
- [GitHub admission protocol v2](protocol-v2.md)
- [Lifecycle check protocol v3](protocol-v3.md)

## Inference v4

In GitHub mode, submit `POST /v4/inference` with the original run's OIDC bearer token and a JSON body containing `receipt_id`, `generation`, and optional `delay_seconds`. Generation takes `provider`, `model`, `max_output_tokens`, `timeout`, and optional `temperature`. Gemini and OpenRouter use the `AnzerAI-Provider-Key` HTTPS header. The mock provider uses no key. Inference model IDs must appear on the service allowlist.

The route returns the new job with HTTP 201 or the existing job with 200. A receipt can schedule one compatible job. Reusing a receipt with different preferences returns 409. It does not replace the credential.

Use `GET /v4/inference/{id}` to retrieve the job, provider and model, normalized request history, and a complete result or null. The result is time-limited. Access is scoped to the original verified run, actor and repository. Send `POST /v4/inference/{id}/cancel` with an empty body to cancel. Omit the provider key from either operation.

The only v4 job type is `inference_probe`. A result is untrusted text from a fixed connectivity prompt. The API contains no repository coding or tool operations. Errors use stable codes in `{"error":"code"}` responses. See [BYOK setup](BYOK.md).

## Repository analysis v5

Send POST /v5/analysis with the original workflow's OIDC bearer, receipt_id, generation, task, and context. The provider-key header uses the same HTTPS rules as v4. The versioned context contains declared repository identity, revision, and text files. Its declared scope must match the admitted task. Core labels the contents as caller-supplied.

GET /v5/analysis/{id} returns the job, provider/model, usage ledger, and an expiring structured result or null. POST /v5/analysis/{id}/cancel cancels with an empty body. Both require the same workflow identity. Core rechecks live authority for result retrieval. Invalid context or policy budgets return 400, scope or authorization mismatches return 403, foreign jobs return 404, and queue limits return 429. When enabled, submitted content is bounded separately from ordinary inference requests.

See [analysis commands and schema](ANALYSIS.md).
