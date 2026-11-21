import importlib.util
import os
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "anzerai.py"
SPEC = importlib.util.spec_from_file_location("anzerai", SCRIPT)
agent = importlib.util.module_from_spec(SPEC)
with patch.dict(os.environ, {
    "GITHUB_REPOSITORY": "example/project", "GITHUB_TOKEN": "test-token",
    "ANZERAI_API_KEY": "test-key", "ISSUE_NUMBER": "1",
    "TRIGGER_KIND": "issue", "TRIGGER_ACTOR": "tester",
    "TRIGGER_ASSOCIATION": "OWNER",
}, clear=False):
    SPEC.loader.exec_module(agent)


class SecurityTests(unittest.TestCase):
    def test_path_traversal_rejected(self):
        with self.assertRaises(agent.AgentError):
            agent.resolve_path("../outside.txt")

    def test_engine_checkout_not_editable(self):
        with self.assertRaises(agent.AgentError):
            agent.resolve_path(".anzerai-engine/secrets.txt")

    def test_destructive_shell_commands_rejected(self):
        for command in ("rm -rf tmp", "git reset --hard", "sudo apt install x"):
            with self.subTest(command=command), self.assertRaises(agent.AgentError):
                agent.run_shell(command)

    def test_network_shell_commands_rejected(self):
        for command in ("curl https://example.com", "wget example.com", "ssh host"):
            with self.subTest(command=command), self.assertRaises(agent.AgentError):
                agent.run_shell(command)

    def test_shell_command_length_limited(self):
        with self.assertRaises(agent.AgentError):
            agent.run_shell("echo " + ("x" * 1300))

    def test_unknown_tool_rejected(self):
        with self.assertRaises(agent.AgentError):
            agent.execute_tool("read_environment", {})

    def test_author_association_allowlist(self):
        self.assertEqual(agent.SAFE_ASSOCIATIONS, {"OWNER", "MEMBER", "COLLABORATOR"})


if __name__ == "__main__":
    unittest.main()
