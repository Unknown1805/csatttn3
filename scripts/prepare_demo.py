"""Prepare an independent D1 dataset and Compose project; start no containers."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import uuid

from backup_lab import DOCKER, clean_environment, ensure_vm
from prepare_simulator_test import NAMES, data_directory, expected_content, inspect_samples
from prepare_simulator_test import prepare as prepare_copy

ROOT = Path(__file__).resolve().parents[1]
VM_UUID = 'bd0eab21-9089-4489-a703-b7771e210d5e'
BACKUP_UUID = '72fd2516-3134-4ff1-abcd-50369a6db1b9'


def guest_preflight(lab):
    ensure_vm()
    if socket.gethostname() != 'csattt3' or Path.home() != Path('/home/csattt3'):
        raise RuntimeError('Run as csattt3 inside the approved Ubuntu VM.')
    actual = subprocess.check_output(
        ['sudo', 'cat', '/sys/class/dmi/id/product_uuid'], text=True, timeout=30
    ).strip().lower()
    if actual != VM_UUID:
        raise RuntimeError('Wrong VM UUID.')
    if any((p / 'device').exists() for p in Path('/sys/class/net').iterdir()):
        raise RuntimeError('VM still has a hardware network interface.')
    for family in ('-4', '-6'):
        routes = json.loads(subprocess.check_output(
            ['ip', '-j', family, 'route', 'show', 'table', 'all'], text=True, timeout=10
        ))
        if any(route.get('dst') == 'default' for route in routes):
            raise RuntimeError('VM still has an external default route.')
    if os.path.lexists(Path('/dev/disk/by-uuid') / BACKUP_UUID):
        raise RuntimeError('Backup disk is attached.')
    mounted = subprocess.run(
        ['findmnt', '-rn', '-M', '/mnt/csattt-backup'], capture_output=True, timeout=10
    )
    if mounted.returncode != 1:
        raise RuntimeError('Cannot confirm the backup mount is absent.')
    if shutil.disk_usage(lab).free < 15 * 1024**3:
        raise RuntimeError('Guest has less than 15 GiB free.')
    active = subprocess.check_output(
        DOCKER + ['ps', '--filter', 'label=com.docker.compose.project=csatttn3',
                  '--format', '{{.Label "com.docker.compose.service"}}'],
        env=clean_environment(), text=True, timeout=30,
    ).splitlines()
    allowed = {'workstation', 'wazuh.manager', 'wazuh.indexer', 'wazuh.dashboard'}
    if not set(active) <= allowed:
        raise RuntimeError('An unexpected original-project service is running.')
    if not allowed.difference({'workstation'}) <= set(active):
        raise RuntimeError('Start and verify the three existing Wazuh services first.')


def write_new(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(content)


def prepare(data, probe, bundle, commit):
    data, probe, bundle = (Path(p).absolute() for p in (data, probe, bundle))
    if not re.fullmatch('[0-9a-f]{40}', commit):
        raise RuntimeError('Expected a full source commit SHA.')
    for path in (data, probe, bundle):
        if any(c in str(path) for c in "\n\r\x00'$\\"):
            raise RuntimeError('Unsupported character in a Compose environment path.')
        if path.resolve(strict=True) != path or not path.is_dir():
            raise RuntimeError('Paths must be existing real directories without symlinks.')
    outputs = ('copy.env', 'copy.json', 'demo.env', 'demo.json', 'source.sha256')
    if any(os.path.lexists(bundle / name) for name in outputs):
        raise RuntimeError('D1 preparation output already exists; keep it and use a new bundle.')
    if data.is_relative_to(probe) or probe.is_relative_to(data) or any(
        bundle.is_relative_to(p) or p.is_relative_to(bundle) for p in (data, probe)
    ):
        raise RuntimeError('Source, watched area and output bundle must not overlap.')
    # Reuse the S1 validator/copy routine; original data is never mounted in D1.
    target = prepare_copy(data, probe, bundle / 'copy.env')
    for directory in (data, target):
        with data_directory(directory) as descriptor:
            inspect_samples(descriptor)
    project = 'csatttn3-d1-' + uuid.uuid4().hex[:12]
    write_new(bundle / 'demo.env', f'LAB_DATA_DIR={target}\nLAB_SIM_DATA_DIR={target}\n')
    hashes = {name: hashlib.sha256(expected_content(n)).hexdigest()
              for n, name in enumerate(NAMES, 1)}
    write_new(bundle / 'source.sha256', ''.join(f'{hashes[name]}  {name}\n' for name in NAMES))
    result = {
        'status': 'prepared_only', 'created_utc': datetime.now(timezone.utc).isoformat(),
        'source_commit': commit, 'project': project, 'original_directory': str(data),
        'active_directory': str(target), 'fim_prefix': '/lab/fim-probe/' + target.name + '/',
        'files': 15, 'bytes': 600, 'sha256': hashes,
        'containers_started': False, 'apply_executed': False,
    }
    write_new(bundle / 'demo.json', json.dumps(result, indent=2) + '\n')
    return result


def main():
    lab = Path.home() / 'csattt-lab'
    guest_preflight(lab)
    commit = (ROOT.parent / 'COMMIT.txt').read_text().strip()
    result = prepare(lab / 'runtime/sample_data', lab / 'runtime/fim-probe', ROOT.parent, commit)
    print('D1 PREP: OK — original 15/15 unchanged; new copy 15/15.')
    print('PROJECT:', result['project'])
    print('ACTIVE DATA:', result['active_directory'])
    print('FIM PREFIX:', result['fim_prefix'])
    print('No containers were started. No simulator was applied.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError, subprocess.SubprocessError, ValueError) as error:
        raise SystemExit(f'STOP: {error}')
