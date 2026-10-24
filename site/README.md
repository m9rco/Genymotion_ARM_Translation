# GitHub Pages download center

Site: https://m9rco.github.io/Genymotion_ARM_Translation/

The templates in this directory are filled by `scripts/build_pages.py`. Version availability comes from `package/catalog.json`; SHA-256 values come from the existing checksum files. For release bundles, use the complete package checksum, not the nested system.zip checksum. Shared payloads are grouped into one download card.

## Local build

```sh
python3 -m unittest discover -s scripts -p 'test_build_pages.py' -v
python3 scripts/build_pages.py --output work/pages
python3 -m http.server 8000 --directory work/pages
```

Open http://localhost:8000. No Node, npm, third-party fonts, runtime API calls or framework is required. Content and download links work without JavaScript; JavaScript adds filters and clipboard copying.

## CI and deployment

`.github/workflows/pages.yml` builds and tests pull requests without deploying. Pushes to master run the same checks, verify the package archive inventory, upload only the generated static files, and deploy using the `github-pages` environment and GitHub's official Pages actions. Manual runs are supported; only master can deploy.

Enable Pages with Settings → Pages → Source → GitHub Actions. For a fork, enable Pages there and update the public website link in its README. The repository name used by generated source/download links is taken from `github.repository`; legacy ZIP links are pinned to the build commit. Existing Release URLs in the catalog continue to refer to their actual published assets.

To add a package, update the catalog, package/checksum files and install guide, then push the change. Do not commit work/pages or copy ZIP binaries into the site directory. CI publishes no credentials or device backups.
