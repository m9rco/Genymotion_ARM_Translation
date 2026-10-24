#!/usr/bin/env python3
"""Check package inventory, SHA-256 and ZIP CRCs without executing payloads."""

import argparse
import hashlib
from pathlib import Path
import re
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CHECKSUMS = ROOT / "SHA256SUMS"
ENTRY = re.compile(r"([0-9a-f]{64})  (package/(?:[A-Za-z0-9_-][A-Za-z0-9_.-]*/)*[A-Za-z0-9_-][A-Za-z0-9_.-]*\.zip)")


def package_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_archive(path):
    with zipfile.ZipFile(path) as archive:
        if not archive.infolist():
            raise ValueError(f"{path.name}: empty archive")
        broken = archive.testzip()
        if broken is not None:
            raise ValueError(f"{path.name}: corrupt member {broken}")
        if not {'system/lib/libhoudini.so', 'system/lib64/libndk_translation.so'}.intersection(archive.namelist()):
            raise ValueError(f"{path.name}: missing core translation library")


def verify(write_checksums=False):
    packages = sorted((ROOT / "package").rglob("*.zip"))
    if not packages:
        raise ValueError("no packages found")
    if any(not path.is_file() or path.is_symlink() for path in packages):
        raise ValueError("packages must be regular files, not symlinks")
    actual = {path.relative_to(ROOT).as_posix(): package_hash(path) for path in packages}
    if not write_checksums:
        expected = {}
        for number, line in enumerate(CHECKSUMS.read_text(encoding="utf-8").splitlines(), 1):
            match = ENTRY.fullmatch(line)
            if match is None:
                raise ValueError(f"SHA256SUMS:{number}: malformed entry")
            digest, name = match.groups()
            if name in expected:
                raise ValueError(f"SHA256SUMS:{number}: duplicate entry {name}")
            expected[name] = digest
        if expected.keys() != actual.keys():
            raise ValueError(
                f"package inventory mismatch: missing={sorted(expected.keys() - actual.keys())}, "
                f"unlisted={sorted(actual.keys() - expected.keys())}"
            )
        for name, digest in actual.items():
            if expected[name] != digest:
                raise ValueError(f"{name}: SHA-256 mismatch")
    for path in packages:
        check_archive(path)
        hash_status = "SHA-256 computed" if write_checksums else "SHA-256 matched"
        print(f"OK {path.relative_to(ROOT)} ({hash_status}, ZIP CRC, core library)")
    if write_checksums:
        CHECKSUMS.write_text(
            "".join(f"{digest}  {name}\n" for name, digest in actual.items()),
            encoding="utf-8",
        )
        print("Updated SHA256SUMS; review the diff before committing.")
    print(f"Verified {len(packages)} archives. Runtime compatibility is not tested.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-checksums", action="store_true", help="validate ZIPs and regenerate hashes")
    args = parser.parse_args()
    try:
        verify(args.write_checksums)
    except (OSError, ValueError, zipfile.BadZipFile, RuntimeError, NotImplementedError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
