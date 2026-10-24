# Compatibility and upstream status

Reviewed on **2026-10-24**. A source project's version claim is distinct from a runtime result for this repository. This table describes Genymotion Desktop guests on Intel/AMD hosts; it does not apply to native ARM64 images or Genymotion SaaS.

| Guest Android / architecture | This repository | Validation |
| --- | --- | --- |
| 4.3 | No usable package | Previous HTML download removed |
| 4.4, 5.1, 6.0, 7.X, 8.0, 9.0 / legacy x86 | Preserved historical ARMv7 packages | SHA-256 and ZIP CRC checked; current runtime unverified |
| 10 / API 29 | No profile | No matching package validated |
| 11 / API 30 / x86_64 | [Experimental ARM64/ARMv7 integration](android11-arm64.md) | Payload/core ELF integrity and offline tooling tested; VM/runtime acceptance pending |
| 12–15 / x86_64 | External candidates identified; no integrated profile | Requires independent payload/provenance review and per-image runtime acceptance |
| 16+ | No profile | Not investigated or validated |

## Android 11 upstream

[niizam/Genymotion_A11_libhoudini release 1.0](https://github.com/niizam/Genymotion_A11_libhoudini/releases/tag/1.0) is still the latest published release at this review. Its `system.zip` asset metadata remains 259,372,539 bytes, last updated 2023-02-04. This is not a new upstream engine release; the [local profile](../config/android11-arm64.json) continues to pin the audited full SHA-256 and core file hashes.

A release metadata check does not replace downloading and hashing the asset. Use `check-payload` for a local file; a changed upstream asset will fail the pinned hash check.

## Android 12–15 candidates

[naijun0403/genymotion-tools](https://github.com/naijun0403/genymotion-tools), reviewed at commit [`31dd162`](https://github.com/naijun0403/genymotion-tools/tree/31dd16203b4e9efbe28d92585ac82a94efd3675c), claims Android 12–15 integration. Its [`stuff/ndk.py`](https://github.com/naijun0403/genymotion-tools/blob/31dd16203b4e9efbe28d92585ac82a94efd3675c/stuff/ndk.py) selects the **same Android 12 tar payload** for all four versions. That mapping alone does not establish compatibility with each Genymotion image. The reviewed tree has no license file, so its implementation is not copied into this repository.

The referenced payload project, [zhouziyang/libndk_translation](https://github.com/zhouziyang/libndk_translation/tree/c2093bd678eb493ea0f918e01ab76c0695a54c3c), documents prebuilts for Android 11–14 and extraction from Android Emulator images. Its reviewed tree also has no license/notice file establishing redistribution rights. This repository does not mirror these binaries or infer an Android 15 support guarantee from them.

Before adding a profile, record the exact source and hashes, inspect archive paths/symlinks/core ELF files, establish applicable use/redistribution terms, and run the [runtime acceptance procedure](arm64-runtime-validation.md) adapted to the exact Android image. Native bridge properties and payload layout may differ from the Android 11 Houdini profile; do not substitute a tarball into that tool.

For current platform ABI behavior, refer to the [Genymotion installation documentation](https://docs.genymotion.com/usage/desktop/install_apps/). Official platform availability and a third-party bridge's runtime compatibility are separate checks.
