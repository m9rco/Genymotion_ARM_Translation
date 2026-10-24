# Genymotion ARM Translation

ARM translation resources for Genymotion Desktop: preserved **legacy x86/ARMv7 packages** plus an **experimental Android 11 x86_64 → ARM64/ARMv7 integration**.

For Intel/AMD hosts and ARM64 applications, start with the [Android 11 setup](docs/android11-arm64.md). It includes a pinned external payload, guarded configuration/restore scripts and a [runtime acceptance procedure](docs/arm64-runtime-validation.md). Real-device runtime validation is pending. The legacy ZIPs below remain 32-bit only.

[简体中文](README.zh-CN.md) · [ADB guide](tools/adb.md) · [Package audit](docs/package-audit.md)

## Legacy packages and compatibility

This repository preserves prebuilt packages, not the translation engine's source code or a reproducible build system. Package names indicate their intended Android versions, **not a current compatibility certification**. No emulator runtime validation was performed for the 2026-10-24 maintenance update.

| Android image | Package | Status |
| --- | --- | --- |
| 4.3 | Unavailable | Previous file was HTML, not a ZIP; see the [audit](docs/package-audit.md). |
| 4.4 | [Download ZIP](package/Genymotion-ARM-Translation_for_4.4.zip?raw=true) | Legacy; archive integrity checked |
| 5.1 | [Download ZIP](package/Genymotion-ARM-Translation_for_5.1.zip?raw=true) | Legacy; archive integrity checked |
| 6.0 | [Download ZIP](package/Genymotion-ARM-Translation_for_6.0.zip?raw=true) | Legacy; archive integrity checked |
| 7.x | [Download ZIP](package/Genymotion-ARM-Translation_for_7.X.zip?raw=true) | Legacy; archive integrity checked |
| 8.0 | [Download ZIP](package/Genymotion-ARM-Translation_for_8.0.zip?raw=true) | Legacy; archive integrity checked |
| 9.0 | [Download ZIP](package/Genymotion-ARM-Translation_for_9.0.zip?raw=true) | Legacy; archive integrity checked |
| 11 / API 30, x86_64 | [Experimental ARM64/ARMv7 integration](docs/android11-arm64.md) | External payload; runtime unverified |
| 10, 12+ and other unlisted versions | No matching integration | Do not flash a package for a different Android version. |

There are no dedicated 5.0, 7.1 or 8.1 packages here; the historical `7.X` label does not establish validation on every 7.x image. Use the named package only with an appropriate disposable legacy image. Reports about using the 8.0 package on 9.0 are mixed ([#12](https://github.com/m9rco/Genymotion_ARM_Translation/issues/12), [#26](https://github.com/m9rco/Genymotion_ARM_Translation/issues/26)); they do not extend the supported range.

For current host/image ABI compatibility, consult the [Genymotion installation guide](https://docs.genymotion.com/usage/desktop/install_apps/#supported-abis). Apple Silicon uses ARM64 images and is outside this legacy x86 package workflow. For ARM64 applications, use a compatible ARM64 device/image, or obtain an APK built for the target device's ABI. See also [Genymotion SaaS deployment](https://docs.genymotion.com/usage/saas/deploy_apps/) and [Android ABI documentation](https://developer.android.com/ndk/guides/abis).

## Install on a legacy x86 image

Flashing changes the Android system and can leave a virtual device unusable. Back up needed data and use a disposable device. Install ARM translation **before Open GApps**, as described in the [official flashing instructions](https://docs.genymotion.com/usage/desktop/install_apps/#arm-32-bit-applications-on-x86_64-computers).

1. Check the virtual device's Android version and ABI with ADB (see [setup](tools/adb.md)):

   ```sh
   adb devices -l
   adb -s SERIAL shell getprop ro.build.version.release
   adb -s SERIAL shell getprop ro.product.cpu.abi
   adb -s SERIAL shell getprop ro.product.cpu.abilist
   ```

   Replace `SERIAL` with the intended Genymotion device from `adb devices -l`. On old Android images, `abilist` may be empty; also inspect `ro.product.cpu.abi2`.

2. Download the matching ZIP above. Keep it compressed. Verify its hash against [SHA256SUMS](SHA256SUMS), then drag the ZIP onto the running virtual device and accept the flash prompt.
3. Reboot the virtual device after flashing:

   ```sh
   adb -s SERIAL reboot
   ```

4. Once Android has finished booting, inspect the ABI properties again. Seeing `armeabi-v7a` (and sometimes `armeabi`) alongside `x86` indicates advertised 32-bit ARM support; it does not prove that a particular app will run.
5. Install an APK with compatible native libraries:

   ```sh
   adb -s SERIAL install "application.apk"
   ```

If drag and drop only copies the ZIP, check the image/version and downloaded file first. On legacy images that actually provide `/system/bin/flash-archive.sh`, the manual fallback is:

```sh
adb -s SERIAL shell ls /system/bin/flash-archive.sh
adb -s SERIAL push "package/Genymotion-ARM-Translation_for_8.0.zip" /sdcard/Download/arm-translation.zip
adb -s SERIAL shell sh /system/bin/flash-archive.sh /sdcard/Download/arm-translation.zip
adb -s SERIAL reboot
```

This example is for **Android 8.0 only**; substitute the matching local ZIP. Stop if the script is missing or flashing fails. Do not repeatedly flash packages from other versions.

## Troubleshooting

### `INSTALL_FAILED_NO_MATCHING_ABIS`

Compare the device properties above with the APK's native library directories:

```sh
unzip -Z1 "application.apk" | awk -F/ '$1 == "lib" && NF >= 3 {print $2}' | sort -u
```

An APK containing only `arm64-v8a` libraries cannot use the legacy 32-bit packages. On an Android 11 x86_64 Genymotion guest, see the separate [experimental ARM64 integration](docs/android11-arm64.md). For split APK installs, inspect **all** APKs in the split set, including the ABI split; the base APK alone can be misleading. No `lib/` output only means no conventional native libraries were found in that APK, not guaranteed compatibility.

### Installation succeeds but the app crashes

Translation is not full hardware emulation. A matching ABI is necessary for native libraries but does not guarantee runtime compatibility. Capture logs immediately after reproducing the failure:

```sh
adb -s SERIAL logcat -d > genymotion-logcat.txt
```

Check for native crashes, missing libraries, graphics requirements and root detection. Genymotion documents [other installation and runtime limitations](https://docs.genymotion.com/usage/desktop/install_apps/#installation-failures). Recreate a disposable device if flashing caused a boot failure; preserve needed data before resetting anything.

### Android 10+, ARM64, or building a new translator

Android 11 x86_64 now has a separate [experimental ARM64/ARMv7 integration](docs/android11-arm64.md) using an external, hash-pinned third-party payload. Runtime validation is pending. Android 10 and Android 12+ have no matching profile here. This repository does not contain the translator engine source needed to build new engine versions.

## Integrity and maintenance

From the repository root, with Python 3:

```sh
python3 scripts/verify_packages.py
```

This checks the exact package inventory, SHA-256 hashes and ZIP CRCs without extracting or executing package contents. On macOS/Linux, hashes can also be checked with `shasum -a 256 -c SHA256SUMS`; on Linux, `sha256sum -c SHA256SUMS` is another option. These checks detect changes relative to this repository's baseline; they do not establish upstream authenticity, licensing or emulator compatibility.

For a deliberate package update, review the source and redistribution terms, run `python3 scripts/verify_packages.py --write-checksums`, review the resulting diff, then run verification again. CI never regenerates hashes automatically.

Before opening an issue, search [existing reports](https://github.com/m9rco/Genymotion_ARM_Translation/issues) and include the host CPU/OS, Genymotion version, Android image/version, package filename and hash, device ABI output, APK ABI list, reproduction steps and relevant logs. Remove private information from logs before sharing.

## License and provenance

The repository includes an [MIT license](LICENSE). Bundled third-party translation binaries retain their owners' rights; the repository license does not establish that those binaries are MIT-licensed. Genymotion identifies ARM translation libraries as Intel property. Known provenance and audit limits are recorded in [the package audit](docs/package-audit.md).
