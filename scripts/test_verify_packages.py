"""Regression checks for invalid downloads, corruption and checksum drift."""

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

SPEC = importlib.util.spec_from_file_location("verify_packages", Path(__file__).with_name("verify_packages.py"))
verifier = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(verifier)


class PackageVerificationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / "package").mkdir()
        self.package = self.root / "package" / "test.zip"
        self.checksums = self.root / "SHA256SUMS"
        self.make_zip(self.package)
        self.enterContext(patch.object(verifier, "ROOT", self.root))
        self.enterContext(patch.object(verifier, "CHECKSUMS", self.checksums))
        self.enterContext(redirect_stdout(io.StringIO()))
        verifier.verify(write_checksums=True)

    @staticmethod
    def make_zip(path, payload=b"translation-library-fixture"):
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_STORED) as archive:
            archive.writestr("system/lib/libhoudini.so", payload)

    def test_valid_package(self):
        verifier.verify()

    def test_changed_package_fails_hash_check(self):
        self.make_zip(self.package, b"different-library")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verifier.verify()

    def test_missing_and_unlisted_packages_fail(self):
        extra = self.package.with_name("extra.zip")
        self.make_zip(extra)
        with self.assertRaisesRegex(ValueError, "unlisted=.*extra.zip"):
            verifier.verify()
        extra.unlink()
        self.package.unlink()
        self.make_zip(extra)
        with self.assertRaisesRegex(ValueError, "missing=.*test.zip"):
            verifier.verify()

    def test_duplicate_or_malformed_checksum_fails(self):
        original = self.checksums.read_text()
        for content, message in ((original * 2, "duplicate"), ("invalid\n", "malformed")):
            with self.subTest(content=content):
                self.checksums.write_text(content)
                with self.assertRaisesRegex(ValueError, message):
                    verifier.verify()

    def test_html_disguised_as_zip_cannot_replace_baseline(self):
        original = self.checksums.read_bytes()
        self.package.write_bytes(b"<!DOCTYPE html><html>download page</html>")
        with self.assertRaises(zipfile.BadZipFile):
            verifier.verify(write_checksums=True)
        self.assertEqual(original, self.checksums.read_bytes())

    def test_crc_corruption_cannot_replace_baseline(self):
        original = self.checksums.read_bytes()
        data = self.package.read_bytes().replace(b"translation-library-fixture", b"Translation-library-fixture", 1)
        self.package.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "corrupt member"):
            verifier.verify(write_checksums=True)
        self.assertEqual(original, self.checksums.read_bytes())

    def test_zip_without_core_library_fails(self):
        with zipfile.ZipFile(self.package, "w") as archive:
            archive.writestr("README.txt", "wrong download")
        with self.assertRaisesRegex(ValueError, "missing core"):
            verifier.verify(write_checksums=True)

    def test_empty_inventory_fails(self):
        self.package.unlink()
        with self.assertRaisesRegex(ValueError, "no packages"):
            verifier.verify()


if __name__ == "__main__":
    unittest.main()
