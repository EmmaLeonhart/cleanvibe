"""Tests for ``cleanvibe replicate --batch`` (network-free)."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from cleanvibe import cli
from cleanvibe.replicate import load_batch

CORPUS = Path(__file__).resolve().parent.parent / "docs" / "replication-examples" / "papers.json"


class TestLoadBatch(unittest.TestCase):
    def _file(self, tmp, name, text):
        path = Path(tmp) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_corpus_file_loads(self):
        entries = load_batch(CORPUS)
        papers = json.loads(CORPUS.read_text(encoding="utf-8"))["papers"]
        self.assertEqual([r for r, _ in entries], [p["arxiv_id"] for p in papers])
        self.assertTrue(all(p is None for _, p in entries))

    def test_json_list_of_strings_and_objects(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self._file(tmp, "b.json", json.dumps([
                "2605.20919",
                {"url": "https://example.org/paper", "path": "elsewhere"},
                {"ref": "clawrxiv:2605.02609", "arxiv_id": "ignored"},
            ]))
            self.assertEqual(load_batch(f), [
                ("2605.20919", None),
                ("https://example.org/paper", Path("elsewhere")),
                ("clawrxiv:2605.02609", None),
            ])

    def test_text_file_with_comments(self):
        with tempfile.TemporaryDirectory() as tmp:
            f = self._file(tmp, "b.txt",
                           "# my papers\n2605.20919   # Sutra\n\n"
                           "https://example.org/p#section-2\n  my-folder\n")
            self.assertEqual([r for r, _ in load_batch(f)], [
                "2605.20919", "https://example.org/p#section-2", "my-folder",
            ])

    def test_bad_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name, text in (("empty.txt", "# nothing\n"),
                               ("broken.json", "{\"papers\": [\n"),
                               ("noref.json", "[{\"title\": \"x\"}]"),
                               ("shape.json", "{\"other\": 1}")):
                with self.subTest(name=name):
                    with self.assertRaises(ValueError):
                        load_batch(self._file(tmp, name, text))


class TestBatchCli(unittest.TestCase):
    def setUp(self):
        self._delay = cli.BATCH_DELAY_SECONDS
        cli.BATCH_DELAY_SECONDS = 0
        self._one = cli._replicate_one

    def tearDown(self):
        cli.BATCH_DELAY_SECONDS = self._delay
        cli._replicate_one = self._one

    def _run(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            with self.assertRaises(SystemExit) as cm:
                cli.main(["replicate", *argv])
        return cm.exception.code, out.getvalue(), err.getvalue()

    def test_manual_entries_scaffold_into_dir_without_claude(self):
        with tempfile.TemporaryDirectory() as tmp:
            batch = Path(tmp) / "b.txt"
            batch.write_text("paper-one\npaper-two\n", encoding="utf-8")
            into = Path(tmp) / "reps"
            cwd = os.getcwd()
            code, out, _ = self._run("--batch", str(batch), "--into", str(into))
            self.assertEqual(os.getcwd(), cwd)
            self.assertEqual(code, 0, out)
            for name in ("paper-one", "paper-two"):
                self.assertTrue((into / name / "queue.md").is_file())
                self.assertTrue((into / name / "replication_target").is_dir())
            self.assertIn("Batch: 2 of 2 scaffolded", out)
            self.assertIn("Claude was not launched", out)

    def test_routes_every_entry_and_never_launches_claude(self):
        calls = []
        cli._replicate_one = lambda ref, path, dry, no_claude: calls.append(
            (ref, path, os.path.realpath(os.getcwd()), no_claude))
        with tempfile.TemporaryDirectory() as tmp:
            batch = Path(tmp) / "b.json"
            batch.write_text(json.dumps({"papers": [
                {"arxiv_id": "2605.20919"}, {"ref": "x", "path": "p"}]}),
                encoding="utf-8")
            into = Path(tmp) / "out"
            code, _, _ = self._run("--batch", str(batch), "--into", str(into))
            self.assertEqual(code, 0)
            here = os.path.realpath(into)
            self.assertEqual(calls, [("2605.20919", None, here, True),
                                     ("x", Path("p"), here, True)])

    def test_one_failure_does_not_stop_the_rest(self):
        seen = []

        def fake(ref, path, dry, no_claude):
            seen.append(ref)
            if ref == "bad":
                raise ValueError("no such paper")

        cli._replicate_one = fake
        with tempfile.TemporaryDirectory() as tmp:
            batch = Path(tmp) / "b.txt"
            batch.write_text("good-1\nbad\ngood-2\n", encoding="utf-8")
            code, out, err = self._run("--batch", str(batch), "--into", tmp)
            self.assertEqual(code, 1)
            self.assertEqual(seen, ["good-1", "bad", "good-2"])
            self.assertIn("Batch: 2 of 3", out)
            self.assertIn("failed: bad (no such paper)", out)
            self.assertIn("FAILED: no such paper", err)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            batch = Path(tmp) / "b.txt"
            batch.write_text("paper-one\n", encoding="utf-8")
            into = Path(tmp) / "never"
            code, out, _ = self._run("--batch", str(batch), "--into", str(into),
                                     "--dry-run")
            self.assertEqual(code, 0)
            self.assertFalse(into.exists())
            self.assertFalse((Path(tmp) / "paper-one").exists())
            self.assertIn("[dry-run] Would create", out)

    def test_argument_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            batch = Path(tmp) / "b.txt"
            batch.write_text("x\n", encoding="utf-8")
            self.assertEqual(self._run()[0], 2)
            self.assertEqual(self._run("x", "--batch", str(batch))[0], 2)
            self.assertEqual(self._run("--batch", str(Path(tmp) / "missing"))[0], 2)


if __name__ == "__main__":
    unittest.main()
