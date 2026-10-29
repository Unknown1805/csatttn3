import argparse
import json
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


DATA_DIR = Path("/lab/data")


def log_event(event, **fields):
    print(
        json.dumps(
            {"time_utc": datetime.now(timezone.utc).isoformat(), "event": event, **fields}
        ),
        flush=True,
    )


def seed_samples(directory):
    if not directory.is_dir():
        raise SystemExit("Data directory does not exist; check the bind mount.")
    if any(directory.iterdir()):
        raise SystemExit("Data directory is not empty; existing data was kept.")

    for number in range(1, 16):
        path = directory / f"file_{number:02d}.txt"
        with path.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(f"CSATTT N3 - SYNTHETIC DATA ONLY\nfile={number:02d}\n")
    log_event("seed_complete", files=15)


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, message, *args):
        log_event("http_request", client=self.client_address[0], message=message % args)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("seed", "serve"))
    action = parser.parse_args().action

    if action == "seed":
        seed_samples(DATA_DIR)
        return
    if not DATA_DIR.is_dir():
        raise SystemExit("Data directory does not exist; check the bind mount.")

    handler = partial(Handler, directory=str(DATA_DIR))
    log_event("server_start", port=8080, data_dir=str(DATA_DIR))
    with ThreadingHTTPServer(("0.0.0.0", 8080), handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
