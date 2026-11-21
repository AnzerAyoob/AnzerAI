import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from test_client import JOB, Response

from anzerai_client.api import Client, ClientError
from anzerai_client.github import AUDIENCE, get_workflow_token

TOKEN = "header.payload.signature"
ENV = {
    "ACTIONS_ID_TOKEN_REQUEST_URL": "https://vstoken.actions.githubusercontent.com/oidc?version=2",
    "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "fixture-runner-credential",
}


class WorkflowClientTests(unittest.TestCase):
    def test_runner_token_request_has_fixed_audience_and_uses_bearer(self):
        with patch("anzerai_client.github.build_opener") as opener:
            send = opener.return_value.open
            send.return_value = Response({"value": TOKEN})
            self.assertEqual(get_workflow_token(ENV), TOKEN)
        request = send.call_args.args[0]
        self.assertEqual(
            parse_qs(urlsplit(request.full_url).query),
            {"version": ["2"], "audience": [AUDIENCE]},
        )
        self.assertEqual(
            request.get_header("Authorization"), "Bearer fixture-runner-credential"
        )

    def test_runner_credentials_are_never_sent_to_untrusted_origin(self):
        for url in (
            "",
            "https://attacker.example.test",
            "http://vstoken.actions.githubusercontent.com/oidc",
            "https://vstoken.actions.githubusercontent.com.attacker.example.test/oidc",
            "https://user@vstoken.actions.githubusercontent.com/oidc",
            "https://vstoken.actions.githubusercontent.com:444/oidc",
            "https://vstoken.actions.githubusercontent.com/oidc?%61udience=wrong",
        ):
            env = ENV | {"ACTIONS_ID_TOKEN_REQUEST_URL": url}
            with (
                self.subTest(url=url),
                patch("anzerai_client.github.build_opener") as opener,
                self.assertRaises(ClientError),
            ):
                get_workflow_token(env)
            opener.assert_not_called()

    def test_rejects_malformed_runner_response_without_echoing_credentials(self):
        with (
            patch("anzerai_client.github.build_opener") as opener,
            self.assertRaises(ClientError) as failure,
        ):
            opener.return_value.open.return_value = Response(
                {"value": ENV["ACTIONS_ID_TOKEN_REQUEST_TOKEN"]}
            )
            get_workflow_token(ENV)
        self.assertNotIn(ENV["ACTIONS_ID_TOKEN_REQUEST_TOKEN"], str(failure.exception))

    def test_v2_uses_oidc_and_requires_authorized_receipt(self):
        client = Client("https://api.example.test", TOKEN, github=True)
        authorized = JOB | {"status": "authorized"}
        with patch.object(
            client.opener, "open", return_value=Response(authorized, 201)
        ) as send:
            self.assertEqual(client.submit("Example/Project", "issue", 7), authorized)
        request = send.call_args.args[0]
        self.assertEqual(request.full_url, "https://api.example.test/v2/jobs")
        self.assertEqual(request.get_header("Authorization"), f"Bearer {TOKEN}")
        self.assertIsNone(request.get_header("Idempotency-key"))
        self.assertEqual(
            json.loads(request.data),
            {"repository": "example/project", "kind": "issue", "number": 7},
        )

        with patch.object(
            client.opener, "open", return_value=Response(authorized)
        ) as send:
            self.assertEqual(client.status(JOB["id"]), authorized)
        self.assertEqual(
            send.call_args.args[0].full_url,
            "https://api.example.test/v2/jobs/" + JOB["id"],
        )

        with (
            patch.object(client.opener, "open", return_value=Response(JOB, 201)),
            self.assertRaisesRegex(ClientError, "invalid job record"),
        ):
            client.submit("example/project", "issue", 7)

    def test_no_legacy_credential_or_caller_idempotency_key_in_github_mode(self):
        with self.assertRaises(ClientError):
            Client("https://api.example.test", "x" * 43, github=True)
        client = Client("https://api.example.test", TOKEN, github=True)
        with self.assertRaises(ClientError):
            client.submit("example/project", "issue", 7, "client-key")
