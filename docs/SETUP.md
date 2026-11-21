# GitHub workflow setup

Use the [manual-dispatch example](../examples/anzerai.yml) after the Core operator provides an HTTPS service origin and a reviewed public client commit is reachable on GitHub.

1. Copy the example to `.github/workflows/anzerai.yml` in the target repository. Set the HTTPS service origin and pin the public client to its reviewed 40-character commit SHA. Keep the input names and `run-name` expression intact.
2. Put the workflow on the protected default branch and have the Core operator enroll the repository, GitHub App installation, numeric owner and repository IDs, and reviewed caller commit SHA. Update the Core pin when the approved default-branch revision changes. Plan the update with the operator so the new revision is available for dispatch.
3. In GitHub Actions, open **AnzerAI authorization** and run it from the default branch with a kind and an issue or pull request number. Use a new dispatch for a new submission.

The sample job requests `id-token: write`. This allows the job to obtain an OIDC token. It grants no repository write permission. The client uses the runner-provided `ACTIONS_ID_TOKEN_REQUEST_URL` and `ACTIONS_ID_TOKEN_REQUEST_TOKEN` to request the fixed audience `urn:anzerai:github-actions:v2`. The sample fetches only the pinned public client revision. Use the job solely for the reviewed submission logic and pass values through environment variables. Do not add code from the target repository or a pull request to the job, or forward repository secrets to it.

The CLI commands in that job are:

~~~sh
python3.12 -m anzerai_client submit-github --repository "$GITHUB_REPOSITORY" --kind "$TASK_KIND" --number "$TASK_NUMBER"
python3.12 -m anzerai_client status-github JOB_ID
~~~

Status requires an OIDC token from the same first-attempt workflow run and repeats authorization checks. Core returns a receipt, and Phase 2 stops at admission. For local Phase 1 development, see [protocol v1](protocol-v1.md).

[GitHub OIDC reference](https://docs.github.com/en/actions/reference/security/oidc) · [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
