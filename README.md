# AnzerAI

AnzerAI is the MIT-licensed client for a separately operated private coding service. The client and service communicate through a versioned JSON API. The [architecture decision](docs/CORE_ARCHITECTURE.md) describes the intended GitHub integration and bring-your-own-key model.

Phase 1 supports submitting an issue or pull request reference and looking up its receipt. A receipt is stored as received while GitHub verification and processing are pending implementation. This branch has no installable GitHub Actions release.

## Local development

Use Python 3.12. Set ANZERAI_API_URL to the service origin and ANZERAI_API_KEY to the repository's AnzerAI client credential in your shell environment.

~~~sh
python -m anzerai_client submit --repository example/project --kind issue --number 42 --idempotency-key delivery-42
python -m anzerai_client status JOB_ID
~~~

Use the same idempotency key when retrying the same submission. For a loopback development server, set the origin to http://127.0.0.1:8765 and place --allow-loopback-http before the subcommand. The client otherwise requires HTTPS and refuses redirects.

~~~sh
python -m pip install ruff==0.17.6
python -m unittest discover -s tests -v
python -m compileall -q anzerai_client tests
python -m ruff check .
python -m ruff format --check .
~~~

See [the v1 protocol](docs/protocol-v1.md) and [LICENSE](LICENSE).
