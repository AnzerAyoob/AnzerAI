import json
import unittest
from unittest.mock import patch

from test_client import Response
from test_job_client import ID, RECEIPT_ID, RECORD

from anzerai_client.api import Client, ClientError

KEY = "fixture-provider-credential"
TOKEN = "header.payload.signature"
CHOICE = {
    "provider": "gemini",
    "model": "gemini-test",
    "max_output_tokens": 32,
    "timeout": 10,
}
JOB = RECORD | {"job_type": "inference_probe"}


class InferenceClientTests(unittest.TestCase):
    def setUp(self):
        self.client = Client("https://api.example.test", TOKEN, github=True)

    def test_key_is_only_sent_to_enqueue_in_a_header(self):
        with patch.object(
            self.client.opener, "open", return_value=Response(JOB, 201)
        ) as send:
            self.assertEqual(
                self.client.enqueue_inference(RECEIPT_ID, CHOICE, KEY), JOB
            )
        request = send.call_args.args[0]
        self.assertTrue(request.get_header("Anzerai-provider-key") == KEY)
        self.assertFalse(KEY in request.full_url or KEY.encode() in request.data)
        self.assertEqual(
            json.loads(request.data), {"receipt_id": RECEIPT_ID, "generation": CHOICE}
        )

    def test_paid_credentials_require_https_and_echoed_credentials_are_rejected(self):
        local = Client(
            "http://127.0.0.1:8765", TOKEN, github=True, allow_loopback_http=True
        )
        with patch.object(local.opener, "open") as send, self.assertRaises(ClientError):
            local.enqueue_inference(RECEIPT_ID, CHOICE, KEY)
        send.assert_not_called()
        with (
            patch.object(self.client.opener, "open") as send,
            self.assertRaises(ClientError),
        ):
            self.client.enqueue_inference(RECEIPT_ID, {"provider": "mock"}, KEY)
        send.assert_not_called()
        with patch.object(
            self.client.opener, "open", return_value=Response(JOB | {"leaked": KEY})
        ):
            with self.assertRaises(ClientError) as error:
                self.client.enqueue_inference(RECEIPT_ID, CHOICE, KEY)
        self.assertFalse(KEY in str(error.exception))

    def test_result_and_cancel_do_not_send_provider_credentials(self):
        final = JOB | {"status": "succeeded"}
        result = {
            "job": final,
            "provider": "gemini",
            "model": "gemini-test",
            "result": "ready",
            "requests": [],
        }
        with patch.object(
            self.client.opener, "open", return_value=Response(result)
        ) as send:
            self.assertEqual(self.client.inference(ID), result)
        self.assertIsNone(send.call_args.args[0].get_header("Anzerai-provider-key"))
        with patch.object(
            self.client.opener, "open", return_value=Response(final)
        ) as send:
            self.assertEqual(self.client.inference(ID, cancel=True), final)
        self.assertEqual(send.call_args.args[0].get_method(), "POST")
