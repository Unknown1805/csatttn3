"""Prepare one new synthetic dataset in the watched FIM test area; never replace one."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile

from backup_lab import ensure_vm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/simulator'))
from simulator import NAMES, data_directory, expected_content, inspect_samples


def prepare(data, probe, env_file):
    data, probe, env_file = (Path(p).absolute() for p in (data, probe, env_file))
    metadata = env_file.with_suffix('.json')
    for path in (env_file, metadata):
        if os.path.lexists(path):
            raise RuntimeError(f'Output already exists; existing test state was kept: {path}')
    for path in (data, probe, env_file.parent):
        if path.resolve(strict=True) != path or not path.is_dir():
            raise RuntimeError('Source, watched parent and output parent must be real directories without symlinks')
    if (probe.is_relative_to(data) or data.is_relative_to(probe)
            or env_file.is_relative_to(data) or env_file.is_relative_to(probe)):
        raise RuntimeError('Data, watched test area and output file must not overlap')
    with data_directory(data) as descriptor:
        inspect_samples(descriptor)
        target = Path(tempfile.mkdtemp(prefix='sim33-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-', dir=probe))
        target.chmod(0o755)
        for number, name in enumerate(NAMES, 1):
            descriptor = os.open(target / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(expected_content(number))
        with data_directory(target) as descriptor:
            inspect_samples(descriptor)
    descriptor = os.open(env_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        stream.write(f'LAB_DATA_DIR={data}\nLAB_SIM_DATA_DIR={target}\n')
    descriptor = os.open(metadata, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as stream:
        json.dump({'created_utc': datetime.now(timezone.utc).isoformat(),
                   'source': str(data), 'test_directory': str(target),
                   'container_name': 'csatttn3-' + target.name}, stream, indent=2)
        stream.write('\n')
    return target


def main():
    ensure_vm()
    runtime = Path.home() / 'csattt-lab/runtime'
    env_file = ROOT.parent / 'simulator-test.env'
    target = prepare(runtime / 'sample_data', runtime / 'fim-probe', env_file)
    print(f'SIMULATOR TEST DATA: {target}')
    print(f'ENVIRONMENT: {env_file}')
    print('Source data was validated and kept. No simulator was started.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, RuntimeError) as error:
        raise SystemExit(f'STOP: {error}')
