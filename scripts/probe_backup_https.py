"""Check real TLS, hostname validation, HTTP rejection and REST authentication."""
import argparse
import base64
import http.client
import json
from pathlib import Path
import socket
import ssl
import subprocess
import sys

import backup_lab as lab


class Connection(http.client.HTTPSConnection):
    def __init__(self, address, name, context):
        super().__init__(name, port=8000, timeout=5, context=context)
        self.address = address

    def connect(self):
        raw = socket.create_connection((self.address, self.port), timeout=self.timeout)
        try:
            self.sock = self._context.wrap_socket(raw, server_hostname=self.host)
        except BaseException:
            raw.close()
            raise


def request(address, context, name="backup-server", password=None):
    connection = Connection(address, name, context)
    try:
        headers = {}
        if password is not None:
            token = base64.b64encode(f"csattt:{password}".encode()).decode("ascii")
            headers["Authorization"] = "Basic " + token
        connection.request("GET", "/csattt/config", headers=headers)
        protocol = connection.sock.version()
        response = connection.getresponse()
        data = response.read(65536)
        return response.status, protocol, data
    finally:
        connection.close()


def certificate_rejected(address, context, name):
    try:
        request(address, context, name=name)
    except ssl.SSLCertVerificationError as error:
        return error.verify_message
    raise RuntimeError("An invalid trust/name configuration was accepted.")


def probe(model, compose, environment):
    lab.preflight(model)
    lab.check_running_server(compose, model, environment)
    identifier = subprocess.check_output(
        compose + ["ps", "-q", "backup-server"], env=environment, text=True,
    ).strip()
    actual = json.loads(subprocess.check_output(
        lab.DOCKER + ["inspect", identifier], env=environment, text=True,
    ))[0]
    if actual["HostConfig"].get("PortBindings"):
        raise RuntimeError("Backup server must not publish ports.")
    if set(actual["NetworkSettings"]["Networks"]) != {"csatttn3_backup_net"}:
        raise RuntimeError("Backup server must only use the internal backup network.")
    network = actual["NetworkSettings"]["Networks"]["csatttn3_backup_net"]
    network_info = json.loads(subprocess.check_output(
        lab.DOCKER + ["network", "inspect", network["NetworkID"]],
        env=environment, text=True,
    ))[0]
    if not network_info["Internal"]:
        raise RuntimeError("Backup network is not internal.")
    address = network["IPAddress"]
    ca = lab.tls_paths(model)["backup_ca"]
    context = ssl.create_default_context(cafile=str(ca))
    context.minimum_version = ssl.TLSVersion.TLSv1_3
    paths = model["secrets"]
    password = Path(paths["rest_http_password"]["file"]).read_text().strip()
    result = {}
    status, protocol, config = request(address, context, password=password)
    if status != 200 or protocol != "TLSv1.3":
        raise RuntimeError("Existing repository config is not accessible through TLS 1.3.")
    # The REST backend returns the encrypted repository config as opaque bytes.
    # Restic itself decrypts and authenticates it in the subsequent client tests.
    if not config:
        raise RuntimeError("Existing repository returned an empty encrypted config.")
    result["valid_ca_and_name"] = {
        "status": status, "protocol": protocol, "config_bytes": len(config),
    }
    for label, value in (("no_auth", None), ("wrong_password", password + "-incorrect")):
        code, _, _ = request(address, context, password=value)
        if code != 401:
            raise RuntimeError(f"Authentication test failed: {label} returned {code}.")
        result[label] = code
    # A fresh client context has no trusted roots. Do not send credentials in negative tests.
    result["untrusted_ca_rejected"] = certificate_rejected(
        address, ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT), "backup-server",
    )
    result["wrong_name_rejected"] = certificate_rejected(
        address, context, "incorrect-backup-server.invalid",
    )
    old_tls = ssl.create_default_context(cafile=str(ca))
    old_tls.minimum_version = ssl.TLSVersion.TLSv1_2
    old_tls.maximum_version = ssl.TLSVersion.TLSv1_2
    try:
        request(address, old_tls)
    except ssl.SSLError as error:
        if error.reason not in ("TLSV1_ALERT_PROTOCOL_VERSION", "UNSUPPORTED_PROTOCOL"):
            raise
        result["tls12_rejected"] = error.reason
    else:
        raise RuntimeError("TLS 1.2 unexpectedly succeeded.")
    # Go's HTTPS server can return a plaintext 400 explaining that TLS is required.
    # This request intentionally contains no credentials.
    connection = http.client.HTTPConnection(address, 8000, timeout=5)
    try:
        connection.request("GET", "/csattt/config")
        response = connection.getresponse()
        body = response.read(65536)
        if response.status != 400 or b"HTTPS" not in body:
            raise RuntimeError("Plain HTTP did not give the expected TLS-required rejection.")
        result["plain_http_rejected"] = response.status
    except (http.client.RemoteDisconnected, ConnectionResetError):
        result["plain_http_rejected"] = "connection closed"
    finally:
        connection.close()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--env-file", required=True)
    args = parser.parse_args()
    lab.ensure_vm()
    environment = lab.clean_environment()
    compose = lab.compose_command(args.env_file)
    model = json.loads(subprocess.check_output(
        compose + ["config", "--format", "json"], env=environment, text=True,
    ))
    print(json.dumps(probe(model, compose, environment), indent=2))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"STOP: {error}", file=sys.stderr)
        sys.exit(1)
