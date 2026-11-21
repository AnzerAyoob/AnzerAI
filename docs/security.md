# Security model

AnzerAI is privileged automation. A caller workflow grants it the ability to write repository contents and open pull requests. Treat it as code execution with meaningful authority.

## Implemented controls

- Caller event is filtered to the `ai-agent` issue label or a comment containing `/agent`.
- Reusable workflow repeats the author-association allowlist.
- Same-repository pull request heads only; fork PRs are rejected before writes.
- File operations are confined to the checked-out target repository and exclude the engine checkout.
- Workflow files and root `AGENTS.md` are protected from editing.
- Tool calls are explicit, bounded, and limited to eight turns.
- Shell commands have a 60-second timeout, a maximum length, blocked destructive patterns, and no network/remote git operations.
- Credentials are passed only through the process environment and are never supplied to the model.
- No auto-merge operation exists in the engine.

## Important limitations

1. **A shell denylist is not a sandbox.** Shell commands can still behave unexpectedly. Run this only in repositories you control, with protected default branches and review requirements.
2. **Repository text is untrusted input.** Issue bodies, comments, source files, test output, and AGENTS.md can contain prompt injection. Treat them as task data, never as authority to reveal credentials or bypass tool policy.
3. **GitHub write tokens are powerful.** Scope workflow permissions to contents, issues, and pull requests. Do not grant administration, Actions secrets, packages, or deployments permissions.
4. **Collaborators are trusted to request runs.** A collaborator who can trigger the agent can influence work performed with the repository token. Adjust the allowlist if your collaboration model requires stricter control.
5. **Workflow supply chain matters.** Pin third-party actions to reviewed full commit SHAs for high-assurance use.
6. **Fork PRs are not eligible.** Do not change this restriction casually.

If a run behaves unexpectedly, disable the caller workflow, rotate the per-repository key, review Actions logs and commits, inspect token permissions, and remove unauthorized changes.
