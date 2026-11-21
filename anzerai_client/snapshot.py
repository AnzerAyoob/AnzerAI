"""Load the caller's explicit snapshot document without traversing its file entries."""

import json
import os
import stat
from pathlib import Path

from anzerai_client.api import ClientError

MAX_BYTES = 3_500_000
FIELDS = {
    "version",
    "repository",
    "repository_id",
    "owner_id",
    "revision",
    "provenance",
    "files",
}
PRIVATE_COMPONENTS = {
    ".git",
    ".ssh",
    ".aws",
    ".azure",
    ".gnupg",
    "secrets",
    "credentials",
}


def unique(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ValueError
        result[name] = value
    return result


def read_snapshot(name: str) -> dict:
    try:
        raw_path = Path(name)
        if (
            not raw_path.parts
            or raw_path.anchor
            or ".." in raw_path.parts
            or raw_path.suffix.lower() != ".json"
            or any(
                part.lower() in PRIVATE_COMPONENTS or part.lower().startswith(".env")
                for part in raw_path.parts
            )
            or any(
                word in raw_path.name.lower()
                for word in ("credential", "secret", "keyring", "service-account")
            )
        ):
            raise ValueError
        root = Path.cwd().resolve()
        file = root
        for part in raw_path.parts:
            file /= part
            if file.is_symlink() or file.is_junction():
                raise ValueError
        resolved = file.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise ValueError
        expected = resolved.stat()
        if not stat.S_ISREG(expected.st_mode):
            raise ValueError
        with resolved.open("rb") as stream:
            if not os.path.samestat(expected, os.fstat(stream.fileno())):
                raise ValueError
            data = stream.read(MAX_BYTES + 1)
        if len(data) > MAX_BYTES:
            raise ValueError
        snapshot = json.loads(data.decode("utf-8"), object_pairs_hook=unique)
        if (
            not isinstance(snapshot, dict)
            or snapshot.keys() != FIELDS
            or type(snapshot["version"]) is not int
            or snapshot["version"] != 1
            or not isinstance(snapshot["files"], list)
        ):
            raise ValueError
        return snapshot
    except (OSError, ValueError, RecursionError):
        raise ClientError(
            "invalid snapshot document within the current workspace"
        ) from None
