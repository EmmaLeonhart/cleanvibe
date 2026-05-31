import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "migrate_repos_to_skills.py"

OLD_CLAUDE = """# demo

## Workflow Rules
- Plan into queue.md first.

## Emergency Stop Mode
stop stop stop blah blah three-cron LOCAL by default with CronCreate

## Writing
do not say honest

## Project Description
real project stuff that must survive
"""


def _init_repo(repo: Path, claude_text: str):
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=repo, check=True,
                   capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True,
                   capture_output=True)
    (repo / "CLAUDE.md").write_text(claude_text, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=repo, check=True,
                   capture_output=True)


class TestMigrate(unittest.TestCase):
    def test_dry_run_detects_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            repo = root / "demo"
            _init_repo(repo, OLD_CLAUDE)
            out = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--dry-run"],
                capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertIn("demo", out.stdout)
            # dry-run must not create skills or modify CLAUDE.md
            self.assertFalse((repo / ".claude" / "skills").exists())
            self.assertIn("Emergency Stop Mode",
                          (repo / "CLAUDE.md").read_text(encoding="utf-8"))

    def test_ignores_repo_without_markers(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            repo = root / "clean"
            _init_repo(repo, "# clean\n\n## Project Description\nno blocks here\n")
            out = subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(root), "--dry-run"],
                capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertNotIn("clean", out.stdout.replace("cleanvibe", ""))


if __name__ == "__main__":
    unittest.main()
