import json
import unittest
from unittest.mock import patch

from test_client import JOB, Response

from anzerai_client.api import Client, ClientError

RECEIPT_ID = JOB["id"]
ID = "b1f0121c-3d8a-4fca-9d08-e31f1b20a8a1"
RECORD = {
    **JOB,
    "id": ID,
    "receipt_id": RECEIPT_ID,
    "job_type": "lifecycle_check",
    "status": "queued",
    "attempt_count": 0,
    "max_attempts": 3,
    "failure_category": None,
    "created_at": 1700000000,
    "scheduled_at": 1700000000,
    "started_at": None,
    "completed_at": None,
    "cancel_requested_at": None,
    "cancelled_at": None,
}


class JobClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client(
            "https://api.example.test", "header.payload.signature", github=True
        )

    def test_enqueue_returns_job_with_separate_receipt_id(self):
        with patch.object(
            self.client.opener, "open", return_value=Response(RECORD, 201)
        ) as send:
            self.assertEqual(self.client.enqueue(RECEIPT_ID, 5), RECORD)
        request = send.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, "https://api.example.test/v3/jobs")
        self.assertEqual(
            json.loads(request.data), {"receipt_id": RECEIPT_ID, "delay_seconds": 5}
        )

    def test_status_and_cancellation(self):
        for action, method, suffix, status in (
            (self.client.job, "GET", "", "running"),
            (self.client.cancel, "POST", "/cancel", "cancelling"),
        ):
            with patch.object(
                self.client.opener,
                "open",
                return_value=Response(RECORD | {"status": status}),
            ) as send:
                self.assertEqual(action(ID)["status"], status)
            request = send.call_args.args[0]
            self.assertEqual(request.get_method(), method)
            self.assertTrue(request.full_url.endswith(f"/v3/jobs/{ID}{suffix}"))
            self.assertIsNone(request.data)

    def test_rejects_wrong_receipt_and_unexpected_lifecycle_responses(self):
        for result in (
            JOB,
            RECORD | {"job_type": "coding"},
            RECORD | {"status": "authorized"},
            RECORD | {"receipt_id": ID},
            RECORD | {"failure_category": "secret"},
            RECORD | {"created_at": float("inf")},
        ):
            with (
                self.subTest(result=result),
                patch.object(self.client.opener, "open", return_value=Response(result)),
                self.assertRaises(ClientError),
            ):
                self.client.enqueue(RECEIPT_ID)

    def test_legacy_and_invalid_ids_never_reach_lifecycle_endpoints(self):
        legacy = Client("https://api.example.test", "x" * 43)
        with (
            patch.object(legacy.opener, "open") as send,
            self.assertRaises(ClientError),
        ):
            legacy.job(ID)
        send.assert_not_called()
        with (
            patch.object(self.client.opener, "open") as send,
            self.assertRaises(ClientError),
        ):
            self.client.cancel("../secret")
        send.assert_not_called()
