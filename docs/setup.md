# Installation and setup

## 1. Add the repository secret

In each target repository, open **Settings → Secrets and variables → Actions → New repository secret**.

- Name: `ANZERAI_API_KEY`
- Value: the private access key used by your AnzerAI deployment.

Do not commit the key to the repository, place it in a workflow input, or paste it into an issue or pull request.

## 2. Install the caller workflow

Copy [examples/caller.yml](../examples/caller.yml) into the target repository at `.github/workflows/anzerai.yml`.

The caller must use a published version tag. Do not point privileged automation at a moving branch. After publishing a reviewed release, update the tag reference deliberately.

## 3. Add repository instructions

Create an `AGENTS.md` at the root. Document the language, framework, package manager, runtime versions, important directories, entry points, test/lint/format/build commands, and project-specific coding conventions. Do not put secrets or private configuration in this file.

## 4. Trigger a run

- Add the `ai-agent` label to an issue to request a new implementation branch and pull request.
- Comment `/agent` on an issue to ask AnzerAI to work on it.
- Comment `/agent` on a pull request in the same repository to request a targeted commit on the PR branch.

Only owners, members, and collaborators are accepted. Fork pull requests are deliberately excluded from write-enabled runs.

## 5. Required GitHub settings

Enable GitHub Actions; ensure workflow token permissions include contents, issues, and pull requests; protect the default branch with required checks/reviews; and review the first run carefully.
