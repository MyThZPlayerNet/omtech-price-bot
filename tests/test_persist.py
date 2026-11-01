"""Real Git integration: local bare remote, two clients, no network or credentials."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

PERSIST = Path(__file__).resolve().parents[1] / "scripts" / "persist.py"


@unittest.skipUnless(shutil.which("git"), "Git is required for persistence integration")
class PersistenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.remote = self.root / "remote.git"
        self.client = self.root / "client"
        self.other = self.root / "other"
        self.run_git(self.root, "init", "--bare", "--initial-branch=main", str(self.remote))
        remote_url = self.remote.as_posix()
        self.run_git(self.root, "clone", remote_url, self.client.as_posix())
        for key, value in (("user.name", "Test"), ("user.email", "test@example.invalid")):
            self.run_git(self.client, "config", key, value)
        (self.client / "README.md").write_text("initial")
        self.run_git(self.client, "add", "README.md")
        self.run_git(self.client, "commit", "-m", "initial")
        self.run_git(self.client, "push", "origin", "main")
        self.run_git(self.root, "clone", remote_url, self.other.as_posix())
        for key, value in (("user.name", "Test"), ("user.email", "test@example.invalid")):
            self.run_git(self.other, "config", key, value)

    def run_git(self, cwd, *args):
        result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def persist(self):
        return subprocess.run([sys.executable, str(PERSIST)], cwd=self.client,
                              capture_output=True, text=True, timeout=40)

    def write_data(self):
        (self.client / "data").mkdir(exist_ok=True)
        (self.client / "data" / "store.json").write_text('{"test": true}')
        (self.client / "data" / "price_history.csv").write_text('date,price\ntoday,699.99\n')

    def test_persist_to_remote_and_no_empty_commit(self):
        self.write_data()
        (self.client / "unrelated.txt").write_text("do not commit")
        result = self.persist()
        self.assertEqual(result.returncode, 0, result.stderr)
        sha = self.run_git(self.client, "rev-parse", "HEAD").stdout
        self.assertEqual(self.persist().returncode, 0)
        self.assertEqual(sha, self.run_git(self.client, "rev-parse", "HEAD").stdout)
        self.run_git(self.other, "pull", "--ff-only")
        self.assertEqual((self.other / "data" / "store.json").read_text(), '{"test": true}')
        self.assertFalse((self.other / "unrelated.txt").exists())

    def test_rebase_over_concurrent_readme_edit(self):
        (self.other / "README.md").write_text("user edit")
        self.run_git(self.other, "add", "README.md")
        self.run_git(self.other, "commit", "-m", "user edit")
        self.run_git(self.other, "push", "origin", "main")
        self.write_data()
        result = self.persist()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.client / "README.md").read_text(), "user edit")
        self.run_git(self.other, "pull", "--ff-only")
        self.assertTrue((self.other / "data" / "store.json").exists())
