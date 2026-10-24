# Experimental Android 11 ARM64 bridge

[Download the complete offline package](../package/README.md) · [Short installation guide](../package/android11/INSTALL.md) · [中文操作摘要](#中文操作摘要)

This integration targets **Genymotion Desktop Android 11 / API 30, x86_64 guests on Intel/AMD hosts**. It prepares the third-party Houdini 1.0 payload and guarded property patches for ARMv7 and ARM64 applications. It is experimental: offline integration tests pass, but this project has not flashed a device or run an ARM64 application with it. Upstream reports include both working apps and crashes. CPU brand alone does not guarantee compatibility.

Android 10 / API 29, Android 12+, 32-bit x86 guests, native ARM64 guests and Apple Silicon are excluded from this profile. They need different images or bridges; changing an ABI property does not implement translation.

## Source and static validation

The external payload is [niizam/Genymotion_A11_libhoudini release 1.0](https://github.com/niizam/Genymotion_A11_libhoudini/releases/tag/1.0), asset `94257456` (`system.zip`, 259,372,539 bytes). The exact size, SHA-256 and six core ELF hashes are pinned in [config/android11-arm64.json](../config/android11-arm64.json).

```text
fc1896c7f85965fb8b6030fa60cefc24eadb5140528647842626c11f526f1361  system.zip
```

The archive has 689 entries and passed CRC checks on 2026-10-24. Its libraries include ELF32 x86 and ELF64 x86_64 translators and ARM32/ARM64 linkers. This establishes file structure, not runtime compatibility or authenticity. A replaced release asset fails verification rather than silently updating the baseline.

The upstream repository declares MIT; this does not establish redistribution rights for all included Intel/Android binaries. The downloadable package bundles that payload unchanged with its source and rights notice; it does not relicense the binaries. Review upstream terms before downloading or using it.

## 1. Prepare a disposable test device

Take a VM snapshot/clone before flashing. Property backups below only restore properties, not overwritten translation libraries; recovering the full system requires the snapshot or recreating the device. Install this bridge before Open GApps.

Start a **rooted Android 11 x86_64** Genymotion device. Select its explicit serial; do not copy a serial from another machine:

```sh
adb devices -l
adb -s SERIAL shell getprop ro.build.version.sdk
adb -s SERIAL shell uname -m
adb -s SERIAL shell getprop ro.genymotion.version
adb -s SERIAL shell getprop ro.product.cpu.abi
```

Expected: `30`, `x86_64`, a nonempty Genymotion version, and `x86_64`. Stop on a mismatch. Check `ro.dalvik.vm.native.bridge`; do not mix an existing `libndk_translation.so` or another translator with Houdini.

## 2. Download and validate the payload

From the repository root (Python 3.9+):

```sh
mkdir -p work/android11
python3 scripts/android11_arm64.py download --output work/android11/system.zip
```

Alternatively, download `system.zip` from the pinned upstream release, then run:

```sh
python3 scripts/android11_arm64.py check-payload work/android11/system.zip
```

Verification covers the complete archive hash, ZIP CRCs and hashes/class/machine fields of both translators, both launcher executables and both ARM linkers. It never executes their contents. Downloads use a temporary file and are only promoted after verification; existing outputs are not overwritten.

## 3. Capture exact original properties

Keep these files on the host for recovery. Genymotion root must be enabled; if reading is denied, use the rooted device shell to copy the files to a readable temporary location first. Do not substitute example property files from an issue or another VM.

```sh
adb -s SERIAL pull /system/build.prop work/android11/system.original.prop
adb -s SERIAL pull /system/vendor/build.prop work/android11/vendor.original.prop
python3 scripts/android11_arm64.py prepare \
  --payload work/android11/system.zip \
  --system-prop work/android11/system.original.prop \
  --vendor-prop work/android11/vendor.original.prop \
  --output work/android11/bundle
```

The output contains byte-for-byte originals, patched files, `manifest.json`, `apply.sh` and `restore-properties.sh`. It does not modify the VM or copy the large payload into the bundle. Keep this directory private: device property files can contain device identifiers.

Managed ABI/native-bridge properties are replaced once in each file; unrelated properties/comments are preserved. Repeated preparation from the same inputs gives the same configuration. Existing bundle directories are rejected to protect original backups.

## 4. Flash, configure, reboot

Drag the **verified** `work/android11/system.zip` onto the running Genymotion device and accept the flashing prompt. Do not continue if flashing fails. Keep the VM running until the matching property patch is applied.

Push the generated bundle:

```sh
adb -s SERIAL push work/android11/bundle /data/local/tmp/geny-arm64-bundle
adb -s SERIAL shell
```

Inside the device shell, run each command separately:

```sh
su
mount -o rw,remount /
sh /data/local/tmp/geny-arm64-bundle/apply.sh
```

The script requires root, API 30, an x86_64 kernel and Genymotion identity. It verifies both current property files against this bundle's original/patched hashes, checks all six installed core ELF hashes, then writes and rechecks properties while preserving existing file metadata. Modified properties or a bundle from another VM are rejected before property writes. A write failure attempts to restore each changed file to its exact pre-operation state and verifies its hash, even if the device was already patched before this invocation. Files already in the requested state are not rewritten. Any recovery failure is reported.

It does not disable SELinux/verity, remount partitions or reboot automatically. If the system/vendor partition remains read-only, stop and use a compatible writable rooted test image. Do not disable verification or improvise block-device mount commands. See [upstream read-only filesystem issue #11](https://github.com/niizam/Genymotion_A11_libhoudini/issues/11).

After the script reports success, exit the root/device shells and reboot from the host:

```sh
adb -s SERIAL reboot
```

## 5. Verify configuration, then exercise ARM64 code

Wait until Android finishes booting, then:

```sh
python3 scripts/android11_arm64.py verify --serial SERIAL
```

This uses read-only ADB shell queries with an explicit serial. A successful result says `configuration_matches: true` and **`runtime_tested: false`**. It checks all managed ABI/bridge/zygote properties and the six installed core hashes. The JSON `core_files` section records expected/actual hashes and `match`, `mismatch` or `error` for each file. Missing/unreadable files, malformed hash output and per-file timeouts are collected without stopping the remaining core checks. Failure returns a nonzero exit status. It does not certify apps or Play Store compatibility.

Use the [runtime acceptance procedure](arm64-runtime-validation.md) for an AArch64 execution probe and a real ARM64-only APK. Keep the probe result and app result separate: a native executable passing does not establish Android app/JNI compatibility.

Known limits include crashes and Play Store filtering after configuration; see [upstream #2](https://github.com/niizam/Genymotion_A11_libhoudini/issues/2) and [#17](https://github.com/niizam/Genymotion_A11_libhoudini/issues/17). Do not report Android 12+ or arbitrary app compatibility from an ABI list.

Generated bundles embed the script version used at preparation time. After a tooling update, regenerate from your preserved original property files into a **new** output directory; an existing on-device bundle does not update automatically. See the [changelog](../CHANGELOG.md).

## Restore properties

With the same bundle still on the VM, open `adb -s SERIAL shell`, then run separately:

```sh
su
mount -o rw,remount /
sh /data/local/tmp/geny-arm64-bundle/restore-properties.sh
```

Reboot afterward. The restore script verifies the original backup files and accepts only original/patched target hashes from this bundle. It refuses to overwrite unrelated subsequent edits. If Android cannot boot or ADB cannot connect, restore the VM snapshot or recreate the device. This restores property files only; it does not uninstall translation libraries or undo the ZIP flash.

## 中文操作摘要

本次新增的是 **Intel/AMD 宿主机上，Genymotion Desktop Android 11 x86_64 镜像运行 ARM64/ARMv7 应用的实验性接入**，不是 Android 10/12+ 通用刷包。当前完成文件检查和离线自动测试，尚无真实设备运行验收。

按上文步骤操作：先创建快照，下载并校验指定上游包；从目标虚拟机拉取两个原始 `build.prop`，使用 `prepare` 生成带原文件备份的配置包；拖入 ZIP 刷包后，在同一台虚拟机以 root 执行 `apply.sh`，成功后再重启。脚本会拦截版本/架构不符、配置变化及核心库不符，不会自动关闭 SELinux 或校验机制。

`verify --serial SERIAL` 只证明配置和文件匹配，不能证明应用可用。实际验收需按[运行测试步骤](arm64-runtime-validation.md)执行 ARM64 探针和真实 ARM64 APK。出现问题时，可用 `restore-properties.sh` 恢复属性；完整系统恢复依赖刷包前快照。
