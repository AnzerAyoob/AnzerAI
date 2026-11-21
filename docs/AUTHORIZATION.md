# GitHub authorization

| Event | Issue | Pull request | Conditions |
| --- | --- | --- | --- |
| `workflow_dispatch`, first attempt | Open, unlocked issue | Open, unlocked same-repository pull request with a human author | Enrolled repository, approved workflow revision on the current default branch, authorized human actor |
| Issue label or issue comment | Denied | Denied | GitHub event authorization for these sources is pending |
| `pull_request` or `pull_request_target` | Denied | Denied | Pull requests enter through manual dispatch only |
| Re-run, non-default ref, or any other event | Denied | Denied | A fresh dispatch on the approved ref is required |

GitHub Actions attests the caller, repository, workflow, commit and run. Core uses GitHub's official OIDC issuer and signing keys, a fixed audience, and live GitHub App checks. GitHub supplies the recorded run title through its Actions API. The reviewed workflow sets that title from the dispatch inputs, and Core requires it to match the request. The JSON request carries only a repository, kind, and number.

By default, Core accepts a personal repository owner with verified admin permissions or a repository administrator. An operator can opt in to GitHub's standard maintainer or write role per repository. Organization membership and external contributor status do not independently confer access. GitHub returns the effective repository role without distinguishing direct grants from organization or team grants. Read, triage, custom and unknown roles, missing identities, and GitHub bot accounts are denied.

For pull requests, GitHub must return both head and base in the same enrolled repository and a verifiable head commit. Fork PRs, deleted heads, foreign bases, and bot-authored PRs are denied. The receipt is bound to that head commit.

[GitHub workflow runs API](https://docs.github.com/en/rest/actions/workflow-runs) · [GitHub collaborator permissions](https://docs.github.com/en/rest/collaborators/collaborators#get-repository-permissions-for-a-user)
