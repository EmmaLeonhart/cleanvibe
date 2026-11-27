"""The shipped refusal log (.claude/scripts/permission_denials.py, since 2.0.17)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cleanvibe import templates


def _line(t, content, role="assistant"):
    return json.dumps({"type": role, "timestamp": t,
                       "message": {"role": role, "content": content}})


class PermissionDenialsTest(unittest.TestCase):
    def _project(self, tmp):
        root = Path(tmp)
        (root / ".git").mkdir()
        scripts = root / ".claude" / "scripts"
        scripts.mkdir(parents=True)
        (scripts / "permission_denials.py").write_text(templates.PERMISSION_DENIALS_PY,
                                                        encoding="utf-8")
        (root / "sessions").mkdir()
        return root

    def _run(self, root, *args):
        return subprocess.run([sys.executable, str(root / ".claude" / "scripts" /
                                                   "permission_denials.py"), *args],
                              cwd=root, capture_output=True, text=True, check=True)

    def test_no_refusals_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            (root / "sessions" / "a.jsonl").write_text(
                _line("2026-11-26T10:00:00Z", [{"type": "text", "text": "hi"}]), encoding="utf-8")
            self._run(root)
            self.assertFalse((root / "PERMISSION-DENIALS.md").exists())

    def test_logs_both_kinds_and_retries(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._project(tmp)
            lines = [
                _line("2026-11-25T20:00:00Z", [{"type": "tool_use", "id": "a", "name": "Bash",
                      "input": {"command": "gh release create v2.0.16 --notes x"}}]),
                _line("2026-11-25T20:00:01Z", [{"type": "tool_result", "tool_use_id": "a",
                      "is_error": True, "content": "Permission for this action was denied by "
                      "the Claude Code auto mode classifier. Reason: [Destructive or Unwanted "
                      "Actions]. If"}], "user"),
                _line("2026-11-26T12:00:00Z", [{"type": "tool_use", "id": "b", "name": "Bash",
                      "input": {"command": "gh release create v2.0.16 --notes y"}}]),
                _line("2026-11-26T12:00:05Z", [{"type": "tool_result", "tool_use_id": "b",
                      "content": "ok"}], "user"),
                _line("2026-11-26T13:00:00Z", [{"type": "tool_use", "id": "c", "name": "Bash",
                      "input": {"command": "ls -d x*"}}]),
                _line("2026-11-26T13:00:01Z", [{"type": "tool_result", "tool_use_id": "c",
                      "is_error": True, "content": "The user doesn't want to proceed with this "
                      "tool use. The tool use was rejected"}], "user"),
            ]
            (root / "sessions" / "s.jsonl").write_text("\n".join(lines), encoding="utf-8")
            out = self._run(root, "--open").stdout
            self.assertIn("ls -d x*", out)
            self.assertNotIn("gh release", out)  # retried OK
            text = (root / "PERMISSION-DENIALS.md").read_text(encoding="utf-8")
            self.assertIn("NOT retried", text)
            self.assertIn("retried OK", text)
            self.assertIn("(Destructive or Unwanted Actions)", text)
            self.assertEqual(len(list((root / ".git").glob("cleanvibe-permission-denials-*.json"))), 1)
            self._run(root)  # second run reuses the same cache file
            self.assertEqual(len(list((root / ".git").glob("cleanvibe-permission-denials-*.json"))), 1)

    def test_rules_say_a_refusal_never_closes_a_queue_item(self):
        rules = templates.v2_rules_md()
        self.assertIn("PERMISSION-DENIALS.md", rules)
        self.assertIn("never closes", rules)


if __name__ == "__main__":
    unittest.main()
