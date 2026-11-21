# Public API contracts

- [Legacy receipt protocol v1](protocol-v1.md)
- [GitHub admission protocol v2](protocol-v2.md)
- [Lifecycle check protocol v3](protocol-v3.md)

## Inference v4

In GitHub mode, submit `POST /v4/inference` with the original run's OIDC bearer token and a JSON body containing `receipt_id`, `generation`, and optional `delay_seconds`. Generation takes `provider`, `model`, `max_output_tokens`, `timeout`, and optional `temperature`. Gemini and OpenRouter use the `AnzerAI-Provider-Key` HTTPS header. The mock provider uses no key. Inference model IDs must appear on the service allowlist.

The route returns the new job with HTTP 201 or the existing job with 200. A receipt can schedule one compatible job. Reusing a receipt with different preferences returns 409. It does not replace the credential.

Use `GET /v4/inference/{id}` to retrieve the job, provider and model, normalized request history, and a complete result or null. The result is time-limited. Access is scoped to the original verified run, actor and repository. Send `POST /v4/inference/{id}/cancel` with an empty body to cancel. Omit the provider key from either operation.

The only v4 job type is `inference_probe`. A result is untrusted text from a fixed connectivity prompt. The API contains no repository coding or tool operations. Errors use stable codes in `{"error":"code"}` responses. See [BYOK setup](BYOK.md).
