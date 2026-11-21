# AnzerAI Core Architecture — Core Idea

## Purpose

AnzerAI is intended to be a centrally operated AI coding-agent product. The public repository should provide the installation/client interface, while the proprietary agent engine and orchestration logic remain under the owner's control.

Users bring their own AI provider credentials (BYOK — Bring Your Own Key). AnzerAI does not need to pay for their model inference usage, though hosting, compute, queueing, storage, and security infrastructure remain service costs.

## Repository and service layers

| Layer | Repository / location | Visibility | Responsibility |
|---|---|---|---|
| AnzerAI Client | `AnzerAyoob/AnzerAI` | Public | GitHub Action/client, installer, configuration templates, docs |
| AnzerAI Core | `AnzerAyoob/AnzerAI-Core` (planned) | Private | Agent orchestration, planner, prompts, tool policy, execution loop, recovery, model routing, security logic |
| AnzerAI API | Initially hosted alongside Core; may be split into a separate private repo later | Private service | Authenticated request intake, validation, queueing, job status, orchestration access, rate limits |
| User repository | Each user's own repository | User-controlled | Source code, issues, agent configuration, tests and GitHub permissions |
| User AI credentials | GitHub Actions secrets / secure credential handling | Private | Gemini or OpenRouter API credentials and provider usage/billing |

## Request flow

1. An event in the user's GitHub repository triggers the public AnzerAI client workflow.
2. The client authenticates to the AnzerAI service and submits the task, repository identity, relevant context, and narrowly scoped authorization.
3. AnzerAI's private API validates the request, repository authorization, and limits.
4. The private engine plans and performs the task using the configured AI provider (Gemini or OpenRouter) and permitted tools.
5. The engine returns proposed changes/results through the controlled GitHub mechanism, such as a branch and pull request.
6. The service/client reports job status. No automatic merge is enabled by default.

## BYOK provider support

- Users supply and maintain their own Gemini or OpenRouter API keys.
- Provider choice and model selection should be configurable.
- Keys must never be committed, printed, included in agent output, PR descriptions, logs, or error traces.
- Credential handling must be explicit and secure. Prefer ephemeral use for execution and avoid persistent storage unless a documented secure design requires it.
- The provider abstraction should allow adding providers without changing agent orchestration.
- Key rotation/fallback must respect provider quotas, terms, and restrictions. It must not be designed to bypass quota limits.

## Private intellectual property

Keep the following in AnzerAI Core/private infrastructure:
- Agent planner and decision-making logic
- System prompts and prompt architecture
- Agent execution/iteration loop
- Tool orchestration and execution policy
- Recovery and retry logic
- Provider routing and adapters (implementation details)
- Security enforcement and internal validation
- Internal engine improvements and release control

The public client should contain only the code needed to install, trigger, authenticate, submit requests, receive status/results, and deliver authorized GitHub changes. Do not ship the private engine or prompts in user repositories.

## Public repository contents

The public AnzerAI repository may contain:
- GitHub Action/client interface
- Installation workflow and examples
- User configuration schema/templates
- Documentation
- Client-side request validation and non-secret protocol details

The public client is not the agent engine. Its protocol must be versioned and compatible with the central service.

## Security requirements

- Authenticate clients and requests; do not trust repository or actor fields supplied by a workflow without independent validation.
- Verify GitHub actor permissions and repository authorization on the server side.
- Use least-privilege GitHub permissions and scoped tokens.
- Never accept arbitrary fork-originated requests with write credentials.
- Isolate execution, constrain tools and paths, impose time/resource limits, and validate output.
- Protect against prompt injection in issues, comments, repository files, and other untrusted content.
- Rate-limit by user, repository, and service.
- Keep audit records without secrets.
- Make clear to users that their API key is processed by AnzerAI service if their request requires the service to use it.
- Avoid exposing private engine source, prompts, internal tool policies, or credentials in client responses.

## Initial deployment recommendation

For the first MVP, keep the private engine and API service in one private repository (`AnzerAI-Core`) and deploy them together. Split the API/service repository from the engine only when independent development, deployment, scaling, or access-control needs justify the added complexity.

## Planned repository count

- **Now:** 2 repositories total — existing public `AnzerAI` client and one new private `AnzerAI-Core` repository.
- **Later, optional:** 3 repositories total if a separate private `AnzerAI-API` service repository is warranted.
- The hosting/API service is infrastructure, not automatically a separate repository.

## Status

This is the agreed architectural direction, not an implemented or deployed system. The current public repository scaffold and its open draft PR must be re-evaluated against this hosted/private-engine design before implementation continues.
