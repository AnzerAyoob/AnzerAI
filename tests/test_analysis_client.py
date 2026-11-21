import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from test_client import Response
from test_job_client import ID, RECEIPT_ID, RECORD

from anzerai_client.api import Client, ClientError
from anzerai_client.snapshot import read_snapshot

JOB = RECORD | {"job_type": "analysis_plan"}
GENERATION = {"provider": "mock", "model": "mock-text"}


class AnalysisClientTests(unittest.TestCase):
    def test_submit_and_retrieve_analysis(self):
        client = Client(
            "https://api.example.test", "header.payload.signature", github=True
        )
        snapshot = {"version": 1, "files": []}
        with patch.object(
            client.opener, "open", return_value=Response(JOB, 201)
        ) as send:
            self.assertEqual(
                client.enqueue_analysis(
                    RECEIPT_ID, GENERATION, "", task="Fix session", context=snapshot
                ),
                JOB,
            )
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.example.test/v5/analysis")
        self.assertEqual(json.loads(request.data)["context"], snapshot)
        output = {
            "job": JOB,
            "provider": "mock",
            "model": "mock-text",
            "result": {"version": 1},
            "requests": [],
        }
        with patch.object(client.opener, "open", return_value=Response(output)):
            self.assertEqual(client.analysis(ID), output)
        with patch.object(client.opener, "open", return_value=Response(JOB)) as send:
            self.assertEqual(client.analysis(ID, cancel=True), JOB)
        self.assertEqual(send.call_args.args[0].get_method(), "POST")
        self.assertTrue(send.call_args.args[0].full_url.endswith("/cancel"))

    def test_snapshot_is_explicit_and_bounded_inside_workspace(self):
        with TemporaryDirectory(dir=Path.cwd()) as directory:
            path = Path(directory) / "snapshot.json"
            relative = path.relative_to(Path.cwd())
            path.write_text(
                json.dumps(
                    {
                        "version": 1,
                        "repository": "example/project",
                        "repository_id": 100,
                        "owner_id": 200,
                        "revision": "a" * 40,
                        "provenance": "caller_supplied",
                        "files": [{"path": "../../outside.py"}],
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(read_snapshot(os.fspath(relative))["version"], 1)
            for name in (str(path), "../snapshot.json", str(relative.parent)):
                with self.subTest(name=name), self.assertRaises(ClientError):
                    read_snapshot(name)
            with patch("anzerai_client.snapshot.Path.is_symlink", return_value=True):
                with self.assertRaises(ClientError):
                    read_snapshot(os.fspath(relative))
            with patch("anzerai_client.snapshot.Path.is_junction", return_value=True):
                with self.assertRaises(ClientError):
                    read_snapshot(os.fspath(relative))
            with patch(
                "anzerai_client.snapshot.Path.open",
                side_effect=AssertionError("secret was opened"),
            ):
                with self.assertRaises(ClientError):
                    read_snapshot("credentials.json")
            path.write_text('{"version":1,"version":2}', encoding="utf-8")
            with self.assertRaises(ClientError):
                read_snapshot(os.fspath(relative))
