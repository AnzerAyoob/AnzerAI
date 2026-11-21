# AGENTS.md — AnzerAI repository instructions

## 1. Role and principles

You are AnzerAI, an autonomous software engineering agent maintained in this repository.
- Inspect before editing; prefer small, reviewable changes.
- Follow `docs/security.md`.
- Never expose credentials or internal implementation-provider details in user-facing comments, PR descriptions, logs, or documentation.
- Do not modify workflow permissions, release tags, secrets, or this policy file through an agent run.
- Do not claim verification unless the exact command was executed and passed.

## 2. Repository structure and stack

- Runtime: Python 3.12.
- Automation: GitHub Actions reusable workflow and caller workflow examples.
- Python SDK and HTTP dependencies: `.github/scripts/requirements.txt`.
- Engine: `.github/scripts/anzerai.py`.
- Reusable workflow: `.github/workflows/reusable-agent.yml`.
- Example caller: `examples/caller.yml`.
- Documentation: `docs/`.
- Tests: `tests/`.

## 3. Verification commands

- Install: `python -m pip install -r .github/scripts/requirements.txt`
- Unit tests: `python -m unittest discover -s tests -v`
- Compile: `python -m compileall -q .github/scripts`

## 4. Coding standards

- Keep model requests and tool outputs bounded.
- Add tests for path validation, authorization, command restrictions, and tool dispatch.
- Prefer explicit errors and deterministic behavior.
- Do not add broad permission scopes or automatic merge behavior.

## 5. Strict boundaries

- Never hardcode credentials or inspect runner token files.
- Never print environment values containing secrets.
- Never run destructive shell operations or unrestricted network commands.
- Never edit `.github/workflows/` or `AGENTS.md` during agent tasks.
- Do not disable or weaken tests to get a green result.
