# Genymotion ARM Translation

**[直接下载 Android 11 ARM64/ARMv7 完整包](https://github.com/m9rco/Genymotion_ARM_Translation/releases/download/android11-arm64-package-20261024/Genymotion-ARM-Translation_for_11.0_x86_64_package.zip)** · [安装步骤](package/android11/INSTALL.md)


本项目提供 Genymotion Desktop 的历史 x86/ARMv7 转译包，并新增 **Android 11 x86_64 → ARM64/ARMv7 实验性接入**。

Intel/AMD 电脑运行 ARM64 应用，请使用[Android 11 接入指南](docs/android11-arm64.md)：包含固定哈希的外部包、配置及恢复脚本和[运行验收步骤](docs/arm64-runtime-validation.md)。真实设备运行验证尚未完成。下列历史 ZIP 仍仅面向 32 位应用。

[English](README.md) · [ADB 使用说明](tools/adb.md) · [文件审计记录](docs/package-audit.md)

[更新记录（2026-10-24）](CHANGELOG.md) · [版本支持与上游调研](docs/compatibility-status.md)

## 版本与适用范围

仓库只保存预编译包，没有转译引擎源码或可复现构建流程。文件名表示历史目标版本，不代表当前兼容性认证。2026-10-24 的维护仅进行静态文件检查，未在模拟器上进行运行验证。

| Android 镜像 | 下载 | 状态 |
| --- | --- | --- |
| 4.3 | 暂无可用包 | 原文件是 HTML 网页，已移除，见[审计记录](docs/package-audit.md)。 |
| 4.4 | [ZIP](package/Genymotion-ARM-Translation_for_4.4.zip?raw=true) | 历史包，压缩包完整性通过 |
| 5.1 | [ZIP](package/Genymotion-ARM-Translation_for_5.1.zip?raw=true) | 历史包，压缩包完整性通过 |
| 6.0 | [ZIP](package/Genymotion-ARM-Translation_for_6.0.zip?raw=true) | 历史包，压缩包完整性通过 |
| 7.x | [ZIP](package/Genymotion-ARM-Translation_for_7.X.zip?raw=true) | 历史包，压缩包完整性通过 |
| 8.0 | [ZIP](package/Genymotion-ARM-Translation_for_8.0.zip?raw=true) | 历史包，压缩包完整性通过 |
| 9.0 | [ZIP](package/Genymotion-ARM-Translation_for_9.0.zip?raw=true) | 历史包，压缩包完整性通过 |
| 11 / API 30，x86_64 | [实验性 ARM64/ARMv7 接入](docs/android11-arm64.md) | 使用外部包，尚未验证真实运行 |
| 10、12+ 及其他未列版本 | 暂无对应方案 | 不要跨 Android 版本刷入。 |

本仓库没有专门的 5.0、7.1 或 8.1 包；`7.X` 的历史命名不代表验证过所有 7.x 镜像。[8.0 包用于 9.0 的反馈](https://github.com/m9rco/Genymotion_ARM_Translation/issues/26)存在差异，不能据此扩展兼容范围。

Apple Silicon 使用的 ARM64 镜像不适用本项目的旧版 x86 刷包流程。只有 ARM64 原生库的应用，应使用兼容的 ARM64 设备或镜像，或获取匹配目标设备 ABI 的 APK。请以 [Genymotion 当前 ABI 文档](https://docs.genymotion.com/usage/desktop/install_apps/#supported-abis)及 [SaaS 部署文档](https://docs.genymotion.com/usage/saas/deploy_apps/)为准。

## 安装步骤

刷包会修改 Android 系统，可能导致虚拟设备无法启动。先备份需要的数据，并使用可重建的测试设备。按照[官方说明](https://docs.genymotion.com/usage/desktop/install_apps/#arm-32-bit-applications-on-x86_64-computers)，ARM 转译包应先于 Open GApps 安装。

1. 安装并配置 [ADB](tools/adb.md)，读取设备版本与 ABI：

   ```sh
   adb devices -l
   adb -s SERIAL shell getprop ro.build.version.release
   adb -s SERIAL shell getprop ro.product.cpu.abi
   adb -s SERIAL shell getprop ro.product.cpu.abilist
   ```

   将 `SERIAL` 换成目标 Genymotion 设备的序列号。旧版 Android 的 `abilist` 可能为空，还需查看 `ro.product.cpu.abi2`。

2. 下载匹配版本的 ZIP，按 [SHA256SUMS](SHA256SUMS) 核验。不要解压，直接拖入运行中的虚拟设备，确认刷入提示。
3. 刷入成功后执行 `adb -s SERIAL reboot`，等待 Android 完成启动。
4. 再次读取 ABI 属性。出现 `armeabi-v7a`（有时还有 `armeabi`）表示系统声明支持 32 位 ARM，不代表所有应用都能运行。
5. 执行 `adb -s SERIAL install "application.apk"` 安装 ABI 匹配的应用。

拖入后仅复制文件时，先核对镜像版本和下载内容。仅当旧版镜像实际包含 `/system/bin/flash-archive.sh` 时，才适用 [English README 的手动刷入示例](README.md#install-on-a-legacy-x86-image)。脚本不存在或刷入失败时停止，不要轮流刷入其他版本。

## 常见问题

**安装提示 `INSTALL_FAILED_NO_MATCHING_ABIS`**：对照设备 ABI，检查 APK 中的原生库：

```sh
unzip -Z1 "application.apk" | awk -F/ '$1 == "lib" && NF >= 3 {print $2}' | sort -u
```

如果只有 `arm64-v8a`，历史 32 位包无法解决；Android 11 x86_64 镜像可使用独立的[实验性 ARM64 接入](docs/android11-arm64.md)。分包安装需要检查整套 APK，尤其是 ABI 分包，不能只看 base APK。没有输出仅说明该 APK 没有常规 `lib/` 路径下的原生库，不保证兼容。ABI 的含义见 [Android 官方文档](https://developer.android.com/ndk/guides/abis)。

**安装后闪退**：在复现后运行 `adb -s SERIAL logcat -d > genymotion-logcat.txt`，检查原生崩溃、缺失库、图形要求和 root 检测等原因。ABI 匹配不等于运行兼容。刷入后无法启动时可重建测试设备；重置前先保留所需数据。

**Android 10+、ARM64 或自行编译**：新增的[Android 11 x86_64 实验性接入](docs/android11-arm64.md)使用哈希固定的外部第三方包，提供 ARM64/ARMv7 配置工具，真实运行验收待完成。Android 10 和 Android 12+ 暂无对应方案；本仓库也没有可构建新转译引擎的源码。

## 完整性检查与维护

在仓库根目录运行：

```sh
python3 scripts/verify_packages.py
```

脚本核对文件清单、SHA-256 与 ZIP CRC，不解压到磁盘，也不执行包内文件。也可使用 `shasum -a 256 -c SHA256SUMS`；Linux 可用 `sha256sum -c SHA256SUMS`。

校验只用于发现相对仓库基线的变化，不证明上游真实性、授权或模拟器兼容性。主动更新包时，应先确认来源与再分发条件，再运行 `python3 scripts/verify_packages.py --write-checksums`，审阅校验值变化并重新校验。CI 不会自动重写基线。

提交 issue 前先搜索已有问题，附上宿主 CPU/系统、Genymotion 版本、Android 镜像版本、ZIP 名称与哈希、设备及 APK 的 ABI、复现步骤和相关日志；分享日志前移除隐私信息。

## 许可与来源

仓库包含 [MIT LICENSE](LICENSE)。第三方转译二进制仍受其权利人的条款约束，仓库许可不能证明这些二进制采用 MIT 许可。Genymotion 将转译库标为 Intel 财产。已知来源和核验边界见[审计记录](docs/package-audit.md)。
