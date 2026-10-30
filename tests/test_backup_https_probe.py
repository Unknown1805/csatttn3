"""Regression: the REST repository config is encrypted bytes, not plaintext JSON."""
import json
from pathlib import Path
import ssl
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import probe_backup_https as probe


class BinaryRepositoryConfig(unittest.TestCase):
    def run_probe(self, body, status=200, protocol="TLSv1.3"):
        model = {"secrets": {"rest_http_password": {"file": "/unused/password"}}}
        actual = {
            "HostConfig": {"PortBindings": {}},
            "NetworkSettings": {"Networks": {"csatttn3_backup_net": {
                "NetworkID": "test-network", "IPAddress": "192.0.2.10",
            }}},
        }
        tls12 = ssl.SSLError("TLS 1.2 rejected")
        tls12.reason = "TLSV1_ALERT_PROTOCOL_VERSION"
        plain = Mock()
        plain.getresponse.return_value.status = 400
        plain.getresponse.return_value.read.return_value = b"Client sent an HTTP request to an HTTPS server."
        with (
            patch.object(probe.lab, "preflight"),
            patch.object(probe.lab, "check_running_server"),
            patch.object(probe.lab, "tls_paths", return_value={"backup_ca": Path("unused-ca")}),
            patch.object(probe.subprocess, "check_output", side_effect=[
                "test-container", json.dumps([actual]), json.dumps([{"Internal": True}]),
            ]),
            patch.object(probe.ssl, "create_default_context", side_effect=[Mock(), Mock()]),
            patch.object(probe.Path, "read_text", return_value="unused-test-password"),
            patch.object(probe, "request", side_effect=[
                (status, protocol, body), (401, "TLSv1.3", b""), (401, "TLSv1.3", b""), tls12,
            ]) as requests,
            patch.object(probe, "certificate_rejected", side_effect=[
                "unknown CA", "hostname mismatch",
            ]) as rejected,
            patch.object(probe.http.client, "HTTPConnection", return_value=plain),
        ):
            result = probe.probe(model, ["unused-compose"], {})
            self.assertEqual(requests.call_count, 4)
            self.assertEqual(rejected.call_count, 2)
            self.assertEqual(result["no_auth"], 401)
            self.assertEqual(result["wrong_password"], 401)
            self.assertEqual(result["plain_http_rejected"], 400)
            return result

    def test_non_utf8_config_does_not_abort_remaining_security_checks(self):
        body = b"\xd9\xff\x00" + bytes(range(256))
        result = self.run_probe(body)
        self.assertEqual(result["valid_ca_and_name"]["config_bytes"], len(body))
        self.assertEqual(result["valid_ca_and_name"]["protocol"], "TLSv1.3")

    def test_empty_config_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "empty"):
            self.run_probe(b"")

    def test_wrong_status_is_still_rejected(self):
        with self.assertRaises(RuntimeError):
            self.run_probe(b"anything", status=401)

    def test_wrong_tls_version_is_still_rejected(self):
        with self.assertRaises(RuntimeError):
            self.run_probe(b"anything", protocol="TLSv1.2")


if __name__ == "__main__":
    unittest.main()
