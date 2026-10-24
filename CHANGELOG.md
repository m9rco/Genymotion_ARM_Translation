# Changelog

## 2026-10-24 — downloadable Android 11 package

- Published a complete offline ZIP with the unchanged Android 11 ARM64/ARMv7 payload, configuration tools, checksums and short installation instructions.
- Added direct download links to the READMEs and package directory. No runtime compatibility status has changed.

## 2026-10-24 — recovery and diagnostic maintenance

- Failed property apply/restore now rolls back to each file's state immediately before the operation, including a previously patched or mixed state. Recovery no longer always writes the initial unpatched backup.
- Repeated apply/restore skips files that already have the requested contents, avoiding unnecessary writes.
- Read-only device verification reports every core library/launcher/linker result in JSON. Missing files, permission/read errors, malformed hash output and timeouts are reported per file rather than stopping at the first failure.
- Added regression coverage for failed restoration, repeated application and incomplete device installations.
- Rechecked the pinned Android 11 upstream release and documented Android 12–15 candidate projects and validation/licensing gaps in the [compatibility status](docs/compatibility-status.md).

Existing generated scripts do not update themselves. Regenerate a bundle with the current tool and your preserved original property files, using a new output directory. Keep the old host backups until recovery is verified.

## 2026-10-24 — experimental Android 11 ARM64 integration

- Added a hash-pinned external Android 11/API 30 x86_64 Houdini profile for experimental ARM64/ARMv7 integration on Intel/AMD hosts.
- Added payload verification, property bundle generation, guarded apply/restore scripts and read-only device configuration checks.
- Added an NDK-cross-compiled AArch64 execution probe and manual runtime acceptance procedure.
- Added automated tests and probe build checks. Device/runtime validation remains pending.

## 2026-10-24 — legacy package audit

- Removed the invalid Android 4.3 download: the file was an HTML page saved as `.zip`.
- Preserved all six Android 4.4–9.0 archives unchanged; added SHA-256 and ZIP CRC verification with CI.
- Rewrote English/Chinese installation and troubleshooting instructions and refreshed the ADB guide.
- Documented package provenance and third-party binary license limitations.

Before this maintenance, the latest repository commit was dated 2023-11-24. No new translator engine was built during these updates.
