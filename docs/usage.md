# Usage

## Issue label

Apply the `ai-agent` label to an issue. AnzerAI reads the issue and recent discussion, inspects the codebase, makes bounded changes, runs documented checks, then pushes a branch and opens a pull request referencing the issue.

## Comment command

Comment with `/agent` on an issue or eligible pull request. It must be used by an owner, member, or collaborator.

For an issue, AnzerAI creates a new branch and PR. For a same-repository pull request, AnzerAI works on the PR head branch and pushes a commit there after verification.

## Run report

The report includes a summary, verification performed, and resulting PR or branch. A failed run posts a diagnostic comment and exits non-zero.
