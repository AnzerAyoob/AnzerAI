import io
import json
import unittest
from email.message import Message
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from anzerai_client.api import MAX_RESPONSE_BYTES, Client, ClientError, NoRedirect

TOKEN = "a" * 43
JOB = {
    "id": "9f4a5e4b-3d8a-4fca-9d08-e31f1b20a8a1",
    "status": "received",
    "repository": "example/project",
    "kind": "issue",
    "number": 7,
}


class Response(io.BytesIO):
    def __init__(self, body, status=200, media_type="application/json"):
        super().__init__(
            body if isinstance(body, bytes) else json.dumps(body).encode("utf-8")
        )
        self.status = status
        self.headers = Message()
        self.headers["Content-Type"] = media_type


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client("https://api.example.test", TOKEN)

    def test_submits_reference_and_idempotency_key(self):
        with patch.object(
            self.client.opener, "open", return_value=Response(JOB, 201)
        ) as send:
            self.assertEqual(
                self.client.submit("EXAMPLE/Project", "issue", 7, "event-7"), JOB
            )
        request = send.call_args.args[0]
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.full_url, "https://api.example.test/v1/jobs")
        self.assertEqual(request.get_header("Authorization"), f"Bearer {TOKEN}")
        self.assertEqual(request.get_header("Idempotency-key"), "event-7")
        self.assertEqual(
            json.loads(request.data),
            {"repository": "example/project", "kind": "issue", "number": 7},
        )

    def test_fetches_the_requested_receipt(self):
        with patch.object(
            self.client.opener, "open", return_value=Response(JOB)
        ) as send:
            self.assertEqual(self.client.status(JOB["id"]), JOB)
        request = send.call_args.args[0]
        self.assertEqual(request.get_method(), "GET")
        self.assertTrue(request.full_url.endswith("/v1/jobs/" + JOB["id"]))
        self.assertIsNone(request.data)

    def test_rejects_unsafe_origins(self):
        for url in (
            "http://api.example.test",
            "http://localhost:8765",
            "https://user@api.example.test",
            "https://api.example.test/suffix",
            "https://api.example.test?",
            "https://api.example.test/#",
            "https://api.example.test:65536",
            "https://api.example.test\\another.test",
        ):
            with self.subTest(url=url), self.assertRaises(ClientError):
                Client(url, TOKEN, allow_loopback_http=True)
        with self.assertRaises(ClientError):
            Client("http://127.0.0.1:8765", TOKEN)
        local = Client("http://127.0.0.1:8765", TOKEN, allow_loopback_http=True)
        self.assertEqual(local.endpoint, "http://127.0.0.1:8765")

    def test_invalid_inputs_do_not_send_a_request(self):
        with patch.object(self.client.opener, "open") as send:
            for args in (
                ("bad", "issue", 7, "key"),
                ("example/..", "issue", 7, "key"),
                ("example/project", "discussion", 7, "key"),
                ("example/project", "issue", True, "key"),
                ("example/project", "issue", 7, "bad key"),
            ):
                with self.subTest(args=args), self.assertRaises(ClientError):
                    self.client.submit(*args)
            with self.assertRaises(ClientError):
                self.client.status("../unexpected")
            send.assert_not_called()

    def test_error_output_omits_secrets_and_remote_details(self):
        for error in (
            HTTPError(
                "https://api.example.test", 403, TOKEN, {}, io.BytesIO(TOKEN.encode())
            ),
            URLError(TOKEN),
        ):
            with (
                self.subTest(error=type(error)),
                patch.object(self.client.opener, "open", side_effect=error),
                self.assertRaises(ClientError) as failure,
            ):
                self.client.status(JOB["id"])
            self.assertNotIn(TOKEN, str(failure.exception))

    def test_rejects_invalid_or_unexpected_responses(self):
        for response in (
            Response(JOB, 202),
            Response(JOB, media_type="text/plain"),
            Response(b"{" * (MAX_RESPONSE_BYTES + 1)),
            Response(b"\xff"),
            Response(JOB | {"extra": TOKEN}),
            Response(JOB | {"number": False}),
            Response(JOB | {"repository": "example/.."}),
            Response(JOB | {"id": "00000000-0000-0000-0000-000000000000"}),
        ):
            with (
                patch.object(self.client.opener, "open", return_value=response),
                self.assertRaises(ClientError),
            ):
                self.client.status(JOB["id"])
        with (
            patch.object(
                self.client.opener, "open", return_value=Response(JOB | {"number": 8})
            ),
            self.assertRaisesRegex(ClientError, "different request"),
        ):
            self.client.submit("example/project", "issue", 7, "key")

    def test_does_not_follow_redirects(self):
        handler = next(
            item for item in self.client.opener.handlers if isinstance(item, NoRedirect)
        )
        self.assertIsNone(
            handler.redirect_request(
                None,
                None,
                302,
                "",
                {},
                "https://other.example.test",
            )
        )
