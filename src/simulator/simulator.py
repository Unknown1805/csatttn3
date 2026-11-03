"""Rename-only exercise for exactly 15 synthetic CSATTT files on Linux."""
import argparse
from contextlib import contextmanager
import ctypes
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import time
import uuid

DATA_DIR = Path('/lab/data')
NAMES = tuple(f'file_{n:02d}.txt' for n in range(1, 16))
SUFFIX = '.simlocked'
NOTE = 'SIMULATION_NOTE.txt'
STOP_SIGNAL = None


def expected_content(number):
    return f'CSATTT N3 - SYNTHETIC DATA ONLY\nfile={number:02d}\n'.encode()


def log_event(run_id, event, **fields):
    print(json.dumps({'time_utc': datetime.now(timezone.utc).isoformat(),
                      'run_id': run_id, 'pid': os.getpid(), 'event': event, **fields}), flush=True)


@contextmanager
def data_directory(path):
    descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield descriptor
    finally:
        os.close(descriptor)


def file_signature(info):
    # Reading may update atime; it does not change the approved file content.
    return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def inspect_one(directory, name, number):
    before = os.stat(name, dir_fd=directory, follow_symlinks=False)
    expected = expected_content(number)
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != len(expected):
        raise RuntimeError(f'Refusing non-regular, linked or unexpected-size file: {name}')
    descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    try:
        info = os.fstat(descriptor)
        if file_signature(info) != file_signature(before):
            raise RuntimeError(f'File changed while opening: {name}')
        if os.pread(descriptor, len(expected) + 1, 0) != expected:
            raise RuntimeError(f'Not the approved synthetic content: {name}')
        if file_signature(os.fstat(descriptor)) != file_signature(info):
            raise RuntimeError(f'File metadata changed while reading: {name}')
        return file_signature(info)
    finally:
        os.close(descriptor)


def inspect_samples(directory):
    if set(os.listdir(directory)) != set(NAMES):
        raise RuntimeError('Expected exactly file_01.txt through file_15.txt; no extra entries')
    return {name: inspect_one(directory, name, n) for n, name in enumerate(NAMES, 1)}


def rename_noreplace():
    libc = ctypes.CDLL(None, use_errno=True)
    function = libc.renameat2
    function.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    function.restype = ctypes.c_int

    def rename(directory, source, target):
        # RENAME_NOREPLACE also protects a destination created after preflight.
        if function(directory, os.fsencode(source), directory, os.fsencode(target), 1) != 0:
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error), target)
    return rename


def simulate(path, apply=False):
    run_id = 'sim33-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + uuid.uuid4().hex[:8]
    changed = []
    mode = 'apply' if apply else 'dry-run'
    log_event(run_id, 'start', mode=mode, simulation=True)
    try:
        with data_directory(path) as directory:
            signatures = inspect_samples(directory)
            log_event(run_id, 'preflight_ok', mode=mode, files=15, bytes=600)
            if not apply:
                log_event(run_id, 'dry_run_complete', changed_files=0,
                          planned_renames=[{'source': n, 'target': n + SUFFIX} for n in NAMES],
                          planned_note=NOTE)
                return 0
            rename = rename_noreplace()
            if STOP_SIGNAL is not None:
                log_event(run_id, 'stopped', signal=STOP_SIGNAL, renamed=changed)
                return 128 + STOP_SIGNAL
            note = ('CSATTT N3 - SAFE SIMULATION ONLY\n'
                    'Files are renamed for a course exercise. Their content is unchanged.\n'
                    'No encryption, payment, propagation or persistence is performed.\n'
                    f'run_id={run_id}\n')
            descriptor = os.open(NOTE, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                 0o644, dir_fd=directory)
            with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
                stream.write(note)
                stream.flush()
                os.fsync(stream.fileno())
            os.fsync(directory)
            log_event(run_id, 'simulation_note_created', path=NOTE)
            for index, name in enumerate(NAMES):
                if STOP_SIGNAL is not None:
                    log_event(run_id, 'stopped', signal=STOP_SIGNAL, renamed=changed)
                    return 128 + STOP_SIGNAL
                expected = set(NAMES[index:]) | {n + SUFFIX for n in changed} | {NOTE}
                if set(os.listdir(directory)) != expected:
                    raise RuntimeError('Directory entries changed during the run; existing state was kept')
                if inspect_one(directory, name, index + 1) != signatures[name]:
                    raise RuntimeError(f'Source changed after preflight: {name}')
                rename(directory, name, name + SUFFIX)
                changed.append(name)
                os.fsync(directory)
                log_event(run_id, 'file_renamed', source=name, target=name + SUFFIX,
                          sha256=hashlib.sha256(expected_content(index + 1)).hexdigest())
                if index < len(NAMES) - 1:
                    time.sleep(1)
            if set(os.listdir(directory)) != {n + SUFFIX for n in NAMES} | {NOTE}:
                raise RuntimeError('Final directory entries differ from the planned result')
            for number, name in enumerate(NAMES, 1):
                inspect_one(directory, name + SUFFIX, number)
            log_event(run_id, 'complete', renamed_files=len(changed), note=NOTE)
            return 0
    except (OSError, RuntimeError, AttributeError) as error:
        log_event(run_id, 'rejected_or_failed', error=str(error), renamed=changed,
                  note='No automatic rollback; preserve this state and the logs.')
        return 1


def request_stop(number, frame):
    global STOP_SIGNAL
    STOP_SIGNAL = number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Apply to the approved synthetic dataset; default is dry-run')
    args = parser.parse_args()
    if os.geteuid() == 0:
        raise SystemExit('STOP: Run the simulator as the non-root container user.')
    signal.signal(signal.SIGINT, request_stop)
    signal.signal(signal.SIGTERM, request_stop)
    return simulate(DATA_DIR, apply=args.apply)


if __name__ == '__main__':
    raise SystemExit(main())
