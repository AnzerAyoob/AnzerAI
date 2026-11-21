# Configure a provider key

Your repository must be enrolled for GitHub OIDC and your chosen provider/model must be enabled by the Core operator. The current job sends a fixed connectivity prompt. Provider accounts and usage may incur charges.

Store your own key as a GitHub Actions secret, for example `ANZERAI_PROVIDER_API_KEY`. Set that secret as the step environment variable of the same name in the approved default-branch workflow. Keep GitHub fork and workflow protections intact. Use the key only in the inference enqueue step. Retain a pinned revision of the public client and coordinate workflow pin changes with the Core operator.

~~~sh
python3.12 -m anzerai_client infer-github RECEIPT_ID --provider gemini --model APPROVED_MODEL
python3.12 -m anzerai_client inference-github JOB_ID
python3.12 -m anzerai_client cancel-inference-github JOB_ID
~~~

Use `openrouter` and an approved `vendor/model` ID for OpenRouter. The client requires HTTPS when sending credentials. It sends the key in a dedicated header alongside GitHub OIDC and omits it from status and cancellation. Core decrypts the job-scoped key for the authorized attempt and deletes the encrypted row on cancellation, completion, or expiry cleanup. A request already sent to a provider may still complete or be billed. You can independently revoke a key with your provider.

Use `--provider mock --model mock-text` with a mock-enabled local Core for a free probe. Leave the provider-key environment variable unset in that case.

For a bounded repository planning job using the same credential flow, see [analysis setup](ANALYSIS.md). See the [API contract](API.md) and [GitHub setup](SETUP.md).
