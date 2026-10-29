"""Create new lab secrets in the Ubuntu VM without printing them."""
import argparse
import os
from pathlib import Path
import secrets
import subprocess

from backup_lab import DOCKER, clean_environment, ensure_vm

SERVER_IMAGE = "restic/rest-server:0.14.0"


def write_new(path, value):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        stream.write(value + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    ensure_vm()
    directory = args.directory.expanduser().absolute()
    if os.path.lexists(directory):
        raise RuntimeError("Secret directory already exists; existing secrets were kept.")
    repository_password = secrets.token_urlsafe(32)
    http_password = secrets.token_urlsafe(32)
    result = subprocess.run(
        DOCKER + ["run", "--rm", "--pull=never", "-i", "--network", "none",
                  "--read-only", "--user", "1000:1000", "--cap-drop", "ALL",
                  "--security-opt", "no-new-privileges:true",
                  "--entrypoint", "htpasswd", SERVER_IMAGE, "-nBi", "csattt"],
        input=http_password + "\n", capture_output=True, text=True,
        env=clean_environment(), check=True,
    )
    record = result.stdout.strip()
    if not record.startswith(("csattt:$2a$", "csattt:$2b$", "csattt:$2y$")) or "\n" in record:
        raise RuntimeError("htpasswd did not return one bcrypt record.")
    directory.parent.mkdir(parents=True, exist_ok=True)
    directory.mkdir(mode=0o700)
    write_new(directory / "repository-password", repository_password)
    write_new(directory / "rest-http-password", http_password)
    write_new(directory / "rest.htpasswd", record)
    print(f"Secrets created at {directory}; values were not printed.")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        raise SystemExit(f"STOP: {error}")
