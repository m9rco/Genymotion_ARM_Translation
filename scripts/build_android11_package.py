#!/usr/bin/env python3
"""Bundle the verified Android 11 payload and offline configuration tools."""

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
    args = parser.parse_args()
    try:
        validate_payload(args.payload, json.loads(PROFILE.read_text(encoding='utf-8')))
        files = {
            'system.zip': args.payload,
            'scripts/android11_arm64.py': ROOT / 'scripts/android11_arm64.py',
            'config/android11-arm64.json': PROFILE,
            'LICENSE': ROOT / 'LICENSE',
            'INSTALL.md': ROOT / 'package/android11/INSTALL.md',
            'THIRD_PARTY_NOTICES.md': ROOT / 'package/android11/THIRD_PARTY_NOTICES.md',
        }
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
