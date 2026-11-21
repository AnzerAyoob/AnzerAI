import argparse
import json
import os

from anzerai_client.api import Client, ClientError
from anzerai_client.github import get_workflow_token


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
    for command in ("submit", "submit-github"):
        submit = commands.add_parser(command)
        submit.add_argument("--repository", required=True)
        submit.add_argument("--kind", required=True, choices=("issue", "pull_request"))
        submit.add_argument("--number", required=True, type=int)
        if command == "submit":
            submit.add_argument("--idempotency-key", required=True)
    enqueue = commands.add_parser("enqueue-github")
    enqueue.add_argument("receipt_id")
    enqueue.add_argument("--delay-seconds", type=int, default=0)
    for command in ("status", "status-github", "job-github", "cancel-github"):
        status = commands.add_parser(command)
        status.add_argument("job_id")
    args = parser.parse_args()
    try:
        github = args.command.endswith("-github")
        token = (
            get_workflow_token(os.environ)
            if github
            else os.environ.get("ANZERAI_API_KEY", "")
        )
        client = Client(
            os.environ.get("ANZERAI_API_URL", ""),
            token,
            allow_loopback_http=args.allow_loopback_http,
            github=github,
        )
        if args.command.startswith("submit"):
            job = client.submit(
                args.repository,
                args.kind,
                args.number,
                getattr(args, "idempotency_key", None),
            )
        elif args.command == "enqueue-github":
            job = client.enqueue(args.receipt_id, args.delay_seconds)
        elif args.command == "job-github":
            job = client.job(args.job_id)
        elif args.command == "cancel-github":
            job = client.cancel(args.job_id)
        else:
            job = client.status(args.job_id)
    except ClientError as error:
        parser.exit(1, f"anzerai: {error}\n")
    print(json.dumps(job))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
