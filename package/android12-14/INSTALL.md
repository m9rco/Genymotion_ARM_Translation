# Android 12–14 x86_64 ARM64 experimental package

This package includes a shared ARM64-only native bridge payload for rooted Genymotion Desktop x86_64 images. Android 12, 12L/12.1, 13 and 14 (API 31–34) are experimental targets. The source repository's 13/14 files are symlinks to the Android 12 tar, not independent engine builds. No VM/app runtime verification has been performed. Android 10/11/15+, ARMv7-only apps and native ARM64 guests are excluded.

## 安装

解压完整 package，在解压目录打开终端。电脑需 ADB、Python 3.9+；使用可重建的测试虚拟机，刷包前先创建快照。以下 `SERIAL` 替换为目标设备序列号。

```sh
adb devices -l
adb -s SERIAL pull /system/build.prop system.original.prop
adb -s SERIAL pull /system/vendor/build.prop vendor.original.prop
python3 scripts/native_bridge.py prepare --payload system.zip --system-prop system.original.prop --vendor-prop vendor.original.prop --output bundle
```

不允许混用已配置的 Houdini 等其他桥接器。如果报版本、架构或桥接器冲突，请停止，不要绕过检查。

将解压后的 **`system.zip`** 拖入运行中的虚拟机确认刷入，不要拖入外层 package ZIP。成功后执行：

```sh
adb -s SERIAL push bundle /data/local/tmp/geny-arm64-bundle
adb -s SERIAL shell
```

在设备 shell 中逐条执行：

```sh
su
mount -o rw,remount /
sh /data/local/tmp/geny-arm64-bundle/apply.sh
```

退出设备 shell，回到电脑终端：

```sh
adb -s SERIAL reboot
python3 scripts/native_bridge.py verify --serial SERIAL
```

等 Android 启动完成后再运行校验。成功只说明属性与核心文件匹配，仍需用实际 ARM64 APK 验收。若系统只读、缺少库、无法启动或校验失败，请保留错误信息并恢复快照。ARM 转译应先于 Open GApps 安装。

## 恢复

在 root shell 中执行 `mount -o rw,remount /`，再执行 `sh /data/local/tmp/geny-arm64-bundle/restore-properties.sh` 并重启，仅恢复属性文件。完整撤销 ZIP 刷入要恢复虚拟机快照或重建设备。

## Contents and limits

`system.zip` is repacked from the pinned upstream tar, preserving file bytes, modes and the valid `system/lib64/libnb.so` symlink. The dangling `system/lib/libnb.so` symlink is omitted because the source contains no 32-bit translator. No ARMv7 capability is advertised. All original file hashes except the omitted symlink are preserved and checked during packaging.

Included tools generate device-specific, guarded configuration/restore scripts. No automatic remount, reboot, SELinux disable or verity disable is performed by the scripts. Keep the original property backups private.
