"""Offline tests: use disposable keys, never the lab's real secrets or repository."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import backup_lab as lab
from create_backup_tls import create
from verify_backup_https import check_new_target


class BackupTLS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="csattt-tls-test-")
        cls.directory = Path(cls.temporary.name)
        cls.runtime = cls.directory / "tls"
        cls.authority = cls.directory / "ca"
        create(cls.runtime, cls.authority)
        cls.model = json.loads(subprocess.check_output([
            "docker", "compose", "--env-file", str(ROOT / "lab/.env.backup.example"),
            "-f", str(ROOT / "lab/compose.yaml"),
            "-f", str(ROOT / "lab/compose.backup.yaml"), "config", "--format", "json",
        ], text=True, cwd=ROOT))
        for name, filename in (("backup_ca", "ca.crt"), ("backup_server_cert", "server.crt"),
                               ("backup_server_key", "server.key")):
            cls.model["secrets"][name]["file"] = str(cls.runtime / filename)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_valid_certificate_and_matching_key(self):
        # The real VM contract is UID 1000; tests may run under another developer UID.
        original = lab.check_secret
        with patch.object(lab, "check_secret", side_effect=lambda path: original(path, uid=os.getuid())):
            lab.check_tls(self.model)

    def test_files_are_private(self):
        self.assertEqual(self.runtime.stat().st_mode & 0o777, 0o700)
        for filename in ("ca.crt", "server.crt", "server.key"):
            self.assertEqual((self.runtime / filename).stat().st_mode & 0o777, 0o600)

    def test_ca_private_key_not_in_runtime(self):
        self.assertTrue((self.authority / "ca.key").is_file())
        self.assertFalse((self.runtime / "ca.key").exists())
        self.assertEqual(set(self.runtime.iterdir()), {
            self.runtime / "ca.crt", self.runtime / "server.crt", self.runtime / "server.key",
        })

    def test_existing_directory_is_never_overwritten(self):
        before = (self.runtime / "server.key").read_bytes()
        with self.assertRaises(RuntimeError):
            create(self.runtime, self.directory / "another-ca")
        self.assertEqual(before, (self.runtime / "server.key").read_bytes())
        self.assertFalse((self.directory / "another-ca").exists())

    def test_wrong_hostname_rejected(self):
        completed = subprocess.run([
            "openssl", "verify", "-CAfile", str(self.runtime / "ca.crt"),
            "-purpose", "sslserver", "-verify_hostname", "incorrect.invalid",
            str(self.runtime / "server.crt"),
        ], capture_output=True)
        self.assertNotEqual(completed.returncode, 0)

    def test_wrong_trust_root_rejected(self):
        completed = subprocess.run([
            "openssl", "verify", "-CAfile", str(self.runtime / "server.crt"),
            "-purpose", "sslserver", str(self.runtime / "server.crt"),
        ], capture_output=True)
        self.assertNotEqual(completed.returncode, 0)

    def test_private_key_mismatch_rejected(self):
        model = copy.deepcopy(self.model)
        # An unrelated private key in the same runtime directory.
        wrong = self.runtime / "wrong.key"
        wrong.write_bytes((self.authority / "ca.key").read_bytes())
        wrong.chmod(0o600)
        model["secrets"]["backup_server_key"]["file"] = str(wrong)
        original = lab.check_secret
        try:
            with patch.object(lab, "check_secret", side_effect=lambda path: original(path, uid=os.getuid())):
                with self.assertRaisesRegex(RuntimeError, "do not match"):
                    lab.check_tls(model)
        finally:
            wrong.unlink()

    def test_http_worker_configuration_rejected(self):
        model = copy.deepcopy(self.model)
        model["services"]["backup-worker"]["environment"]["RESTIC_REPOSITORY"] = "rest:http://backup-server:8000/csattt/"
        original = lab.check_secret
        with patch.object(lab, "check_secret", side_effect=lambda path: original(path, uid=os.getuid())):
            with self.assertRaisesRegex(RuntimeError, "HTTPS repository"):
                lab.check_tls(model)

    def test_client_cannot_override_transport(self):
        for value in ("--insecure-tls", "--insecure-tls=true", "--cacert=/tmp/ca",
                      "--repo=rest:http://example", "-rrest:http://example", "--no-lock"):
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError):
                    lab.check_client_arguments(["snapshots", value])

    def test_normal_backup_arguments_allowed(self):
        lab.check_client_arguments(["backup", "/source", "--tag", "https-gate"])
        lab.check_client_arguments(["snapshots", "--json"])
        lab.check_client_arguments(["check", "--read-data"])

    def test_gate_cannot_create_restore_target_in_repository(self):
        with self.assertRaisesRegex(RuntimeError, "overlaps"):
            check_new_target(self.runtime / "restore-new", self.authority, self.runtime)
        self.assertFalse((self.runtime / "restore-new").exists())

    def test_gate_refuses_existing_restore_target(self):
        with self.assertRaisesRegex(RuntimeError, "existing target"):
            check_new_target(self.runtime, self.authority, self.directory / "repository")


if __name__ == "__main__":
    unittest.main()
