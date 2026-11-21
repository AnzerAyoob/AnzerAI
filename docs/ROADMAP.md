# AnzerAI roadmap

| Phase | Status | Scope |
| --- | --- | --- |
| 0. Repository audit | Complete | Reviewed the public draft and recorded the public/private architecture. |
| 1. Core foundation | Complete locally | Versioned client intake and SQLite receipts on local feature branches. |
| 2. GitHub identity and authorization | Complete locally | GitHub OIDC, repository and actor authorization, event binding, and fork protection. Live GitHub Actions-to-Core validation is pending. |
| 3. Authorized job lifecycle | Complete locally | Separate lifecycle jobs, SQLite queue and attempt history, worker reauthorization, fenced leases, retries, and cooperative cancellation. Verification uses offline fixtures. |
| 4. AI provider abstraction and BYOK | Complete locally | Gemini and OpenRouter adapters, encrypted job-scoped keys, normalized usage and inference probes. Live provider smoke tests are pending. |
| 5. Repository analysis and planning engine | Complete locally | Versioned caller snapshots, deterministic inventory and selection, validated evidence-grounded plans, and offline worker/API tests. |
| 6. Controlled coding tools and isolated execution | Pending | Restrict tools and isolate execution. |
| 7. Testing and self-repair | Pending | Verification and bounded repair. |
| 8. GitHub delivery | Pending | Authorized change delivery. |
| 9. End-to-end and security validation | Pending | Validate the integrated service and its security boundaries. |
| 10. Deployment readiness | Pending | Operational readiness and release checks. |

This roadmap records local development status. See the [architecture decision](CORE_ARCHITECTURE.md) and [Phase 0 audit](REPOSITORY_AUDIT.md).
