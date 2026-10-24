# Package audit — 2026-10-24

Baseline: repository commit `2a6b716371a83a905e40c22c7abf6be3d0f2ebbf`.

## Invalid Android 4.3 download

`package/Genymotion-ARM-Translation_for_4.3.zip` was a 46,204-byte HTML document beginning with `<!DOCTYPE html>` and referencing Gitee page assets. It was not a ZIP archive; both Python's ZIP inspection and `unzip` rejected it.

Its SHA-256 was:

```text
4959cb7dd43d239951ceb993f5abddd472faed3ae38e35452368375093d03b52
```

The invalid file was removed from the current tree and download table. It remains recoverable in Git history. No replacement package or Android 4.3 support is claimed.

## Retained packages

All six retained archives passed ZIP CRC checks. Their bytes are unchanged from the baseline above. Sizes and SHA-256 hashes are tracked in [SHA256SUMS](../SHA256SUMS) and the table below. Hashes are repository baselines, not upstream signatures.

| Android label | Bytes | Core translation library inspection |
| --- | ---: | --- |
| 4.4 | 9,390,250 | `system/lib/libhoudini.so`: ELF32, Intel 80386 |
| 5.1 | 28,554,474 | `system/lib/libhoudini.so`: ELF32, Intel 80386 |
| 6.0 | 33,633,324 | `system/lib/libhoudini.so`: ELF32, Intel 80386 |
| 7.X | 36,709,693 | `system/lib/libhoudini.so`: ELF32, Intel 80386 |
| 8.0 | 39,089,799 | `system/lib/libhoudini.so`: ELF32, Intel 80386 |
| 9.0 | 42,496,124 | `system/lib/libhoudini.so`: ELF32, Intel 80386 |

The core library headers identify the translator's x86 executable architecture; they are not runtime compatibility tests. The 4.4 archive also contains an ARM32 recovery `update-binary`; that is distinct from the x86 translation library. The 6.0 archive includes a historical `.DS_Store` entry, retained to preserve its original bytes.

## Provenance and limits

[PR #27](https://github.com/m9rco/Genymotion_ARM_Translation/pull/27) attributes the Android 9.0 binaries to the Android-x86 project and cites `http://dl.android-x86.org/houdini.php?v=9_y`. This records the contributor's attribution, not independently verified origin or redistribution permission. The repository does not establish a complete upstream source/license chain for the other archives.

The [Genymotion installation guide](https://docs.genymotion.com/usage/desktop/install_apps/) identifies ARM translation libraries as Intel property. The repository's MIT license must not be interpreted as relicensing those third-party binaries.

This update inspected local files only: ZIP structure/CRC, hashes, sizes and the core library's ELF headers. It did not execute payloads, flash devices, run applications, certify binaries as safe, obtain upstream signatures or add new Android/ARM64 compatibility. No engine source or reproducible build pipeline is present.

## Maintenance checks

Run `python3 scripts/verify_packages.py` from the repository root. The check fails for missing/unlisted packages, changed hashes, malformed checksum entries, invalid ZIP files or corrupt ZIP members. CI runs this check on pushes and pull requests.

When intentionally updating package contents, first review provenance, redistribution terms and runtime evidence. Then run `python3 scripts/verify_packages.py --write-checksums`, review the checksum diff, and rerun the normal check. The writer validates every ZIP before replacing the checksum file.

## Subsequent Android 11 integration

The separate [experimental Android 11 ARM64 profile](android11-arm64.md) pins the upstream release used in the [downloadable offline package](../package/README.md); it is not one of the six legacy ZIPs audited above and is not added to `SHA256SUMS`. Its profile tracks complete-payload and core ELF hashes. Runtime evidence is tracked separately in the [acceptance procedure](arm64-runtime-validation.md).
