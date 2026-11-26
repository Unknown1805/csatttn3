"""D1 preparation uses a separate, validated copy and never starts Docker."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_demo as demo

NEW_VM_UUID = '0b8c9f5a-6d01-44d4-83d9-db5d9e0ce1bc'


class DemoPreparation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='csattt-d1-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data, self.probe, self.bundle = (self.root / n for n in ('data', 'probe', 'bundle'))
        for path in (self.data, self.probe, self.bundle):
            path.mkdir()
        for number, name in enumerate(demo.NAMES, 1):
            (self.data / name).write_bytes(demo.expected_content(number))
        self.original = {p.name: p.read_bytes() for p in self.data.iterdir()}
        (self.probe / 's1-evidence').mkdir()
        (self.probe / 's1-evidence/result.json').write_text('KEEP S1\n')
        self.commit = 'a' * 40

    def prepare(self):
        return demo.prepare(self.data, self.probe, self.bundle, self.commit)

    def assert_kept(self):
        self.assertEqual({p.name: p.read_bytes() for p in self.data.iterdir()}, self.original)
        self.assertEqual((self.probe / 's1-evidence/result.json').read_text(), 'KEEP S1\n')

    def test_new_project_and_same_copy_for_http_and_simulator(self):
        with patch.object(subprocess, 'run') as run, patch.object(subprocess, 'check_output') as output:
            result = self.prepare()
        run.assert_not_called()
        output.assert_not_called()
        target = Path(result['active_directory'])
        self.assertNotEqual(target, self.data)
        self.assertEqual(target.parent, self.probe)
        self.assertEqual({p.name: p.read_bytes() for p in target.iterdir()}, self.original)
        self.assertEqual((self.bundle / 'demo.env').read_text().splitlines(),
                         [f'LAB_DATA_DIR={target}', f'LAB_SIM_DATA_DIR={target}'])
        self.assertRegex(result['project'], r'^csatttn3-d1-[0-9a-f]{12}$')
        self.assertFalse(result['apply_executed'])
        self.assertFalse(result['containers_started'])
        self.assertEqual(json.loads((self.bundle / 'demo.json').read_text()), result)
        self.assertEqual(len((self.bundle / 'source.sha256').read_text().splitlines()), 15)
        for name in ('copy.env', 'copy.json', 'demo.env', 'demo.json', 'source.sha256'):
            self.assertEqual((self.bundle / name).stat().st_mode & 0o777, 0o600)
        self.assert_kept()

    def test_existing_output_cannot_be_overwritten_or_create_another_copy(self):
        self.prepare()
        before = {p.name: p.read_bytes() for p in self.bundle.iterdir()}
        directories = set(self.probe.iterdir())
        with self.assertRaisesRegex(RuntimeError, 'already exists'):
            self.prepare()
        self.assertEqual({p.name: p.read_bytes() for p in self.bundle.iterdir()}, before)
        self.assertEqual(set(self.probe.iterdir()), directories)
        self.assert_kept()

    def test_compose_uses_private_project_and_the_same_active_copy(self):
        result = self.prepare()
        model = json.loads(subprocess.check_output([
            'docker', 'compose', '--project-name', result['project'],
            '--env-file', str(self.bundle / 'demo.env'), '--profile', 'incident',
            '-f', str(ROOT / 'lab/compose.yaml'),
            '-f', str(ROOT / 'lab/compose.incident.yaml'), 'config', '--format', 'json',
        ], text=True))
        self.assertEqual(model['name'], result['project'])
        self.assertEqual(set(model['services']), {'workstation', 'simulator'})
        for service in model['services'].values():
            mount = next(m for m in service['volumes'] if m['target'] == '/lab/data')
            self.assertEqual(mount['source'], result['active_directory'])
            self.assertNotEqual(mount['source'], str(self.data))
            self.assertFalse(service.get('ports'))
            self.assertFalse(service.get('secrets'))
        self.assertTrue(model['networks']['incident_net']['internal'])
        self.assertEqual(model['networks']['incident_net']['name'], result['project'] + '_incident_net')
        self.assert_kept()

    def test_corrupt_original_cannot_seed_a_demo(self):
        (self.data / demo.NAMES[0]).write_bytes(b'X' * 40)
        with self.assertRaisesRegex(RuntimeError, 'approved synthetic'):
            self.prepare()
        self.assertEqual(set(self.probe.iterdir()), {self.probe / 's1-evidence'})
        self.assertFalse(any(self.bundle.iterdir()))

    def test_symlink_and_linked_data_are_refused(self):
        link = self.root / 'link'
        link.symlink_to(self.data, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, 'without symlinks'):
            demo.prepare(link, self.probe, self.bundle, self.commit)
        os.link(self.data / demo.NAMES[0], self.root / 'outside')
        with self.assertRaisesRegex(RuntimeError, 'linked'):
            self.prepare()
        self.assertFalse(any(self.bundle.iterdir()))
        self.assert_kept()

    def test_overlap_and_environment_injection_are_refused(self):
        with self.assertRaisesRegex(RuntimeError, 'overlap'):
            demo.prepare(self.data, self.probe, self.probe, self.commit)
        unsafe = self.root / 'value$EXPANSION'
        unsafe.mkdir()
        with self.assertRaisesRegex(RuntimeError, 'Unsupported character'):
            demo.prepare(self.data, self.probe, unsafe, self.commit)
        self.assertFalse(any(unsafe.iterdir()))
        self.assert_kept()

    def test_invalid_commit_is_refused_before_writes(self):
        with self.assertRaisesRegex(RuntimeError, 'full source commit'):
            demo.prepare(self.data, self.probe, self.bundle, 'HEAD')
        self.assertFalse(any(self.bundle.iterdir()))

    def preflight(self, fault=None, *, guest_uuid=demo.VM_UUID, expected_uuid=None):
        def output(arguments, **kwargs):
            if 'product_uuid' in arguments[-1]:
                return 'wrong' if fault == 'uuid' else guest_uuid
            if arguments[0] == 'ip':
                return '[{"dst":"default"}]' if fault == 'route' else '[]'
            if 'ps' in arguments:
                if fault == 'no_wazuh':
                    return 'workstation\n'
                return ('wazuh.manager\nwazuh.indexer\nwazuh.dashboard\n'
                        + ('backup-server\n' if fault == 'backup_service' else ''))
            raise AssertionError(arguments)

        class Interface:
            def __truediv__(self, name):
                return SimpleNamespace(exists=lambda: fault == 'nic')

        with patch.object(demo, 'ensure_vm'), patch.object(demo.socket, 'gethostname', return_value='csattt3'), \
                patch.object(Path, 'home', return_value=Path('/home/csattt3')), \
                patch.object(Path, 'iterdir', return_value=iter([Interface()])), \
                patch.object(demo.os.path, 'lexists', return_value=fault == 'backup_disk'), \
                patch.object(demo.shutil, 'disk_usage', return_value=SimpleNamespace(free=(1 if fault == 'low_disk' else 40) * 1024**3)), \
                patch.object(demo.subprocess, 'check_output', side_effect=output), \
                patch.object(demo.subprocess, 'run', return_value=SimpleNamespace(returncode=0 if fault == 'mounted' else 1)) as run:
            if expected_uuid is None:
                demo.guest_preflight(self.root)
            else:
                demo.guest_preflight(self.root, expected_uuid)
        self.assertEqual(run.call_args.args[0], ['findmnt', '-rn', '-M', '/mnt/csattt-backup'])

    def test_preflight_accepts_isolated_guest_and_never_starts_services(self):
        self.preflight()

    def test_preflight_rejects_wrong_vm_network_and_attached_backup(self):
        for fault in ('uuid', 'route', 'nic', 'backup_disk', 'mounted', 'backup_service', 'no_wazuh', 'low_disk'):
            with self.subTest(fault=fault), self.assertRaises(RuntimeError):
                self.preflight(fault)

    def test_new_guest_requires_matching_explicit_uuid(self):
        with self.assertRaisesRegex(RuntimeError, 'Wrong VM UUID'):
            self.preflight(guest_uuid=NEW_VM_UUID)
        self.preflight(guest_uuid=NEW_VM_UUID, expected_uuid=NEW_VM_UUID.upper())

    def test_explicit_uuid_does_not_skip_network_or_backup_checks(self):
        for fault in ('route', 'nic', 'backup_disk', 'mounted', 'backup_service'):
            with self.subTest(fault=fault), self.assertRaises(RuntimeError):
                self.preflight(fault, guest_uuid=NEW_VM_UUID, expected_uuid=NEW_VM_UUID)

    def test_malformed_expected_uuid_stops_before_guest_checks(self):
        with patch.object(demo, 'ensure_vm') as ensure, self.assertRaisesRegex(RuntimeError, 'full VM UUID'):
            demo.guest_preflight(self.root, 'not-a-uuid')
        ensure.assert_not_called()

    def test_cli_passes_explicit_uuid_to_preflight(self):
        with patch.object(sys, 'argv', ['prepare_demo.py', '--vm-uuid', NEW_VM_UUID]), \
                patch.object(demo, 'guest_preflight', side_effect=RuntimeError('stop')) as preflight, \
                self.assertRaisesRegex(RuntimeError, 'stop'):
            demo.main()
        preflight.assert_called_once_with(Path.home() / 'csattt-lab', NEW_VM_UUID)


if __name__ == '__main__':
    unittest.main()
