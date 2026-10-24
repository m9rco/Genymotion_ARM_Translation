# ADB for Genymotion troubleshooting / ADB 使用说明

ADB (Android Debug Bridge) is part of Android SDK Platform Tools. Its client talks to a local server (normally TCP port 5037), which communicates with device daemons. See the [official ADB guide](https://developer.android.com/tools/adb).

ADB 是 Android SDK Platform Tools 中的调试工具。通常无需使用 `sudo`。以下示例中的 `SERIAL` 必须替换为目标设备序列号，避免多设备时操作错误。

## Install / 安装

Download [SDK Platform Tools](https://developer.android.com/tools/releases/platform-tools) for Windows, macOS or Linux and add its directory to `PATH`. Alternatively, install through Android Studio's SDK Manager.

On macOS with Homebrew:

```sh
brew install --cask android-platform-tools
adb version
```

Genymotion can use bundled ADB or a custom Android SDK path. Check [Genymotion settings](https://docs.genymotion.com/usage/desktop/settings/) if command-line ADB cannot see the device. Avoid running conflicting ADB versions.

## Select a device / 选择设备

```sh
adb devices -l
adb -s SERIAL get-state
adb -s SERIAL shell getprop sys.boot_completed
```

`device` means the ADB connection is ready, not necessarily that Android has finished booting; `sys.boot_completed` normally becomes `1` after startup. `offline` means ADB cannot communicate normally. For `unauthorized`, accept the debugging prompt if the device presents one.

## Inspect version and ABI / 读取版本与架构

```sh
adb -s SERIAL shell getprop ro.build.version.release
adb -s SERIAL shell getprop ro.build.version.sdk
adb -s SERIAL shell getprop ro.product.cpu.abi
adb -s SERIAL shell getprop ro.product.cpu.abi2
adb -s SERIAL shell getprop ro.product.cpu.abilist
adb -s SERIAL shell getprop ro.dalvik.vm.native.bridge
```

Old images may not expose every property. ABI properties advertise capabilities; they do not prove a translator or an app works. See [Android ABIs](https://developer.android.com/ndk/guides/abis).

旧镜像部分属性可能为空。系统声明支持某个 ABI，不等于应用已通过运行验证。

## Install apps and copy files / 安装应用与传输文件

```sh
adb -s SERIAL install "application.apk"
adb -s SERIAL install -r "application.apk"
adb -s SERIAL install-multiple "base.apk" "split_config.armeabi_v7a.apk"
adb -s SERIAL push "local-file.zip" /sdcard/Download/
adb -s SERIAL pull /sdcard/Download/device-file.txt ./device-file.txt
```

`install -r` replaces an existing app while keeping its data when installation is permitted. Split APKs must belong to the same app/version and form a complete set for the device; the filenames above are examples, not a universal split list. Inspect native libraries in every relevant APK.

`adb install` installs APKs; it does **not** flash a translation ZIP. Follow the [repository installation guide](../README.md#install-on-a-legacy-x86-image) for ZIP packages.

## Capture logs / 收集日志

```sh
adb -s SERIAL logcat -d > genymotion-logcat.txt
adb -s SERIAL logcat '*:W'
adb -s SERIAL shell pm path com.example.app
```

Reproduce the problem before capturing logs. Quote `*:W` so your shell does not expand the wildcard. Review logs for private information before sharing.

## Restart / 重启

```sh
adb -s SERIAL reboot
```

If the local ADB server itself is stuck, `adb kill-server` followed by `adb start-server` restarts it. This affects **all** local ADB sessions; coordinate with other device work first. Rebooting does not factory-reset the device.

## Legacy certificate helper / 历史证书脚本

`install-ssl.sh` is an unrelated legacy system-certificate helper, not an ARM translation installer. It assumes an old writable `/system`, BusyBox and a specific block device, and is not validated for current images. Do not use it as part of this installation procedure.
