# Analyze a repository snapshot

From the same enrolled workflow that received the admission receipt, run:

~~~sh
python3.12 -m anzerai_client analyze-github RECEIPT_ID --provider mock --model mock-text --context snapshot.json --task "Fix the session refresh regression"
python3.12 -m anzerai_client analysis-github JOB_ID
python3.12 -m anzerai_client cancel-analysis-github JOB_ID
~~~

The Core operator must enable analysis, an allowed model, and a keyring for queued context. For a real provider, use an approved JSON-capable model and the [BYOK setup](BYOK.md). Only include files suitable to share with the configured provider. The task is supplied by the caller and must never contain credentials.

The context document must be a UTF-8 file with a .json extension below the CLI's working directory. A v1 snapshot contains `version` equal to 1, canonical `repository` as `owner/name`, numeric `repository_id` and `owner_id`, a lowercase 40-character `revision`, `provenance` equal to `caller_supplied`, and `files`. Each file has relative forward-slash `path`, `kind` equal to `file`, exact UTF-8 byte `size`, and inline `text`. For issue intake, use the admitted workflow SHA. For PR intake, use the admitted PR head SHA.

The client reads only that document. The Core validates declared scope, excludes sensitive and unsupported entries, and selects a bounded subset of whole files. Its plan distinguishes observed evidence from model interpretation and includes caveats, risks and future verification. Results and usage are scoped to the original workflow and expire. See [API v5](API.md#repository-analysis-v5).
