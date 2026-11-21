import argparse
import json
import os

from anzerai_client.api import Client, ClientError


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Submit a reference to AnzerAI or look up its receipt."
    )
    parser.add_argument(
        "--allow-loopback-http",
        action="store_true",
        help="Use a local development service.",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    submit = commands.add_parser("submit")
    submit.add_argument("--repository", required=True)
    submit.add_argument("--kind", required=True, choices=("issue", "pull_request"))
    submit.add_argument("--number", required=True, type=int)
    submit.add_argument("--idempotency-key", required=True)
    status = commands.add_parser("status")
    status.add_argument("job_id")
    args = parser.parse_args()
    try:
        client = Client(
            os.environ.get("ANZERAI_API_URL", ""),
            os.environ.get("ANZERAI_API_KEY", ""),
            allow_loopback_http=args.allow_loopback_http,
        )
        if args.command == "submit":
            job = client.submit(
                args.repository, args.kind, args.number, args.idempotency_key
            )
        else:
            job = client.status(args.job_id)
    except ClientError as error:
        parser.exit(1, f"anzerai: {error}\n")
    print(json.dumps(job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
