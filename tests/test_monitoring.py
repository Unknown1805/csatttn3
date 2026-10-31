"""Offline checks: monitor exposure, certificate identities and private setup."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import create_monitoring_runtime as runtime


class Monitoring(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = json.loads(subprocess.check_output([
            "docker", "compose", "--env-file", str(ROOT / "lab/.env.monitoring.example"),
            "-f", str(ROOT / "lab/compose.yaml"),
            "-f", str(ROOT / "lab/compose.monitoring.yaml"),
            "config", "--format", "json",
        ], text=True))

    def test_networks_and_exposure(self):
        services = self.model["services"]
        self.assertEqual(set(services), {"workstation", "wazuh.manager", "wazuh.indexer", "wazuh.dashboard"})
        self.assertEqual(set(services["workstation"]["networks"]), {"incident_net"})
        self.assertTrue(self.model["networks"]["monitoring_net"]["internal"])
        for name in ("wazuh.manager", "wazuh.indexer", "wazuh.dashboard"):
            service = services[name]
            self.assertEqual(set(service["networks"]), {"monitoring_net"})
            self.assertFalse(service.get("privileged", False))
            self.assertNotEqual(service.get("pid"), "host")
            self.assertIn("@sha256:", service["image"])
        self.assertFalse(services["wazuh.manager"].get("ports"))
        self.assertFalse(services["wazuh.indexer"].get("ports"))
        ports = services["wazuh.dashboard"]["ports"]
        self.assertEqual(len(ports), 1)
        self.assertEqual((ports[0]["host_ip"], str(ports[0]["published"]), ports[0]["target"]), ("127.0.0.1", "8443", 5601))

    def test_bind_mounts_are_readonly_and_no_ca_key_or_backup(self):
        for name, service in self.model["services"].items():
            if name == "workstation":
                continue
            for volume in service.get("volumes", []):
                if volume["type"] == "bind":
                    self.assertTrue(volume["read_only"])
                    self.assertFalse(volume["bind"].get("create_host_path", False))
                    self.assertNotIn("docker.sock", volume["source"])
                    self.assertNotIn("/ca/", volume["source"])
                    self.assertNotIn("backup", volume["source"])
        binds = {v["target"] for v in self.model["services"]["wazuh.manager"]["volumes"] if v["type"] == "bind"}
        self.assertTrue({"/lab/data", "/lab/fim-probe"}.issubset(binds))

    def test_fim_scope_and_no_automatic_response(self):
        model = ET.parse(ROOT / "lab/wazuh/wazuh-manager.conf").getroot()
        self.assertEqual({d.text for d in model.findall("syscheck/directories")}, {"/lab/data", "/lab/fim-probe"})
        self.assertTrue(all(d.attrib["realtime"] == "yes" for d in model.findall("syscheck/directories")))
        self.assertEqual(model.findtext("active-response/disabled"), "yes")
        self.assertEqual(model.findtext("vulnerability-detection/enabled"), "no")

    def test_private_setup_certificates_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "data"
            data.mkdir()
            for n in range(1, 16):
                (data / f"file_{n:02d}.txt").write_text(f"CSATTT N3 - SYNTHETIC DATA ONLY\nfile={n:02d}\n")
            directory, probe = root / "private", root / "probe"
            fake_hash = "$2y$12$" + "A" * 53
            with patch.object(runtime, "bcrypt_hash", return_value=fake_hash):
                runtime.prepare(directory, data, probe)
            for path in directory.rglob("*"):
                self.assertEqual(path.stat().st_mode & 0o777, 0o700 if path.is_dir() else 0o600)
            self.assertFalse((directory / "tls/ca.key").exists())
            runtime.openssl("verify", "-CAfile", directory / "tls/root-ca.pem",
                            "-verify_ip", "127.0.0.1", directory / "tls/wazuh.dashboard.pem")
            with self.assertRaises(subprocess.CalledProcessError):
                runtime.openssl("verify", "-CAfile", directory / "tls/root-ca.pem",
                                "-verify_hostname", "wrong.invalid", directory / "tls/wazuh.indexer.pem")
            original = (directory / "monitoring.env").read_bytes()
            with self.assertRaises(RuntimeError):
                runtime.prepare(directory, data, probe)
            self.assertEqual((directory / "monitoring.env").read_bytes(), original)
            self.assertEqual(len(list(data.iterdir())), 15)

    def test_reject_overlapping_or_symlink_destination(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaises(RuntimeError):
                runtime.prepare(root / "data/private", root / "data", root / "probe")
            (root / "link").symlink_to(root / "real")
            with self.assertRaises(RuntimeError):
                runtime.prepare(root / "link/private", root / "data", root / "probe")

    def test_bcrypt_record_is_validated_and_password_uses_stdin(self):
        record = "$2y$12$" + "A" * 53
        result = subprocess.CompletedProcess([], 0, stdout="csattt:" + record + "\n")
        with patch.object(runtime.subprocess, "run", return_value=result) as command:
            self.assertEqual(runtime.bcrypt_hash("test-password"), record)
            arguments = command.call_args
            self.assertEqual(arguments.kwargs["input"], "test-password\n")
            self.assertNotIn("test-password", arguments.args[0])
            self.assertIn("none", arguments.args[0])
        with patch.object(runtime.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout="bad record")):
            with self.assertRaises(RuntimeError):
                runtime.bcrypt_hash("test-password")


if __name__ == "__main__":
    unittest.main()
