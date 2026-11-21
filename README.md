# AnzerAI

AnzerAI is the MIT-licensed public client for a separate private service. The client submits GitHub issue and pull request references over a versioned JSON API.

Phase 2 adds GitHub Actions OIDC authorization for manually dispatched workflows. Core validates the workflow and actor against GitHub and checks the target before issuing an authorized receipt. This branch is local development work.

- [Set up a GitHub workflow](docs/SETUP.md)
- [Authorization](docs/AUTHORIZATION.md)
- [Security](docs/SECURITY.md)
- [GitHub intake protocol v2](docs/protocol-v2.md)
- [Legacy development protocol v1](docs/protocol-v1.md)
- [Roadmap](docs/ROADMAP.md)
- [Architecture decision](docs/CORE_ARCHITECTURE.md)

## Development

Use Python 3.12.

~~~sh
python -m pip install ruff==0.17.6
python -m unittest discover -s tests -v
python -m compileall -q anzerai_client tests
python -m ruff check .
python -m ruff format --check .
~~~

See [LICENSE](LICENSE).
