"""Keep intentional certificate failures bounded and distinct from infrastructure failure."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import verify_backup_https as gate


class BoundedCertificateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.addCleanup(self.temporary.cleanup)

    def invoke(self, expected="unknown authority"):
        return gate.restic_negative_test(
            ["compose"], {}, self.directory, "test-ca",
            ["-e", "RESTIC_CACERT="], ["snapshots"], expected,
        )

    def test_retry_output_is_accepted_after_bounded_process_exits(self):
        result = subprocess.CompletedProcess([], 143, "", "x509: certificate signed by unknown authority\nretrying\n")
        with patch.object(gate.subprocess, "run", return_value=result) as run:
            self.assertEqual(self.invoke(), "rejected by certificate verification")
        arguments = run.call_args.args[0]
        self.assertIn('exec timeout -s TERM -k 2 8 /usr/bin/restic "$@"', arguments)
        self.assertEqual(run.call_args.kwargs["timeout"], 30)
        self.assertEqual(run.call_args.kwargs["stdin"], subprocess.DEVNULL)
        self.assertIn("unknown authority", (self.directory / "test-ca.log").read_text())
        self.assertEqual(run.call_count, 1)

    def test_hostname_rejection_passes(self):
        result = subprocess.CompletedProcess([], 143, "", "x509: cannot validate certificate because it has no IP SANs")
        with patch.object(gate.subprocess, "run", return_value=result):
            self.invoke("IP SANs")

    def test_infrastructure_error_cannot_pass(self):
        for text in ("network is unreachable", "timeout: not found", "unknown authority without certificate marker"):
            with self.subTest(text=text), patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess([], 1, "", text)):
                with self.assertRaises(RuntimeError):
                    self.invoke()

    def test_success_exit_cannot_pass_even_with_certificate_text(self):
        with patch.object(gate.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "x509: unknown authority", "")):
            with self.assertRaises(RuntimeError):
                self.invoke()

    def test_outer_timeout_preserves_bytes_and_stops_only_its_container(self):
        error = subprocess.TimeoutExpired([], 30, output=b"partial\xff", stderr=b"x509: unknown authority")
        with patch.object(gate.subprocess, "run", side_effect=[
            error, subprocess.CompletedProcess([], 0, "stopped", ""),
        ]) as run:
            with self.assertRaisesRegex(RuntimeError, "timed out"):
                self.invoke()
        first = run.call_args_list[0].args[0]
        container = first[first.index("--name") + 1]
        self.assertEqual(run.call_args_list[1].args[0], gate.lab.DOCKER + ["stop", "--time", "2", container])
        log = (self.directory / "test-ca.log").read_text()
        self.assertIn("partial", log)
        self.assertIn("OUTER TIMEOUT: test failed", log)

    def test_keyboard_interrupt_also_stops_diagnostic(self):
        with patch.object(gate.subprocess, "run", side_effect=[
            KeyboardInterrupt(), subprocess.CompletedProcess([], 0, "stopped", ""),
        ]) as run:
            with self.assertRaises(KeyboardInterrupt):
                self.invoke()
        self.assertEqual(run.call_count, 2)

    def test_cleanup_failure_is_logged_and_does_not_pass(self):
        with patch.object(gate.subprocess, "run", side_effect=[
            subprocess.TimeoutExpired([], 30), subprocess.TimeoutExpired([], 10),
        ]):
            with self.assertRaises(RuntimeError):
                self.invoke()
        self.assertIn("Cleanup needs manual check", (self.directory / "test-ca.log").read_text())


if __name__ == "__main__":
    unittest.main()
