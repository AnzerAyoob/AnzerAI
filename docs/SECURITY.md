# Security

V5 analysis accepts only an explicit text snapshot and matches its declared scope to the original workflow receipt. Inspect the snapshot before submission. Secret filtering is heuristic, and the chosen provider sees selected context. Treat model plans as untrusted proposals. [Analysis setup](ANALYSIS.md)

V4 real-provider submissions require HTTPS and an admitted GitHub workflow. Use a repository secret for the provider key and expose it only to the pinned enqueue step. Results are untrusted text and may expire from the API. See [BYOK](BYOK.md).

Phase 2 verifies identities and stores receipts. The caller workflow gets an OIDC identity and receives a receipt. The private service authenticates to GitHub through a repository-scoped, read-only GitHub App installation token that stays server-side.

- Keep the caller workflow on a protected default branch and pin the public client commit. Run the example job on a GitHub-hosted runner and keep PR and target repository code out of the job.
- Choose the service origin in the reviewed workflow. Use HTTPS and keep Actions OIDC tokens, GitHub App credentials, and provider credentials out of logs, workflow artifacts, command arguments, and request bodies.
- Core denies admission if signature, event, actor permissions, repository, target, or origin cannot be verified. The public API returns broad error codes. Server-side security logs use fixed reason codes without request contents or credentials.
- One GitHub run can authorize one target. Repeated valid requests for the same target and head return the same receipt, and changes are denied. OIDC is a bearer credential. A stolen, valid token for that run can still submit or read the same receipt while all checks pass. Keep the token short-lived and confined to the trusted job.

Before hosted use, the service needs HTTPS termination, rate limits and authorized deployment. Later execution must recheck permissions and PR origin, including the pinned head, before obtaining any write access. GitHub's user account type cannot identify every human-operated versus automated User account.
