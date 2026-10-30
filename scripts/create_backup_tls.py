"""Create a private lab CA and a TLS server certificate; never overwrite files."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def openssl(*arguments):
    return subprocess.run(
        ["openssl", *map(str, arguments)], check=True,
        capture_output=True, text=True, timeout=60,
    ).stdout


def create(runtime, authority):
    runtime = Path(runtime).absolute()
    authority = Path(authority).absolute()
    if runtime == authority or runtime.is_relative_to(authority) or authority.is_relative_to(runtime):
        raise RuntimeError("CA directory and runtime TLS directory must be separate.")
    for directory in (runtime, authority):
        if directory.exists() or directory.is_symlink():
            raise RuntimeError(f"Refusing an existing destination: {directory}")
        if not directory.parent.is_dir() or directory.parent.is_symlink():
            raise RuntimeError("Create the trusted parent directory first.")
    old_umask = os.umask(0o077)
    try:
        authority.mkdir(mode=0o700)
        runtime.mkdir(mode=0o700)
        with tempfile.TemporaryDirectory(prefix="csr-", dir=authority) as temporary:
            csr = Path(temporary) / "server.csr"
            extensions = Path(temporary) / "server.ext"
            extensions.write_text(
                "[server]\n"
                "basicConstraints=critical,CA:FALSE\n"
                "keyUsage=critical,digitalSignature,keyEncipherment\n"
                "extendedKeyUsage=serverAuth\n"
                "subjectAltName=DNS:backup-server\n"
                "subjectKeyIdentifier=hash\n"
                "authorityKeyIdentifier=keyid,issuer\n"
            )
            openssl(
                "req", "-x509", "-newkey", "rsa:3072", "-noenc", "-sha256",
                "-days", "1095", "-subj", "/CN=CSATTT N3 Backup CA",
                "-addext", "basicConstraints=critical,CA:TRUE,pathlen:0",
                "-addext", "keyUsage=critical,keyCertSign,cRLSign",
                "-addext", "subjectKeyIdentifier=hash",
                "-keyout", authority / "ca.key", "-out", authority / "ca.crt",
            )
            openssl(
                "req", "-new", "-newkey", "rsa:3072", "-noenc", "-sha256",
                "-subj", "/CN=backup-server", "-keyout", runtime / "server.key",
                "-out", csr,
            )
            openssl(
                "x509", "-req", "-in", csr, "-CA", authority / "ca.crt",
                "-CAkey", authority / "ca.key", "-CAcreateserial", "-sha256",
                "-days", "365", "-extfile", extensions, "-extensions", "server",
                "-out", runtime / "server.crt",
            )
        shutil.copyfile(authority / "ca.crt", runtime / "ca.crt")
        for directory in (runtime, authority):
            for path in directory.iterdir():
                path.chmod(0o600)
        print(openssl(
            "verify", "-CAfile", runtime / "ca.crt", "-purpose", "sslserver",
            "-verify_hostname", "backup-server", runtime / "server.crt",
        ).strip())
        print(openssl(
            "x509", "-in", runtime / "server.crt", "-noout", "-subject",
            "-issuer", "-dates", "-ext", "subjectAltName", "-fingerprint", "-sha256",
        ).strip())
        print(f"TLS files: {runtime}")
        print(f"CA private key retained outside containers: {authority}")
    finally:
        os.umask(old_umask)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("runtime_directory")
    parser.add_argument("--ca-directory", required=True)
    args = parser.parse_args()
    from backup_lab import ensure_vm
    ensure_vm()
    create(args.runtime_directory, args.ca_directory)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
