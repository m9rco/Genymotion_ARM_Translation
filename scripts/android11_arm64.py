#!/usr/bin/env python3
"""Prepare an experimental Android 11 x86_64 ARM bridge; never flashes a device."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import shutil
import struct
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'config/android11-arm64.json'
TARGETS = ('/system/build.prop', '/system/vendor/build.prop')
PROPERTIES = {
    **{f'{prefix}.cpu.abilist{suffix}': value
       for prefix in ('ro.product', 'ro.vendor.product', 'ro.odm.product')
       for suffix, value in (
           ('', 'x86_64,x86,arm64-v8a,armeabi-v7a,armeabi'),
           ('32', 'x86,armeabi-v7a,armeabi'), ('64', 'x86_64,arm64-v8a'))},
    'ro.dalvik.vm.native.bridge': 'libhoudini.so',
    'ro.enable.native.bridge.exec': '1',
    'ro.enable.native.bridge.exec64': '1',
    'ro.dalvik.vm.isa.arm': 'x86',
    'ro.dalvik.vm.isa.arm64': 'x86_64',
    'ro.zygote': 'zygote64_32',
}
BEGIN = '# BEGIN Genymotion ARM64 experimental configuration'
END = '# END Genymotion ARM64 experimental configuration'


def sha256(path):
    with Path(path).open('rb') as stream:
        digest = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def properties(text):
    result = {}
    for line in text.splitlines():
        match = re.match(r'^\s*([^#\s=]+)\s*=(.*)$', line)
        if match:
            result[match[1]] = match[2].strip()
    return result


def patch_properties(text):
    """Replace every managed occurrence, preserving unrelated lines and comments."""
    if '\x00' in text:
        raise ValueError('NUL in property file')
    kept = []
    for line in text.splitlines():
        key = line.split('=', 1)[0].strip()
        if line in (BEGIN, END) or key in PROPERTIES:
            continue
        kept.append(line)
    return '\n'.join(kept).rstrip() + '\n\n' + BEGIN + '\n' + ''.join(
        f'{key}={value}\n' for key, value in PROPERTIES.items()) + END + '\n'


def validate_device(values, machine):
    if values.get('ro.build.version.sdk') != '30' or machine != 'x86_64':
        raise ValueError('requires Android 11 / API 30 with an x86_64 guest kernel')
    if not values.get('ro.genymotion.version'):
        raise ValueError('missing Genymotion identity')
    if values.get('ro.product.cpu.abi') not in ('', None, 'x86_64'):
        raise ValueError('requires an x86_64 guest ABI, not ARM64 or 32-bit x86')
    bridge = values.get('ro.dalvik.vm.native.bridge', '')
    if bridge not in ('', '0', 'libhoudini.so'):
        raise ValueError(f'conflicting native bridge: {bridge}')


def validate_payload(path, profile):
    if Path(path).stat().st_size != profile['size_bytes'] or sha256(path) != profile['sha256']:
        raise ValueError('payload size/SHA-256 mismatch; only the pinned upstream release is accepted')
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('duplicate ZIP entries')
        for name in names:
            parts = PurePosixPath(name)
            if parts.is_absolute() or '..' in parts.parts or '\\' in name:
                raise ValueError('unsafe ZIP member path')
        if archive.testzip() is not None:
            raise ValueError('corrupt payload CRC')
        for name, expected in profile['elf_files'].items():
            data = archive.read(name)
            if (data[:4] != b'\x7fELF' or data[4] != expected['class'] or data[5] != 1
                    or struct.unpack_from('<H', data, 18)[0] != expected['machine']
                    or hashlib.sha256(data).hexdigest() != expected['sha256']):
                raise ValueError(f'unexpected core ELF: {name}')


def shell_script(records, core_hashes, restore=False):
    """Generate guarded on-device scripts; no remount, flashing or reboot."""
    quote = shlex.quote
    lines = ['#!/system/bin/sh', 'set -eu', 'cd "$(dirname "$0")"',
             'die() { echo "$*" >&2; exit 1; }',
             'hash() { sha256sum "$1" | cut -d " " -f 1; }',
             '[ "$(id -u)" = 0 ] || die "Run as root"',
             '[ "$(getprop ro.build.version.sdk)" = 30 ] || die "Android 11 required"',
             '[ "$(uname -m)" = x86_64 ] || die "x86_64 guest required"',
             '[ -n "$(getprop ro.genymotion.version)" ] || die "Genymotion required"']
    for record in records:
        for field in ('original', 'patched'):
            lines.append(f'[ "$(hash {quote(record[field])})" = {quote(record[field + "_sha256"])} ] || die "Bundle file changed"')
        target = quote(record['target'])
        lines += [f'current=$(hash {target})',
                  f'[ "$current" = {record["original_sha256"]} ] || [ "$current" = {record["patched_sha256"]} ] || die "Device properties differ from this backup"']
    if not restore:
        for target, digest in core_hashes.items():
            lines.append(f'[ "$(hash {quote(target)})" = {digest} ] || die "Flash the verified payload first"')
    # Both input files and both target files are validated before any target write.
    lines += ['rollback() {', '  failed=0']
    for record in records:
        lines.append(f'  cat {quote(record["original"])} > {quote(record["target"])} || failed=1')
    lines += ['  [ "$failed" = 0 ] || echo "Property restore failed; use the host backup or recreate the device" >&2', '}',
              'committed=0', 'trap \'[ "$committed" = 1 ] || rollback\' EXIT',
              "trap 'exit 1' HUP INT TERM"]
    for record in records:
        source = record['original' if restore else 'patched']
        lines.append(f'cat {quote(source)} > {quote(record["target"])}')
    for record in records:
        expected = record['original_sha256' if restore else 'patched_sha256']
        lines.append(f'[ "$(hash {quote(record["target"])})" = {expected} ] || die "Write verification failed"')
    lines += ['committed=1', 'echo "Properties written and verified. Reboot manually. Runtime is not tested."']
    return '\n'.join(lines) + '\n'


def prepare(payload, system_prop, vendor_prop, output, profile):
    validate_payload(payload, profile)
    originals = [Path(system_prop).read_bytes(), Path(vendor_prop).read_bytes()]
    texts = [data.decode('utf-8') for data in originals]
    system_values = properties(texts[0])
    # Kernel architecture is checked again on-device before applying.
    validate_device(system_values, 'x86_64')
    for text in texts:
        bridge = properties(text).get('ro.dalvik.vm.native.bridge', '')
        if bridge not in ('', '0', 'libhoudini.so'):
            raise ValueError('conflicting bridge in property file')
    patched = [patch_properties(text).encode('utf-8') for text in texts]
    output = Path(output)
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    records = []
    for label, target, original, update in zip(('system', 'vendor'), TARGETS, originals, patched):
        record = {'target': target}
        for kind, data in (('original', original), ('patched', update)):
            filename = f'{label}.{kind}.prop'
            (output / filename).write_bytes(data)
            record[kind] = filename
            record[kind + '_sha256'] = hashlib.sha256(data).hexdigest()
        records.append(record)
    core = {'/' + name: info['sha256'] for name, info in profile['elf_files'].items()}
    (output / 'apply.sh').write_text(shell_script(records, core), encoding='utf-8')
    (output / 'restore-properties.sh').write_text(shell_script(records, core, restore=True), encoding='utf-8')
    (output / 'manifest.json').write_text(json.dumps({
        'profile': profile['id'], 'status': 'experimental-runtime-unverified',
        'payload_sha256': profile['sha256'], 'properties': records,
    }, indent=2) + '\n', encoding='utf-8')
    print(f'Prepared {output}; original properties preserved. No device was modified.')


def verify_device(adb, serial, profile):
    def shell(command):
        return subprocess.run([adb, '-s', serial, 'shell', command], check=True,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30).stdout.strip()
    values = {key: shell('getprop ' + key) for key in (
        'ro.build.version.sdk', 'ro.genymotion.version', 'ro.product.cpu.abi', *PROPERTIES)}
    validate_device(values, shell('uname -m'))
    failures = [key for key, expected in PROPERTIES.items() if values[key] != expected]
    for name, expected in profile['elf_files'].items():
        if shell('sha256sum /' + name).split()[0] != expected['sha256']:
            failures.append(name)
    print(json.dumps({'configuration_matches': not failures, 'failed_checks': failures,
                      'runtime_tested': False, 'properties': values}, indent=2))
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    download = commands.add_parser('download', help='fetch and verify the pinned third-party ZIP')
    download.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('check-payload')
    check.add_argument('payload', type=Path)
    bundle = commands.add_parser('prepare', help='create property backups and guarded scripts locally')
    bundle.add_argument('--payload', type=Path, required=True)
    bundle.add_argument('--system-prop', type=Path, required=True)
    bundle.add_argument('--vendor-prop', type=Path, required=True)
    bundle.add_argument('--output', type=Path, required=True)
    verify = commands.add_parser('verify', help='read-only ADB configuration checks, not a runtime test')
    verify.add_argument('--serial', required=True)
    verify.add_argument('--adb', default='adb')
    args = parser.parse_args()
    try:
        profile = json.loads(PROFILE.read_text(encoding='utf-8'))
        if args.command == 'download':
            if args.output.exists():
                raise ValueError('output already exists')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            partial = args.output.with_name(args.output.name + '.part')
            with partial.open('xb') as target:
                try:
                    with urllib.request.urlopen(profile['url'], timeout=60) as source:
                        shutil.copyfileobj(source, target)
                except Exception:
                    partial.unlink(missing_ok=True)
                    raise
            try:
                validate_payload(partial, profile)
                partial.rename(args.output)
            finally:
                partial.unlink(missing_ok=True)
            print(f'Verified payload saved to {args.output}')
        elif args.command == 'check-payload':
            validate_payload(args.payload, profile)
            print('Pinned SHA-256, ZIP CRCs and core ELF headers verified; runtime untested.')
        elif args.command == 'prepare':
            prepare(args.payload, args.system_prop, args.vendor_prop, args.output, profile)
        else:
            return verify_device(args.adb, args.serial, profile)
    except (OSError, ValueError, KeyError, IndexError, zipfile.BadZipFile,
            subprocess.SubprocessError, RuntimeError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
