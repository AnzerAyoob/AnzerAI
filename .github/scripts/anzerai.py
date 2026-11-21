#!/usr/bin/env python3
"""AnzerAI minimal agent entrypoint; full implementation follows in next hardening pass."""
import os
import sys

def main():
    required = ["ANZERAI_API_KEY", "GITHUB_TOKEN", "GITHUB_REPOSITORY", "ISSUE_NUMBER"]
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise RuntimeError("Missing required runner configuration: " + ", ".join(missing))
    raise RuntimeError("AnzerAI engine scaffold is not yet enabled. Install the completed engine release before using the reusable workflow.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
