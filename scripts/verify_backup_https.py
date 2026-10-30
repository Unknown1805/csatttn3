"""Run the HTTPS gate against the existing lab repository without reinitializing it."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

import backup_lab as lab
from probe_backup_https import probe

BASELINE = "4e9113aa6cb9e395797abe8c2f1c410c4437d928ff4bbf5a5122b2496ac6d5d1"


def check_new_target(target, source, repository):
    if target.exists() or target.is_symlink():
        raise RuntimeError("Choose a new LAB_RESTORE_DIR; verification refuses an existing target.")
    if not target.parent.is_dir() or target.parent.is_symlink():
        raise RuntimeError("Restore target parent must be an existing nonsymlink directory.")
    real_target = target.resolve()
    for protected in (source, repository):
        real_protected = protected.resolve()
        if real_target.is_relative_to(real_protected) or real_protected.is_relative_to(real_target):
            raise RuntimeError("Restore target overlaps protected data.")


def files(directory):
    items = list(directory.iterdir())
    expected = [f"file_{number:02d}.txt" for number in range(1, 16)]
    if sorted(item.name for item in items) != expected:
        raise RuntimeError(f"Expected exactly 15 synthetic files at {directory}")
    hashes = {}
    for number, name in enumerate(expected, 1):
        path = directory / name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError("Synthetic files must be regular files, without symlinks.")
        data = path.read_bytes()
        original = f"CSATTT N3 - SYNTHETIC DATA ONLY\nfile={number:02d}\n".encode()
        if data != original:
            raise RuntimeError(f"Synthetic source content differs: {name}")
        hashes[name] = hashlib.sha256(data).hexdigest()
    return hashes


def restic_negative_test(compose, environment, directory, name, options, arguments, expected_error):
    container = "csattt-tls-probe-" + uuid.uuid4().hex
    log = directory / (name + ".log")
    command = compose + [
        "run", "--rm", "--no-deps", "-T", "--name", container,
        "--entrypoint", "/bin/sh",
    ] + options + [
        "backup-worker", "-c",
        'exec timeout -s TERM -k 2 8 /usr/bin/restic "$@"',
        "tls-probe",
    ] + arguments
    print(f"Certificate rejection test: {name} (bounded diagnostic)", flush=True)
    completed = None
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, env=environment,
            stdin=subprocess.DEVNULL, timeout=30,
        )
    except subprocess.TimeoutExpired as error:
        def decoded(value):
            return value.decode(errors="replace") if isinstance(value, bytes) else (value or "")
        log.write_text(decoded(error.stdout) + decoded(error.stderr) + "\nOUTER TIMEOUT: test failed.\n")
        raise RuntimeError(f"Diagnostic timed out: {name}; inspect {log}.") from error
    finally:
        # Compose --rm removes an exited container, but cannot stop a still-running one.
        if completed is None:
            try:
                cleanup = subprocess.run(
                    lab.DOCKER + ["stop", "--time", "2", container],
                    capture_output=True, text=True, env=environment,
                    stdin=subprocess.DEVNULL, timeout=10,
                )
                with log.open("a") as stream:
                    stream.write("\nScoped cleanup:\n" + cleanup.stdout + cleanup.stderr)
            except (OSError, subprocess.SubprocessError) as error:
                with log.open("a") as stream:
                    stream.write(f"\nCleanup needs manual check: {container}: {error}\n")
    combined = completed.stdout + completed.stderr
    log.write_text(combined + f"\nDiagnostic exit code: {completed.returncode}\n")
    if completed.returncode == 0 or "x509" not in combined or expected_error not in combined:
        raise RuntimeError(f"Restic negative test failed: {name}; inspect {log}.")
    print(f"Certificate rejection confirmed: {name}", flush=True)
    return "rejected by certificate verification"


def verify(environment_file):
    lab.ensure_vm()
    environment = lab.clean_environment()
    compose = lab.compose_command(environment_file)
    model = json.loads(subprocess.check_output(
        compose + ["config", "--format", "json"], env=environment, text=True,
    ))
    lab.preflight(model)
    lab.check_running_server(compose, model, environment)
    source = lab.bind_source(model["services"]["backup-worker"], "/source")
    target = lab.bind_source(model["services"]["restore-worker"], "/restore")
    # The helper must validate the target. Do not create directories over existing data.
    check_new_target(target, source, lab.bind_source(model["services"]["backup-server"], "/data"))
    hashes = files(source)
    target.mkdir(mode=0o750)
    result_directory = Path(tempfile.mkdtemp(
        prefix="https-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-"),
        dir=Path(environment_file).resolve().parent,
    ))
    print(f"Evidence directory: {result_directory}", flush=True)
    (result_directory / "source.sha256").write_text("".join(
        f"{digest}  {name}\n" for name, digest in sorted(hashes.items())
    ))
    (result_directory / "transport.json").write_text(
        json.dumps(probe(model, compose, environment), indent=2) + "\n"
    )
    identifier = subprocess.check_output(
        compose + ["ps", "-q", "backup-server"], env=environment, text=True,
    ).strip()
    actual = json.loads(subprocess.check_output(
        lab.DOCKER + ["inspect", identifier], env=environment, text=True,
    ))[0]
    address = actual["NetworkSettings"]["Networks"]["csatttn3_backup_net"]["IPAddress"]
    negative_tests = (
        ("restic-untrusted-ca", ["-e", "RESTIC_CACERT="], ["snapshots"], "unknown authority"),
        ("restic-wrong-name", [], ["-r", f"rest:https://{address}:8000/csattt/", "snapshots"], "IP SANs"),
    )
    negative_results = {}
    for name, options, arguments, expected_error in negative_tests:
        # Only these diagnostic runs bypass the wrapper; no credentials are sent before TLS verifies.
        negative_results[name] = restic_negative_test(
            compose, environment, result_directory, name, options, arguments, expected_error,
        )
    (result_directory / "restic-negative-tests.json").write_text(
        json.dumps(negative_results, indent=2) + "\n"
    )
    command = [sys.executable, str(lab.ROOT / "scripts/backup_lab.py"),
               "--env-file", str(Path(environment_file).resolve())]

    def run(arguments, filename, parse_json=False):
        completed = subprocess.run(command + arguments, capture_output=True, text=True)
        (result_directory / filename).write_text(completed.stdout)
        (result_directory / (filename + ".stderr")).write_text(completed.stderr)
        if completed.stdout:
            print(completed.stdout, end="", flush=True)
        if completed.stderr:
            print(completed.stderr, end="", file=sys.stderr, flush=True)
        completed.check_returncode()
        return json.loads(completed.stdout) if parse_json else completed.stdout

    before = run(["client", "snapshots", "--json"], "snapshots-before.json", True)
    if BASELINE not in {item["id"] for item in before}:
        raise RuntimeError("The original known-good snapshot is missing. Do not initialize another repository.")
    tag = result_directory.name
    run(["client", "backup", "/source", "--tag", tag], "backup.log")
    snapshots = run(["client", "snapshots", "--json", "--tag", tag], "snapshot.json", True)
    if len(snapshots) != 1:
        raise RuntimeError("Expected exactly one snapshot with this unique HTTPS test tag.")
    new_id = snapshots[0]["id"]
    (result_directory / "snapshot-id.txt").write_text(new_id + "\n")
    run(["client", "check", "--read-data"], "check.log")
    # Restoring the old snapshot proves compatibility across the HTTP-to-HTTPS migration.
    started = datetime.now(timezone.utc)
    timer = time.monotonic()
    run(["restore", BASELINE], "restore-original-snapshot.log")
    elapsed = time.monotonic() - timer
    finished = datetime.now(timezone.utc)
    if sorted(item.name for item in target.iterdir()) != ["source"]:
        raise RuntimeError("Unexpected restore layout; expected only a source directory.")
    if files(target / "source") != hashes or files(source) != hashes:
        raise RuntimeError("Hash verification failed after restore.")
    result = {
        "https_backup_snapshot_id": new_id,
        "restored_original_snapshot_id": BASELINE,
        "restore_started_utc": started.isoformat(),
        "restore_finished_utc": finished.isoformat(),
        "restore_step_seconds": round(elapsed, 3),
        "restored_files": 15, "restored_bytes": 600,
        "restored_hashes_verified": 15, "source_hashes_verified": 15,
        "note": "HTTPS functional gate; not incident RTO/RPO or clean-VM recovery.",
    }
    (result_directory / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(f"HTTPS GATE: OK. Evidence: {result_directory}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    args = parser.parse_args()
    try:
        verify(args.env_file)
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
