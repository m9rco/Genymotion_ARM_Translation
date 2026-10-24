# Packages

**[Download all newly added packages](https://github.com/m9rco/Genymotion_ARM_Translation/releases/download/additional-packages-20261024/Genymotion-ARM-Translation_added-packages_20261024.zip)** — Android 4.3, 5.0 and the shared Android 12–14 ARM64 experimental package.

[Complete version inventory / 完整版本清单](catalog.json)

## Added legacy versions

- [Android 4.3 ZIP](Genymotion-ARM-Translation_for_4.3.zip?raw=true)
- [Android 5.0 / API 21 ZIP](Genymotion-ARM-Translation_for_5.0.zip?raw=true)

Both are real historical ZIPs, statically checked; current runtime compatibility remains unverified.

## Android 12–14 x86_64 — ARM64 only

**[Download the complete experimental package](https://github.com/m9rco/Genymotion_ARM_Translation/releases/download/additional-packages-20261024/Genymotion-ARM-Translation_for_12-14_x86_64_ARM64_experimental_package.zip)** · [Install / 安装](android12-14/INSTALL.md) · [SHA-256](android12-14/PACKAGE_SHA256SUMS)

The shared upstream Android 12 payload is also the upstream target of the 13/14 aliases. It is distributed once, not renamed as independent builds. No ARMv7 support or VM runtime success is claimed.

## Still unavailable

8.1, 10 and 15+ have no matching payload obtained for this project. 7.0/7.1 use the existing 7.X historical label; this is not an independent 7.1 build. Missing versions are recorded explicitly in the catalog rather than filled with another version’s ZIP.

## Android 11 x86_64 — ARM64 / ARMv7

**[Download the complete offline package](https://github.com/m9rco/Genymotion_ARM_Translation/releases/download/android11-arm64-package-20261024/Genymotion-ARM-Translation_for_11.0_x86_64_package.zip)** · [SHA-256](android11/SHA256SUMS) · [Install / 安装](android11/INSTALL.md)

Intel/AMD Genymotion Desktop, rooted Android 11 / API 30 x86_64 only. Experimental; real-device runtime validation is pending.

解压完整包后，将其中的 `system.zip` 拖入虚拟机，再按包内 `INSTALL.md` 配置。完整包包含转译库与配置工具，不需要克隆仓库或二次下载。不要把外层 package ZIP 直接拖入设备。

The large binary bundle is hosted as a GitHub Release asset. Its unchanged upstream payload, configuration tool and checksums are included in the download.

## Legacy Android 4.3–9.0

The eight historical ZIP files in this directory remain unchanged. Choose the matching version from the [main compatibility table](../README.md#legacy-packages-and-compatibility).
