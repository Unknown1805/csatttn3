"""Bounded synthetic-file operations and Compose controls; no daemon is started."""
from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/simulator'))
sys.path.insert(0, str(ROOT / 'scripts'))
import simulator as sim
import prepare_simulator_test as preparation


class Simulator(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='csattt-sim-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.data = self.root / 'data'
        self.data.mkdir()
        for n, name in enumerate(sim.NAMES, 1):
            (self.data / name).write_bytes(sim.expected_content(n))
        self.output = io.StringIO()
        self.redirect = redirect_stdout(self.output)
        self.redirect.__enter__()
        self.addCleanup(self.redirect.__exit__, None, None, None)
        self.stop = patch.object(sim, 'STOP_SIGNAL', None)
        self.stop.start()
        self.addCleanup(self.stop.stop)

    def snapshot(self):
        return {p.name: (p.lstat().st_mode, p.read_bytes() if p.is_file() else None)
                for p in self.data.iterdir()}

    def test_dry_run_changes_nothing(self):
        before = self.snapshot()
        self.assertEqual(sim.simulate(self.data), 0)
        self.assertEqual(self.snapshot(), before)
        events = [json.loads(line) for line in self.output.getvalue().splitlines()]
        self.assertEqual(events[-1]['event'], 'dry_run_complete')
        self.assertEqual(events[-1]['changed_files'], 0)

    def test_apply_only_renames_fifteen_files_and_adds_note(self):
        before = {p.name: p.read_bytes() for p in self.data.iterdir()}
        with patch.object(sim.time, 'sleep'):
            self.assertEqual(sim.simulate(self.data, apply=True), 0)
        self.assertEqual(set(p.name for p in self.data.iterdir()),
                         {n + sim.SUFFIX for n in sim.NAMES} | {sim.NOTE})
        for name, data in before.items():
            self.assertEqual((self.data / (name + sim.SUFFIX)).read_bytes(), data)
        self.assertIn('SAFE SIMULATION ONLY', (self.data / sim.NOTE).read_text())

    def test_rerun_refused_without_resetting_partial_or_completed_state(self):
        with patch.object(sim.time, 'sleep'):
            self.assertEqual(sim.simulate(self.data, apply=True), 0)
        before = self.snapshot()
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertEqual(self.snapshot(), before)

    def test_changed_content_rejected_before_any_mutation(self):
        (self.data / sim.NAMES[-1]).write_bytes(b'private data')
        before = self.snapshot()
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.data / sim.NOTE).exists())

    def test_equal_size_wrong_content_rejected(self):
        (self.data / sim.NAMES[-1]).write_bytes(b'X' * len(sim.expected_content(15)))
        before = self.snapshot()
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertEqual(self.snapshot(), before)

    def test_extra_and_existing_target_refused_without_overwrite(self):
        target = self.data / (sim.NAMES[0] + sim.SUFFIX)
        target.write_bytes(b'keep existing target')
        before = self.snapshot()
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertEqual(self.snapshot(), before)

    def test_symlink_file_does_not_change_external_file(self):
        outside = self.root / 'outside'
        outside.write_bytes(sim.expected_content(1))
        (self.data / sim.NAMES[0]).unlink()
        (self.data / sim.NAMES[0]).symlink_to(outside)
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertEqual(outside.read_bytes(), sim.expected_content(1))
        self.assertTrue((self.data / sim.NAMES[0]).is_symlink())
        self.assertFalse((self.data / sim.NOTE).exists())

    def test_symlink_directory_refused(self):
        link = self.root / 'link'
        link.symlink_to(self.data, target_is_directory=True)
        before = self.snapshot()
        self.assertEqual(sim.simulate(link, apply=True), 1)
        self.assertEqual(self.snapshot(), before)

    def test_hardlink_and_subdirectory_refused(self):
        outside = self.root / 'outside'
        os.link(self.data / sim.NAMES[0], outside)
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertFalse((self.data / sim.NOTE).exists())
        outside.unlink()
        (self.data / sim.NAMES[0]).unlink()
        (self.data / sim.NAMES[0]).mkdir()
        self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertFalse((self.data / sim.NOTE).exists())

    def test_second_instance_cannot_lock_the_same_dataset(self):
        with sim.data_directory(self.data):
            before = self.snapshot()
            self.assertEqual(sim.simulate(self.data, apply=True), 1)
            self.assertEqual(self.snapshot(), before)

    def test_atomic_rename_never_overwrites_a_destination(self):
        with sim.data_directory(self.data) as directory:
            (self.data / 'destination').write_bytes(b'keep')
            with self.assertRaises(FileExistsError):
                sim.rename_noreplace()(directory, sim.NAMES[0], 'destination')
        self.assertEqual((self.data / 'destination').read_bytes(), b'keep')
        self.assertEqual((self.data / sim.NAMES[0]).read_bytes(), sim.expected_content(1))

    def test_stop_preserves_partial_state_and_never_rolls_back(self):
        def stop_after_first(seconds):
            sim.request_stop(signal.SIGTERM, None)
        with patch.object(sim.time, 'sleep', side_effect=stop_after_first):
            self.assertEqual(sim.simulate(self.data, apply=True), 143)
        self.assertTrue((self.data / (sim.NAMES[0] + sim.SUFFIX)).is_file())
        self.assertEqual((self.data / (sim.NAMES[0] + sim.SUFFIX)).read_bytes(), sim.expected_content(1))
        self.assertTrue(all((self.data / n).is_file() for n in sim.NAMES[1:]))
        self.assertEqual(json.loads(self.output.getvalue().splitlines()[-1])['event'], 'stopped')

    def test_change_mid_run_stops_before_renaming_the_changed_file(self):
        def change_source(seconds):
            (self.data / sim.NAMES[1]).write_bytes(b'X' * len(sim.expected_content(2)))
        with patch.object(sim.time, 'sleep', side_effect=change_source):
            self.assertEqual(sim.simulate(self.data, apply=True), 1)
        self.assertTrue((self.data / (sim.NAMES[0] + sim.SUFFIX)).is_file())
        self.assertFalse((self.data / (sim.NAMES[1] + sim.SUFFIX)).exists())

    def test_preparation_copies_only_synthetic_data_and_never_overwrites(self):
        probe = self.root / 'probe'
        probe.mkdir()
        env = self.root / 'simulator-test.env'
        before = self.snapshot()
        target = preparation.prepare(self.data, probe, env)
        self.assertEqual(self.snapshot(), before)
        self.assertEqual({p.name: p.read_bytes() for p in target.iterdir()},
                         {p.name: p.read_bytes() for p in self.data.iterdir()})
        self.assertEqual(env.stat().st_mode & 0o777, 0o600)
        self.assertIn(str(target), env.read_text())
        with self.assertRaises(RuntimeError):
            preparation.prepare(self.data, probe, env)
        self.assertEqual(len(list(probe.iterdir())), 1)

    def test_preparation_refuses_overlapping_or_symlink_paths(self):
        with self.assertRaises(RuntimeError):
            preparation.prepare(self.data, self.data, self.root / 'simulator-test.env')
        probe = self.root / 'probe'
        probe.mkdir()
        link = self.root / 'link'
        link.symlink_to(probe, target_is_directory=True)
        with self.assertRaises(RuntimeError):
            preparation.prepare(self.data, link, self.root / 'simulator-test.env')

    def test_cli_defaults_to_dry_run_on_fixed_container_path(self):
        with patch.object(sys, 'argv', ['simulator.py']), patch.object(sim.os, 'geteuid', return_value=1000), \
                patch.object(sim.signal, 'signal'), patch.object(sim, 'simulate', return_value=0) as run:
            self.assertEqual(sim.main(), 0)
        run.assert_called_once_with(Path('/lab/data'), apply=False)

    def test_cli_apply_is_explicit_and_root_is_refused(self):
        with patch.object(sys, 'argv', ['simulator.py', '--apply']), patch.object(sim.os, 'geteuid', return_value=1000), \
                patch.object(sim.signal, 'signal'), patch.object(sim, 'simulate', return_value=0) as run:
            self.assertEqual(sim.main(), 0)
        run.assert_called_once_with(Path('/lab/data'), apply=True)
        with patch.object(sys, 'argv', ['simulator.py', '--apply']), patch.object(sim.os, 'geteuid', return_value=0), \
                patch.object(sim, 'simulate') as run:
            with self.assertRaisesRegex(SystemExit, 'non-root'):
                sim.main()
        run.assert_not_called()


class SimulatorCompose(unittest.TestCase):
    def test_runtime_permissions_and_scope(self):
        model = json.loads(subprocess.check_output([
            'docker', 'compose', '--env-file', str(ROOT / 'lab/.env.simulator.example'),
            '--profile', 'incident', '-f', str(ROOT / 'lab/compose.yaml'),
            '-f', str(ROOT / 'lab/compose.incident.yaml'), 'config', '--format', 'json'], text=True))
        s = model['services']['simulator']
        self.assertEqual(s['image'], model['services']['workstation']['image'])
        self.assertEqual(s['pull_policy'], 'never')
        self.assertEqual(s['entrypoint'], ['python', '/app/simulator.py'])
        self.assertEqual(s['command'], [])
        self.assertEqual(s['user'], '1000:1000')
        self.assertTrue(s['read_only'])
        self.assertEqual(s['cap_drop'], ['ALL'])
        self.assertIn('no-new-privileges:true', s['security_opt'])
        self.assertEqual(s['restart'], 'no')
        self.assertFalse(s.get('privileged', False))
        self.assertFalse(s.get('ports'))
        self.assertEqual(s['profiles'], ['incident'])
        self.assertEqual(set(s['networks']), {'incident_net'})
        self.assertTrue(model['networks']['incident_net']['internal'])
        self.assertEqual(len(s['volumes']), 2)
        mounts = {v['target']: v for v in s['volumes']}
        self.assertFalse(mounts['/lab/data'].get('read_only', False))
        self.assertTrue(mounts['/app/simulator.py']['read_only'])
        for volume in s['volumes']:
            self.assertFalse(volume['bind'].get('create_host_path', False))
            self.assertNotIn('secrets', volume['source'])
            self.assertNotIn('docker.sock', volume['source'])
            self.assertNotIn('backup', volume['source'])


if __name__ == '__main__':
    unittest.main()
