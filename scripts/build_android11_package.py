#!/usr/bin/env python3
"""Bundle a verified native bridge payload and offline configuration tools."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from android11_arm64 import PROFILE, ROOT, sha256, validate_payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--payload', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', type=Path, default=PROFILE)
    parser.add_argument('--install-guide', type=Path, default=ROOT / 'package/android11/INSTALL.md')
    parser.add_argument('--notices', type=Path, default=ROOT / 'package/android11/THIRD_PARTY_NOTICES.md')
    args = parser.parse_args()
    try:
        profile = json.loads(args.profile.read_text(encoding='utf-8'))
        validate_payload(args.payload, profile)
        files = {
            'system.zip': args.payload,
            'scripts/android11_arm64.py': ROOT / 'scripts/android11_arm64.py',
            'config/' + args.profile.name: args.profile,
            'LICENSE': ROOT / 'LICENSE',
            'INSTALL.md': args.install_guide,
            'THIRD_PARTY_NOTICES.md': args.notices,
        }
        if profile.get('native_bridge') == 'libndk_translation.so':
            files['scripts/native_bridge.py'] = ROOT / 'scripts/native_bridge.py'
        hashes = {name: sha256(path) for name, path in files.items()}
        with zipfile.ZipFile(args.output, 'x', compression=zipfile.ZIP_STORED) as bundle:
            for name, path in files.items():
                bundle.write(path, name)
            bundle.writestr('SHA256SUMS', ''.join(f'{digest}  {name}\n' for name, digest in hashes.items()))
        with zipfile.ZipFile(args.output) as bundle:
            if bundle.testzip() is not None:
                raise ValueError('package ZIP integrity failed')
            for name, expected in hashes.items():
                digest = hashlib.sha256()
                with bundle.open(name) as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                        digest.update(chunk)
                if digest.hexdigest() != expected:
                    raise ValueError(f'packaged file changed: {name}')
        print(f'Package: {args.output}\nBytes: {args.output.stat().st_size}\nSHA-256: {sha256(args.output)}')
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
