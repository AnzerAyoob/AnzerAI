# AnzerAI job lifecycle protocol v3

Use the same GitHub Actions OIDC issuer and audience as [v2](protocol-v2.md). The v2 response is an admission receipt. An explicitly enqueued v3 job has its own ID and status. GitHub mode supports both versions, and legacy v1 development mode remains separate.

| Request | Behavior |
| --- | --- |
| `POST /v3/jobs` | Require JSON with `receipt_id` and optional nonnegative integer `delay_seconds`, default zero. Core rechecks the receipt and GitHub authorization, then creates one job per receipt. |
| `GET /v3/jobs/{id}` | Return the current state to the original verified workflow run and actor. |
| `POST /v3/jobs/{id}/cancel` | Record cancellation for the original verified workflow run and actor. Send an empty body. |

Status and cancellation require a fresh OIDC token matching the original enrolled workflow identity. These operations can still report or stop an existing job after its target changes. Only enqueue and worker admission perform the live target and permission checks.

Enqueue returns HTTP 201 for a new job or 200 for an identical enqueue. A different delay for an existing job returns 409. Omit the `Idempotency-Key` header. Status and cancellation return HTTP 200. Cancellation of a waiting job returns `cancelled`. Cancellation of a claimed or running job can return `cancelling` while the worker stops cooperatively. Repeated cancellation returns the current record.

The response includes `id`, `receipt_id`, `repository`, `kind`, `number`, `job_type`, `status`, `attempt_count`, `max_attempts`, `failure_category`, `created_at`, `scheduled_at`, `started_at`, `completed_at`, `cancel_requested_at`, and `cancelled_at`. Timestamps are Unix seconds, with null for milestones that have yet to occur. Status can be `queued`, `scheduled`, `claimed`, `running`, `retry_wait`, `cancelling`, `cancelled`, `succeeded`, `failed`, or `expired`. The only job type is `lifecycle_check`. Its successful result means the worker completed a lifecycle check.

| HTTP status | Error code |
| --- | --- |
| 400 | `invalid_request`, `invalid_schedule`, `unexpected_idempotency_key` |
| 401 | `unauthorized` |
| 403 | `forbidden` |
| 404 | `not_found` for unknown, out-of-scope, or unavailable receipts and jobs |
| 408 | `request_timeout` |
| 409 | `submission_conflict` |
| 413 | `request_too_large` |
| 415 | `unsupported_media_type` |
| 429 | `queue_full`, `rate_limited` |
| 503 | `verification_unavailable`, `storage_unavailable` |

Errors use `{"error":"code"}`. Queue inspection, worker health, attempt history, and revocation are private operator functions.
