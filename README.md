# AnzerAI

**Your AI coding agent. Across your repositories.**

AnzerAI is a reusable GitHub coding agent for issue triage, targeted code changes, verification, and pull-request delivery. Install a small caller workflow in each repository and maintain the agent centrally.

## What it does

- Starts from an issue carrying the `ai-agent` label, or an authorized `/agent` comment on an issue or same-repository pull request.
- Reads the target repository's `AGENTS.md` and project files before editing.
- Uses bounded repository tools to inspect, search, read, edit, and verify code.
- Creates a dedicated branch and pull request for issue work.
- For authorized same-repository pull request requests, pushes a narrowly scoped commit to that PR branch.
- Reports what changed, what was tested, and any blocker. It does not merge pull requests.

## Architecture

- **Central engine:** this repository contains the agent implementation and reusable workflow.
- **Caller repository:** the workflow checks out the project being changed, so AnzerAI works with that repository's code and history.
- **Credentials:** each caller repository supplies its own Actions secret named `ANZERAI_API_KEY`. The key is never printed or included in agent tool output.

## Quick start

1. Add an Actions secret named `ANZERAI_API_KEY` to each repository that should use AnzerAI.
2. Add the caller workflow from [examples/caller.yml](examples/caller.yml) as `.github/workflows/anzerai.yml`.
3. Add or adapt an `AGENTS.md` with the exact project structure, test, and lint commands.
4. Create an issue, add the `ai-agent` label, and let the workflow run. Or comment `/agent` on an issue or eligible pull request.

See [docs/setup.md](docs/setup.md) before enabling it in production.

## Trigger rules

- Issue label event: the issue must receive the `ai-agent` label.
- Comment event: the comment must contain `/agent` as a standalone command.
- Only repository owners, members, or collaborators may trigger execution.
- Pull-request comment execution is limited to PRs whose head branch belongs to the same repository. Fork PRs are never given write credentials.
- Workflow concurrency prevents overlapping agent runs against the same issue or PR.

## Security model and limitations

An autonomous coding agent with write access is a privileged automation. AnzerAI uses least-privilege workflow permissions, author-association checks, same-repository PR restrictions, bounded tool execution, path validation, secret redaction, and command restrictions. These controls reduce risk; they do not make arbitrary shell execution safe. Review changes and workflow logs, protect your default branch, and use repository rulesets.

Do not put production secrets in files accessible to the agent. Do not enable this workflow in repositories where issue or pull-request content is untrusted without reviewing the threat model.

## Development

```bash
python -m pip install -r .github/scripts/requirements.txt
python -m unittest discover -s tests -v
python -m compileall -q .github/scripts
```

## License

MIT. See [LICENSE](LICENSE).
