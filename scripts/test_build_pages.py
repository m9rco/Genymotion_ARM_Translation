"""Verify that the public site uses the right artifacts, hashes and missing states."""

from contextlib import redirect_stdout
from html.parser import HTMLParser
import importlib.util
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location('build_pages', Path(__file__).with_name('build_pages.py'))
site = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(site)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.downloads = []

    def handle_starttag(self, tag, attributes):
        values = dict(attributes)
        if tag == 'a' and 'download' in values.get('class', '').split():
            self.downloads.append(values['href'])


class SiteTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.directory = Path(tmp.name)
        self.enterContext(redirect_stdout(io.StringIO()))

    def fixture(self):
        root = self.directory / 'fixture'
        for name in ('package/catalog.json', 'SHA256SUMS', 'package/android11/SHA256SUMS', 'package/android12-14/PACKAGE_SHA256SUMS'):
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(site.ROOT / name, target)
        data = json.loads((root / 'package/catalog.json').read_text())
        for row in data['packages']:
            if row.get('path'):
                target = root / row['path']
                target.parent.mkdir(parents=True, exist_ok=True)
                target.touch()
        return root, data

    def test_static_content_contains_all_downloads_without_javascript(self):
        output = self.directory / 'site'
        site.build(output, ref='a' * 40)
        data = json.loads((output / 'downloads.json').read_text())
        self.assertEqual(len(data['packages']), 10)
        self.assertEqual(data['missing_versions'], ['8.1', '10', '15', '16+'])
        parser = Links()
        parser.feed((output / 'index.html').read_text())
        self.assertEqual(set(parser.downloads), {row['url'] for row in data['packages']})
        self.assertEqual(len(parser.downloads), 10)
        self.assertTrue((output / '.nojekyll').is_file())
        self.assertEqual({p.name for p in output.iterdir()}, {'index.html', 'style.css', 'app.js', '.nojekyll', 'downloads.json'})
        self.assertLess(sum(p.stat().st_size for p in output.iterdir()), 100_000)

    def test_grouping_and_checksum_match_the_actual_download(self):
        _, rows, _ = site.load_downloads(site.ROOT, 'm9rco/Genymotion_ARM_Translation', 'b' * 40)
        shared = next(row for row in rows if '12' in row['versions'])
        self.assertEqual(shared['versions'], ['12', '12.1', '13', '14'])
        self.assertEqual(shared['sha256'], site.checksum(site.ROOT / 'package/android12-14/PACKAGE_SHA256SUMS', shared['filename']))
        self.assertNotEqual(shared['sha256'], json.loads((site.ROOT / 'config/libndk-android12-14-arm64.json').read_text())['sha256'])
        seven = next(row for row in rows if '7.0' in row['versions'])
        self.assertEqual(seven['versions'], ['7.0', '7.1'])
        self.assertIn('/' + 'b' * 40 + '/package/', seven['url'])

    def test_missing_version_cannot_silently_gain_a_download(self):
        root, data = self.fixture()
        next(row for row in data['packages'] if row['status'] == 'missing')['url'] = 'https://github.com/fake.zip'
        (root / 'package/catalog.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'Missing version has a download'):
            site.load_downloads(root, 'm9rco/Genymotion_ARM_Translation', 'master')

    def test_catalog_hash_drift_and_unsafe_urls_are_rejected(self):
        root, data = self.fixture()
        data['packages'][0]['sha256'] = '0' * 64
        (root / 'package/catalog.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'checksum differs'):
            site.load_downloads(root, 'm9rco/Genymotion_ARM_Translation', 'master')
        for url in ('javascript:alert(1)', 'http://github.com/file.zip', 'https://github.com.evil.invalid/file.zip'):
            with self.assertRaises(ValueError):
                site.safe_url(url)

    def test_builder_cannot_overwrite_sources(self):
        for output in (site.ROOT, site.ROOT.parent, site.ROOT / 'site', site.ROOT / 'site/subdirectory'):
            with self.subTest(output=output), self.assertRaises(ValueError):
                site.build(output)


if __name__ == '__main__':
    unittest.main()
