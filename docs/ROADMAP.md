# AnzerAI roadmap

| Phase | Status | Scope |
| --- | --- | --- |
| 0. Repository audit | Complete | Reviewed the public draft, established the public/private boundary, and recorded the architecture and audit findings. |
| 1. Core foundation | Complete locally | Implemented the versioned CLI-to-Core intake and SQLite receipts on local feature branches. |
| 2. GitHub identity and authorization | In progress for live GitHub validation | Local implementation covers GitHub OIDC, repository enrollment, actor permissions, manual event binding, fork protection, and run deduplication. Local tests use offline GitHub fixtures. |
| 3. Authorized job lifecycle | Pending | Define job state, queue and limits. Recheck admission, actor permissions and target state before a job can start. |
| Later phases | Pending | Isolated execution, BYOK integration, and controlled delivery after separate design and validation. |

The public client and proprietary Core remain in separate repositories. This roadmap describes development status. See the [architecture decision](CORE_ARCHITECTURE.md) and [Phase 0 audit](REPOSITORY_AUDIT.md).
