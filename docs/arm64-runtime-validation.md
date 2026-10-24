# ARM64 runtime acceptance — not yet performed

The current integration status is **experimental / runtime unverified**. No Intel/AMD Genymotion Android 11 test device was available during implementation. Automated tests use temporary file fixtures and mocked ADB; they do not emulate Android, Houdini, root mounts, SELinux or an app process.

## Record the environment

Record host OS/CPU, Genymotion version, virtual image name/build/fingerprint, SDK, kernel architecture, payload SHA-256 and the integration commit. Save the full output and exit status of `python3 scripts/android11_arm64.py verify --serial SERIAL` after reboot. Property files and device identifiers should remain private.

## Native ARM64 probe

CI cross-compiles the probe and checks its ELF64/AArch64 header without executing it. A successful workflow uploads an `android11-arm64-smoke` artifact (seven-day retention). Alternatively, build locally with an installed [Android NDK](https://developer.android.com/ndk/guides/other_build_systems) and the AArch64 Android compiler. Replace `/path/to/ndk` and `HOST_TAG` with your installation's toolchain directory (for example `linux-x86_64`, `windows-x86_64` or `darwin-x86_64`):

```sh
/path/to/ndk/toolchains/llvm/prebuilt/HOST_TAG/bin/aarch64-linux-android30-clang \
  -O2 tests/arm64-smoke/main.c -o work/android11/arm64-smoke
/path/to/ndk/toolchains/llvm/prebuilt/HOST_TAG/bin/llvm-readelf \
  -h work/android11/arm64-smoke
```

Confirm `ELF64`, `AArch64` and a successful compiler exit. The probe source refuses a host/x86 build and checks 64-bit arithmetic before printing its marker.

```sh
adb -s SERIAL push work/android11/arm64-smoke /data/local/tmp/arm64-smoke
adb -s SERIAL shell chmod 755 /data/local/tmp/arm64-smoke
adb -s SERIAL shell /system/bin/houdini64 /data/local/tmp/arm64-smoke
```

Accept only an exit status of zero and exact marker `ARM64_TRANSLATION_OK`. Save stdout/stderr and relevant logcat output. This explicitly exercises the ARM64 launcher; it does not depend on `binfmt_misc` registration. If the launcher rejects the invocation or execution fails, record failure rather than inferring success from properties.

## ARM64 application/JNI test

Use an APK you are authorized to test whose native libraries contain **only `arm64-v8a`**, or an equivalent complete ARM64 split set. Record the APK's hash and inspect its library inventory:

```sh
unzip -Z1 application.apk | awk -F/ '$1 == "lib" && NF >= 3 {print $2}' | sort -u
adb -s SERIAL install application.apk
```

Launch the app, exercise an action known to load its ARM64 native library, and record the expected/observed result. A Java-only screen appearing is insufficient. Capture logs immediately afterward with `adb -s SERIAL logcat -d > arm64-app-logcat.txt`. Redact private data before sharing. Record the Android package name/version and tested feature, not a broad claim that every app works.

## Result record

| Check | Current evidence | Acceptance evidence required |
| --- | --- | --- |
| Archive and core ELF integrity | Passed on downloaded release 1.0 | Pinned hash/CRC/core header checks |
| Host tooling and property apply/restore | Passed on isolated file fixtures | Same checks on the selected VM |
| Post-reboot device configuration | Not performed | `configuration_matches: true` |
| AArch64 execution | Not performed | Probe marker and exit status 0 |
| ARM64-only APK native feature | Not performed | App/feature outcome plus logs |
| Reboot persistence and property restore | Not performed on a VM | Reboot, repeat probe, restore properties and verify original hashes |

A success report applies only to the recorded host, VM build, payload and app. Android 10, Android 12+ and other CPU/image combinations remain outside this profile.
