# Android 11 x86_64 ARM64/ARMv7 package

完整离线包：内含已校验的 `system.zip` 和配置工具，无需克隆仓库或再次下载转译库。

适用：Intel/AMD 电脑上的 Genymotion Desktop **Android 11 / API 30 x86_64**、已启用 root 的可重建测试虚拟机。不适用于 Android 10/12+ 或 Apple Silicon。实验包，未完成真实设备运行验收。

## 安装

先在电脑上解压本 package，在解压目录打开终端。电脑需要 ADB 和 Python 3.9+；虚拟机先创建快照。将以下 `SERIAL` 替换为 `adb devices -l` 中目标虚拟机的序列号。

1. 拉取目标虚拟机的原始配置，并生成带备份的配置包：

   ```sh
   adb devices -l
   adb -s SERIAL pull /system/build.prop system.original.prop
   adb -s SERIAL pull /system/vendor/build.prop vendor.original.prop
   python3 scripts/android11_arm64.py prepare --payload system.zip --system-prop system.original.prop --vendor-prop vendor.original.prop --output bundle
   ```

   若读取配置被拒绝，先在 Genymotion 中启用 root。不要使用其他设备的配置文件。

2. 把解压后得到的 **`system.zip`** 拖入运行中的虚拟机并确认刷入。不要拖入外层 package ZIP；不要解压 `system.zip`。刷入失败则停止。

3. 推送配置包：

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

   配置成功后退出设备 shell，从电脑执行：

   ```sh
   adb -s SERIAL reboot
   python3 scripts/android11_arm64.py verify --serial SERIAL
   ```

   等 Android 启动完成后再运行 `verify`。成功只表示配置及核心文件匹配，不表示所有 ARM64 应用均可运行。此后可用 `adb -s SERIAL install application.apk` 安装 ABI 匹配的 APK。ARM 转译应先于 Open GApps 安装。

## 恢复

保留电脑上的 `bundle` 和虚拟机快照。设备还能启动时，在 root shell 中执行 `mount -o rw,remount /`，再执行 `sh /data/local/tmp/geny-arm64-bundle/restore-properties.sh` 并重启。该脚本只恢复属性文件；完整撤销刷包应恢复虚拟机快照或重建设备。

## Package contents

- `system.zip`: unchanged upstream Houdini 1.0 payload, 259,372,539 bytes.
- `scripts/android11_arm64.py` and `config/android11-arm64.json`: offline payload verification and device-specific configuration tools.
- `SHA256SUMS`: hashes of all packaged files, including `system.zip`.
- `THIRD_PARTY_NOTICES.md`: payload source and rights notice.

Payload SHA-256: `fc1896c7f85965fb8b6030fa60cefc24eadb5140528647842626c11f526f1361`.
