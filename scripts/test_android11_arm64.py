"""Offline tests; generated shell scripts operate only on temporary fixtures."""

from contextlib import redirect_stdout
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location('android11_arm64', Path(__file__).with_name('android11_arm64.py'))
bridge = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bridge)
SYSTEM = 'ro.build.version.sdk=30\nro.product.cpu.abi=x86_64\nro.genymotion.version=3.6.0\n'


class Arm64Tests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.enterContext(redirect_stdout(io.StringIO()))
        self.payload = self.root / 'system.zip'
        self.profile = {'id': 'fixture', 'elf_files': {}}
        with zipfile.ZipFile(self.payload, 'w') as archive:
            for name, elf_class, machine in (
                ('system/lib/libhoudini.so', 1, 3),
                ('system/lib64/libhoudini.so', 2, 62),
            ):
                data = bytearray(64)
                data[:6] = b'\x7fELF' + bytes((elf_class, 1))
                struct.pack_into('<H', data, 18, machine)
                archive.writestr(name, data)
                self.profile['elf_files'][name] = {
                    'class': elf_class, 'machine': machine,
                    'sha256': hashlib.sha256(data).hexdigest(),
                }
        self.profile['size_bytes'] = self.payload.stat().st_size
        self.profile['sha256'] = bridge.sha256(self.payload)

    def test_property_replacement_is_idempotent_and_preserves_unrelated_lines(self):
        text = SYSTEM + '# comment\nkeep = original\nro.zygote=zygote64\nro.zygote=zygote32\n'
        result = bridge.patch_properties(text)
        self.assertEqual(result, bridge.patch_properties(result))
        self.assertIn('# comment\nkeep = original\n', result)
        for key, value in bridge.PROPERTIES.items():
            self.assertEqual(result.count('\n' + key + '='), 1)
            self.assertEqual(bridge.properties(result)[key], value)

    def test_device_rejects_wrong_android_arch_identity_and_bridge(self):
        values = bridge.properties(SYSTEM)
        bridge.validate_device(values, 'x86_64')
        for update, arch in (({'ro.build.version.sdk': '29'}, 'x86_64'),
                             ({'ro.build.version.sdk': '31'}, 'x86_64'),
                             ({}, 'aarch64'), ({}, 'i686'),
                             ({'ro.genymotion.version': ''}, 'x86_64'),
                             ({'ro.dalvik.vm.native.bridge': 'libndk_translation.so'}, 'x86_64')):
            with self.subTest(update=update, arch=arch), self.assertRaises(ValueError):
                bridge.validate_device(dict(values, **update), arch)

    def test_pinned_payload_and_elf_checks(self):
        bridge.validate_payload(self.payload, self.profile)
        changed = copy.deepcopy(self.profile)
        changed['elf_files']['system/lib64/libhoudini.so']['machine'] = 183
        with self.assertRaisesRegex(ValueError, 'core ELF'):
            bridge.validate_payload(self.payload, changed)
        self.payload.write_bytes(b'<!DOCTYPE html>download error')
        with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
            bridge.validate_payload(self.payload, self.profile)

    def test_prepare_preserves_original_bytes_and_refuses_existing_output(self):
        system = self.root / 'system.prop'
        vendor = self.root / 'vendor.prop'
        system.write_bytes(SYSTEM.replace('\n', '\r\n').encode())
        vendor.write_text('ro.vendor.product.cpu.abilist=x86_64,x86\n')
        output = self.root / 'bundle'
        bridge.prepare(self.payload, system, vendor, output, self.profile)
        self.assertEqual(system.read_bytes(), (output / 'system.original.prop').read_bytes())
        subprocess.run(['/bin/sh', '-n', str(output / 'apply.sh')], check=True)
        subprocess.run(['/bin/sh', '-n', str(output / 'restore-properties.sh')], check=True)
        with self.assertRaises(FileExistsError):
            bridge.prepare(self.payload, system, vendor, output, self.profile)

    def shell_fixture(self):
        records = []
        for label in ('system', 'vendor'):
            target = self.root / f'{label}.target'
            original = SYSTEM.encode()
            update = bridge.patch_properties(SYSTEM).encode()
            target.write_bytes(original)
            record = {'target': str(target)}
            for kind, data in (('original', original), ('patched', update)):
                path = self.root / f'{label}.{kind}.prop'
                path.write_bytes(data)
                record[kind] = str(path)
                record[kind + '_sha256'] = hashlib.sha256(data).hexdigest()
            records.append(record)
        commands = self.root / 'bin'
        commands.mkdir()
        stubs = {
            'id': '#!/bin/sh\necho 0\n',
            'uname': '#!/bin/sh\necho x86_64\n',
            'getprop': '#!/bin/sh\ncase "$1" in ro.build.version.sdk) echo 30;; ro.genymotion.version) echo 3.6.0;; esac\n',
            'sha256sum': f'#!{sys.executable}\nimport sys,hashlib\nprint(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest()+"  "+sys.argv[1])\n',
        }
        for name, source in stubs.items():
            script = commands / name
            script.write_text(source)
            script.chmod(0o755)
        env = dict(os.environ, PATH=str(commands) + os.pathsep + os.environ['PATH'])
        return records, env

    def run_shell(self, records, env, restore=False, core=None):
        script = self.root / ('restore.sh' if restore else 'apply.sh')
        script.write_text(bridge.shell_script(records, core or {}, restore))
        return subprocess.run(['/bin/sh', str(script)], env=env, capture_output=True, text=True)

    def test_generated_apply_and_restore_on_fixture_files(self):
        records, env = self.shell_fixture()
        for _ in range(2):
            result = self.run_shell(records, env)
            self.assertEqual(result.returncode, 0, result.stderr)
        for record in records:
            self.assertEqual(bridge.sha256(record['target']), record['patched_sha256'])
        result = self.run_shell(records, env, restore=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        for record in records:
            self.assertEqual(bridge.sha256(record['target']), record['original_sha256'])

    def test_changed_device_or_bundle_and_missing_payload_cause_no_writes(self):
        records, env = self.shell_fixture()
        first = Path(records[0]['target'])
        second = Path(records[1]['target'])
        second.write_text('different device')
        result = self.run_shell(records, env)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(bridge.sha256(first), records[0]['original_sha256'])
        second.write_bytes(Path(records[1]['original']).read_bytes())
        result = self.run_shell(records, env, core={str(self.root / 'missing.so'): '0' * 64})
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(bridge.sha256(first), records[0]['original_sha256'])
        Path(records[1]['patched']).write_text('corrupt bundle')
        self.assertNotEqual(self.run_shell(records, env).returncode, 0)
        self.assertEqual(bridge.sha256(first), records[0]['original_sha256'])

    def test_second_write_failure_restores_both_originals(self):
        records, env = self.shell_fixture()
        cat = self.root / 'bin' / 'cat'
        cat.write_text('#!/bin/sh\ncase "$1" in *vendor.patched.prop) exit 1;; esac\nexec /bin/cat "$@"\n')
        cat.chmod(0o755)
        result = self.run_shell(records, env)
        self.assertNotEqual(result.returncode, 0)
        for record in records:
            self.assertEqual(bridge.sha256(record['target']), record['original_sha256'])

    def test_download_validation_failure_leaves_no_final_or_partial_file(self):
        destination = self.root / 'download.zip'
        profile = dict(self.profile, url='https://example.invalid/system.zip')
        manifest = self.root / 'profile.json'
        manifest.write_text(json.dumps(profile))
        argv = ['android11_arm64.py', 'download', '--output', str(destination)]
        with patch.object(bridge, 'PROFILE', manifest), patch.object(sys, 'argv', argv):
            with patch.object(bridge.urllib.request, 'urlopen', return_value=io.BytesIO(b'HTML download error')):
                self.assertEqual(bridge.main(), 1)
            self.assertFalse(destination.exists())
            self.assertFalse(destination.with_name('download.zip.part').exists())
            with patch.object(bridge.urllib.request, 'urlopen', return_value=io.BytesIO(self.payload.read_bytes())):
                self.assertEqual(bridge.main(), 0)
            self.assertEqual(bridge.sha256(destination), profile['sha256'])

    def test_read_only_verifier_distinguishes_config_from_runtime(self):
        values = dict(bridge.properties(SYSTEM), **bridge.PROPERTIES)
        def fake_run(args, **kwargs):
            self.assertEqual(args[:4], ['adb', '-s', 'fixture-serial', 'shell'])
            command = args[4]
            if command.startswith('getprop '):
                answer = values[command.split()[1]]
            elif command == 'uname -m':
                answer = 'x86_64'
            elif command.startswith('sha256sum '):
                name = command.split()[1].lstrip('/')
                answer = self.profile['elf_files'][name]['sha256'] + '  /' + name
            else:
                self.fail('unexpected command: ' + command)
            return subprocess.CompletedProcess(args, 0, stdout=answer, stderr='')
        with patch.object(bridge.subprocess, 'run', side_effect=fake_run):
            self.assertEqual(bridge.verify_device('adb', 'fixture-serial', self.profile), 0)
            values['ro.zygote'] = 'zygote64'
            self.assertEqual(bridge.verify_device('adb', 'fixture-serial', self.profile), 1)


if __name__ == '__main__':
    unittest.main()
