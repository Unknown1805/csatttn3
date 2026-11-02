"""Prepare private Wazuh credentials and certificates inside the Ubuntu lab VM."""
import argparse
import os
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import sys

from backup_lab import DOCKER, clean_environment, ensure_vm
from create_backup_secrets import SERVER_IMAGE, write_new
from create_backup_tls import openssl


def bcrypt_hash(password):
    # Reuse the already installed Restic server's htpasswd; no new hash dependency.
    result = subprocess.run(
        DOCKER + ["run", "--rm", "--pull=never", "-i", "--network", "none",
                  "--read-only", "--user", "1000:1000", "--cap-drop", "ALL",
                  "--security-opt", "no-new-privileges:true", "--entrypoint",
                  "htpasswd", SERVER_IMAGE, "-nBi", "-C", "12", "csattt"],
        input=password + "\n", capture_output=True, text=True, timeout=60,
        env=clean_environment(), check=True,
    )
    record = result.stdout.strip()
    if not re.fullmatch(r"csattt:\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}", record):
        raise RuntimeError("htpasswd did not return one bcrypt record.")
    return record.split(":", 1)[1]


def certificates(directory):
    authority, runtime = directory / "ca", directory / "tls"
    authority.mkdir(mode=0o700)
    runtime.mkdir(mode=0o700)
    openssl(
        "req", "-x509", "-newkey", "rsa:3072", "-noenc", "-sha256",
        "-days", "1095", "-subj", "/CN=CSATTT N3 Monitoring CA",
        "-addext", "basicConstraints=critical,CA:TRUE,pathlen:0",
        "-addext", "keyUsage=critical,keyCertSign,cRLSign",
        "-addext", "subjectKeyIdentifier=hash",
        "-keyout", authority / "ca.key", "-out", authority / "ca.pem",
    )
    for name in ("wazuh.manager", "wazuh.indexer", "wazuh.dashboard", "admin"):
        csr, extension = authority / (name + ".csr"), authority / (name + ".ext")
        usage = "clientAuth" if name == "admin" else "serverAuth,clientAuth"
        san = "DNS:" + name
        if name == "wazuh.dashboard":
            san += ",DNS:localhost,IP:127.0.0.1"
        write_new(extension,
                  "basicConstraints=critical,CA:FALSE\n"
                  "keyUsage=critical,digitalSignature,keyEncipherment\n"
                  f"extendedKeyUsage={usage}\nsubjectAltName={san}\n"
                  "subjectKeyIdentifier=hash\nauthorityKeyIdentifier=keyid,issuer")
        openssl(
            "req", "-new", "-newkey", "rsa:3072", "-noenc", "-sha256",
            "-subj", f"/C=US/L=California/O=Wazuh/OU=Wazuh/CN={name}",
            "-keyout", runtime / (name + "-key.pem"), "-out", csr,
        )
        openssl(
            "x509", "-req", "-in", csr, "-CA", authority / "ca.pem",
            "-CAkey", authority / "ca.key", "-set_serial", str(secrets.randbits(128) or 1),
            "-sha256", "-days", "365", "-extfile", extension,
            "-out", runtime / (name + ".pem"),
        )
        openssl("verify", "-CAfile", authority / "ca.pem", runtime / (name + ".pem"))
        if name != "admin":
            openssl("verify", "-CAfile", authority / "ca.pem", "-purpose", "sslserver",
                    "-verify_hostname", name, runtime / (name + ".pem"))
    shutil.copyfile(authority / "ca.pem", runtime / "root-ca.pem")
    for path in runtime.iterdir():
        path.chmod(0o600)


def prepare(directory, data, probe):
    paths = [Path(p).expanduser().absolute() for p in (directory, data, probe)]
    directory, data, probe = paths
    for path in paths:
        if path.resolve() != path or path.is_symlink():
            raise RuntimeError("Runtime and data paths must not contain symlinks.")
    for i, path in enumerate(paths):
        if any(path.is_relative_to(other) or other.is_relative_to(path)
               for other in paths[i + 1:]):
            raise RuntimeError("Private configuration, source and probe paths must not overlap.")
    if os.path.lexists(directory) or os.path.lexists(probe):
        raise RuntimeError("Destination already exists; existing files were kept. Do not regenerate.")
    if not data.is_dir():
        raise RuntimeError("The existing sample data directory is missing.")
    names = [f"file_{number:02d}.txt" for number in range(1, 16)]
    if sorted(p.name for p in data.iterdir()) != names:
        raise RuntimeError("Expected exactly the original 15 sample files.")
    for number, name in enumerate(names, 1):
        path = data / name
        expected = f"CSATTT N3 - SYNTHETIC DATA ONLY\nfile={number:02d}\n".encode()
        if path.is_symlink() or not path.is_file() or path.read_bytes() != expected:
            raise RuntimeError("Sample data is not the expected clean baseline.")
    passwords = {name: "Aa1!" + secrets.token_hex(24) for name in ("admin", "dashboard", "api")}
    hashes = {name: bcrypt_hash(passwords[name]) for name in ("admin", "dashboard")}
    previous = os.umask(0o077)
    try:
        directory.parent.mkdir(parents=True, exist_ok=True)
        probe.parent.mkdir(parents=True, exist_ok=True)
        directory.mkdir(mode=0o700)
        probe.mkdir(mode=0o700)
        config = directory / "config"
        config.mkdir(mode=0o700)
        certificates(directory)
        write_new(config / "internal_users.yml",
                  '_meta:\n  type: "internalusers"\n  config_version: 2\n'
                  'admin:\n  hash: "' + hashes["admin"] + '"\n'
                  '  reserved: true\n  backend_roles: ["admin"]\n'
                  'kibanaserver:\n  hash: "' + hashes["dashboard"] + '"\n  reserved: true')
        environment = {
            "LAB_DATA_DIR": str(data), "LAB_FIM_PROBE_DIR": str(probe),
            "LAB_MONITORING_DIR": str(directory),
            "WAZUH_ADMIN_PASSWORD": passwords["admin"],
            "WAZUH_DASHBOARD_PASSWORD": passwords["dashboard"],
            "WAZUH_API_PASSWORD": passwords["api"],
        }
        write_new(directory / "monitoring.env", "\n".join(f"{k}={v}" for k, v in environment.items()))
        write_new(directory / "dashboard-login.txt", "username=admin\npassword=" + passwords["admin"])
    finally:
        os.umask(previous)
    print(f"MONITORING RUNTIME: OK\nEnvironment: {directory / 'monitoring.env'}")
    print(f"Login stays private at: {directory / 'dashboard-login.txt'}")
    print("No main Wazuh services were started. No source files were changed.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    ensure_vm()
    if args.directory.expanduser().resolve().is_relative_to(Path(__file__).resolve().parents[1]):
        raise RuntimeError("Keep generated private files outside the source checkout.")
    runtime = Path.home() / "csattt-lab/runtime"
    prepare(args.directory, runtime / "sample_data", runtime / "fim-probe")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
