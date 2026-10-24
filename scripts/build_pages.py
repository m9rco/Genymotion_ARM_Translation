#!/usr/bin/env python3
"""Build a dependency-free GitHub Pages download page from the package catalog."""

import argparse
import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


def checksum(path, filename):
    for line in path.read_text(encoding='utf-8').splitlines():
        digest, name = line.split('  ', 1)
        if name == filename and re.fullmatch('[0-9a-f]{64}', digest):
            return digest
    raise ValueError(f'No checksum for {filename} in {path}')


def safe_url(url):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or parsed.netloc not in ('github.com', 'raw.githubusercontent.com'):
        raise ValueError(f'Unexpected download URL: {url}')
    return url


def load_downloads(root, repository, ref):
    catalog = json.loads((root / 'package/catalog.json').read_text(encoding='utf-8'))
    groups, missing = {}, []
    source = f'https://github.com/{repository}/blob/{quote(ref, safe="")}/'
    raw = f'https://raw.githubusercontent.com/{repository}/{quote(ref, safe="")}/'
    for entry in catalog['packages']:
        version = entry['android']
        if entry['status'] == 'missing':
            if entry.get('url') or entry.get('path'):
                raise ValueError(f'Missing version has a download: {version}')
            missing.append(version)
            continue
        experimental = entry['status'].startswith('experimental-')
        if entry.get('url'):
            url = safe_url(entry['url'])
            filename = urlsplit(url).path.rsplit('/', 1)[-1]
            directory = 'android12-14' if entry.get('profile') else 'android11'
            sums = 'PACKAGE_SHA256SUMS' if directory == 'android12-14' else 'SHA256SUMS'
            digest = checksum(root / 'package' / directory / sums, filename)
            guide = source + f'package/{directory}/INSTALL.md'
        else:
            path = entry['path']
            if not path.startswith('package/') or '..' in Path(path).parts or not (root / path).is_file():
                raise ValueError(f'Invalid package path: {path}')
            digest = checksum(root / 'SHA256SUMS', path)
            if entry.get('sha256') != digest:
                raise ValueError(f'Catalog checksum differs for {version}')
            filename = Path(path).name
            url = raw + quote(path, safe='/')
            guide = source + 'README.md#install-on-a-legacy-x86-image'
        group = groups.setdefault(url, {
            'versions': [], 'url': url, 'filename': filename, 'sha256': digest,
            'guide': guide, 'kind': 'experimental' if experimental else 'legacy',
            'abi': 'arm64' if experimental else 'armv7',
        })
        if group['sha256'] != digest:
            raise ValueError('Shared download has conflicting checksums')
        group['versions'].append(version)
    rows = list(groups.values())
    rows.sort(key=lambda row: tuple(int(part) for part in row['versions'][0].split('.')), reverse=True)
    return catalog['reviewed'], rows, missing


def card(row):
    esc = html.escape
    versions = row['versions']
    shared = len(versions) > 1
    modern = row['kind'] == 'experimental'
    title = '12–14' if modern and shared else ' / '.join(versions)
    abi = 'ARM64 + ARMv7' if modern and not shared else ('ARM64' if modern else 'ARMv7 · 32-bit')
    note = ('12 / 12.1 / 13 / 14 共用上游文件，仅 ARM64。' if modern and shared
            else '包含转译库与配置工具，解压后按说明安装。' if modern
            else '7.0 / 7.1 共用历史 7.X 包。' if shared
            else '历史版本 ZIP，选择匹配的 Android 镜像。')
    status = '实验性' if modern else '历史归档'
    search = ' '.join(versions + [row['filename'], abi, status])
    return f'''<article class="package-card" data-kind="{row['kind']}" data-search="{esc(search, quote=True)}">
      <div class="card-top"><span class="badge {row['kind']}">{status}</span><span class="abi">{abi}</span></div>
      <h3>Android {esc(title)}</h3><p class="card-note">{note}</p>
      <a class="download {'primary' if modern else ''}" href="{esc(row['url'], quote=True)}">下载 {'完整包' if modern else 'ZIP'} <span aria-hidden="true">↗</span></a>
      <div class="card-links"><a href="{esc(row['guide'], quote=True)}">安装步骤</a><details><summary>SHA-256</summary><code>{row['sha256']}</code><button class="copy" type="button" data-copy="{row['sha256']}">复制校验值</button></details></div>
    </article>'''


def build(output, repository='m9rco/Genymotion_ARM_Translation', ref='master', root=ROOT):
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Expected owner/repository')
    output = Path(output).resolve()
    if output == root.resolve() or output in root.resolve().parents:
        raise ValueError('Output must not overwrite source')
    if (root / 'site').resolve() in (output, *output.parents):
        raise ValueError('Output must not overwrite site templates')
    reviewed, rows, missing = load_downloads(root, repository, ref)
    source = f'https://github.com/{repository}'
    context = {
        'REPOSITORY': source,
        'REVIEWED': html.escape(reviewed),
        'EXPERIMENTAL_CARDS': '\n'.join(card(row) for row in rows if row['kind'] == 'experimental'),
        'LEGACY_CARDS': '\n'.join(card(row) for row in rows if row['kind'] == 'legacy'),
        'MISSING_CARDS': ''.join(f'<span class="missing-version">Android {html.escape(version)}</span>' for version in missing),
        'LEGACY_COUNT': str(sum(row['kind'] == 'legacy' for row in rows)),
        'EXPERIMENTAL_COUNT': str(sum(row['kind'] == 'experimental' for row in rows)),
        'MISSING_COUNT': str(len(missing)),
    }
    template = (root / 'site/index.html').read_text(encoding='utf-8')
    for key, value in context.items():
        template = template.replace('{{' + key + '}}', value)
    if re.search(r'\{\{[A-Z_]+\}\}', template):
        raise ValueError('Unresolved template variable')
    output.mkdir(parents=True, exist_ok=True)
    (output / 'index.html').write_text(template, encoding='utf-8')
    (output / '.nojekyll').write_text('', encoding='utf-8')
    for name in ('style.css', 'app.js'):
        shutil.copyfile(root / 'site' / name, output / name)
    (output / 'downloads.json').write_text(json.dumps({
        'reviewed': reviewed, 'packages': rows, 'missing_versions': missing,
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Built {output}: {len(rows)} downloads, {len(missing)} missing versions')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'work/pages')
    parser.add_argument('--repository', default='m9rco/Genymotion_ARM_Translation')
    parser.add_argument('--ref', default='master')
    args = parser.parse_args()
    build(args.output, args.repository, args.ref)


if __name__ == '__main__':
    main()
