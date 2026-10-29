"""Operator commands for the Ubuntu VM backup rehearsal."""
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCKER = ["sudo", "docker", "--host", "unix:///var/run/docker.sock"]


def ensure_vm():
    release = Path("/etc/os-release").read_text()
    if 'ID=ubuntu\n' not in release and 'ID="ubuntu"\n' not in release:
        raise RuntimeError("Run this command inside the Ubuntu lab VM.")
    result = subprocess.run(
        ["systemd-detect-virt", "--vm"], capture_output=True, text=True, timeout=5
    )
    if result.returncode != 0 or os.getuid() != 1000 or os.getgid() != 1000:
        raise RuntimeError("Expected an Ubuntu VM session with UID/GID 1000.")


def clean_environment():
    environment = os.environ.copy()
    for key in ("DOCKER_HOST", "DOCKER_CONTEXT"):
        environment.pop(key, None)
    return environment


def mounted_fields(path, exact=False):
    option = "-M" if exact else "-T"
    result = subprocess.run(
        ["findmnt", "-rn", option, str(path), "-o", "UUID,FSTYPE,OPTIONS"],
        capture_output=True, text=True, check=True,
    )
    lines = result.stdout.strip().splitlines()
    if len(lines) != 1:
        raise RuntimeError("Expected one mounted filesystem.")
    return lines[0].split(None, 2)


def bind_source(service, target):
    matches = [item for item in service.get("volumes", []) if item["target"] == target]
    if len(matches) != 1 or matches[0]["type"] != "bind":
        raise RuntimeError(f"Expected one bind mount at {target}.")
    return Path(matches[0]["source"])


def check_backup_mount(mount, repository, expected_uuid, uid=1000):
    mount = Path(mount)
    repository = Path(repository)
    if mount.is_symlink() or repository.is_symlink():
        raise RuntimeError("Mountpoint and repository must not be symlinks.")
    actual_uuid, filesystem, options = mounted_fields(mount, exact=True)
    if actual_uuid != expected_uuid or filesystem != "ext4" or "rw" not in options.split(","):
        raise RuntimeError("Backup mount must match the configured UUID, ext4 and RW.")
    real_mount = mount.resolve(strict=True)
    real_repository = repository.resolve(strict=True)
    if not real_repository.is_dir() or real_repository == real_mount or not real_repository.is_relative_to(real_mount):
        raise RuntimeError("Repository must be a directory below the backup mount.")
    if mounted_fields(real_repository)[0] != expected_uuid:
        raise RuntimeError("Repository is on a different filesystem.")
    if real_repository.stat().st_uid != uid or not os.access(real_repository, os.W_OK | os.X_OK):
        raise RuntimeError("Repository must be writable by UID 1000.")


def check_secret(path, uid=1000):
    path = Path(path)
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_uid != uid:
        raise RuntimeError(f"Secret must be a regular file owned by UID 1000: {path.name}")
    if stat.S_IMODE(info.st_mode) != 0o600 or info.st_size == 0:
        raise RuntimeError(f"Secret must be nonempty with mode 0600: {path.name}")
    if path.parent.is_symlink() or path.parent.stat().st_uid != uid or stat.S_IMODE(path.parent.stat().st_mode) != 0o700:
        raise RuntimeError("Secret directory must belong to UID 1000 with mode 0700.")


def compose_command(environment_file):
    return DOCKER + [
        "compose", "--env-file", str(Path(environment_file).resolve(strict=True)),
        "-f", str(ROOT / "lab/compose.yaml"),
        "-f", str(ROOT / "lab/compose.backup.yaml"),
    ]


def preflight(model):
    server = model["services"]["backup-server"]
    labels = server["labels"]
    repository = bind_source(server, "/data")
    check_backup_mount(
        labels["org.csattt.backup.mount"], repository,
        labels["org.csattt.backup.uuid"],
    )
    for name in ("rest_htpasswd", "repository_password", "rest_http_password"):
        check_secret(model["secrets"][name]["file"])
    source = bind_source(model["services"]["backup-worker"], "/source")
    if not source.is_dir() or source.is_symlink():
        raise RuntimeError("Sample data directory is missing or is a symlink.")
    if source.resolve() != bind_source(model["services"]["workstation"], "/lab/data").resolve():
        raise RuntimeError("Backup source differs from workstation data.")
    real_source, real_repository = source.resolve(), repository.resolve()
    if real_source.is_relative_to(real_repository) or real_repository.is_relative_to(real_source):
        raise RuntimeError("Sample data and backup repository must not overlap.")
    print("PREFLIGHT: OK (UUID, ext4, RW, repository and secret permissions)", file=sys.stderr, flush=True)


def check_running_server(compose, model, environment):
    identifier = subprocess.check_output(
        compose + ["ps", "-q", "backup-server"], env=environment, text=True
    ).strip()
    if not identifier:
        raise RuntimeError("Start backup-server with this helper before running a worker.")
    actual = json.loads(subprocess.check_output(
        DOCKER + ["inspect", identifier], env=environment, text=True
    ))[0]
    expected_repository = bind_source(model["services"]["backup-server"], "/data").resolve()
    mounts = [item for item in actual["Mounts"] if item["Destination"] == "/data"]
    if not actual["State"]["Running"] or len(mounts) != 1:
        raise RuntimeError("Backup server is not running with the expected repository.")
    if mounts[0]["Type"] != "bind" or not mounts[0]["RW"] or Path(mounts[0]["Source"]).resolve() != expected_repository:
        raise RuntimeError("Running server repository differs from the validated mount.")


def check_workstation_source(compose, model, environment):
    identifier = subprocess.check_output(
        compose + ["ps", "-a", "-q", "workstation"], env=environment, text=True
    ).strip()
    if not identifier:
        raise RuntimeError("Expected the stage-1 workstation container before backup.")
    actual = json.loads(subprocess.check_output(
        DOCKER + ["inspect", identifier], env=environment, text=True
    ))[0]
    expected = bind_source(model["services"]["backup-worker"], "/source").resolve()
    mounts = [item for item in actual["Mounts"] if item["Destination"] == "/lab/data"]
    if len(mounts) != 1 or mounts[0]["Type"] != "bind" or Path(mounts[0]["Source"]).resolve() != expected:
        raise RuntimeError("Backup source differs from the actual workstation mount.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    parser.add_argument("action", choices=("preflight", "start", "stop", "status", "client", "restore"))
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    ensure_vm()
    environment = clean_environment()
    compose = compose_command(args.env_file)
    if args.action in ("stop", "status"):
        command = ["stop", "backup-server"] if args.action == "stop" else ["ps", "-a"]
        subprocess.run(compose + command, env=environment, check=True)
        return
    model = json.loads(subprocess.check_output(
        compose + ["config", "--format", "json"], env=environment, text=True
    ))
    preflight(model)
    if args.action == "preflight":
        return
    if args.action == "start":
        command = ["up", "-d", "--no-deps", "backup-server"]
    elif args.action == "client":
        check_running_server(compose, model, environment)
        if not args.arguments or args.arguments[0] not in ("init", "backup", "check", "snapshots", "ls", "stats"):
            raise RuntimeError("Allowed client commands: init, backup, check, snapshots, ls, stats.")
        if args.arguments[0] == "backup":
            check_workstation_source(compose, model, environment)
        command = ["run", "--rm", "--no-deps", "backup-worker"] + args.arguments
    else:
        check_running_server(compose, model, environment)
        if len(args.arguments) != 1 or not re.fullmatch(r"[0-9a-f]{64}", args.arguments[0]):
            raise RuntimeError("Restore requires one full 64-character snapshot ID.")
        target = bind_source(model["services"]["restore-worker"], "/restore")
        if target.is_symlink() or not target.is_dir() or any(target.iterdir()):
            raise RuntimeError("Restore target must be an existing, empty, nonsymlink directory.")
        if target.stat().st_uid != 1000 or not os.access(target, os.W_OK | os.X_OK):
            raise RuntimeError("Restore target must be writable by UID 1000.")
        for protected in (
            bind_source(model["services"]["backup-worker"], "/source"),
            bind_source(model["services"]["backup-server"], "/data"),
        ):
            real_target = target.resolve()
            real_protected = protected.resolve()
            if real_target.is_relative_to(real_protected) or real_protected.is_relative_to(real_target):
                raise RuntimeError("Restore target overlaps protected data.")
        command = ["run", "--rm", "--no-deps", "restore-worker",
                   "restore", args.arguments[0], "--target", "/restore"]
    subprocess.run(compose + command, env=environment, check=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
