​<h1 align="center">:whale: Genymotion_ARM_Translation :whale: </h1>

<p align="center">
<a href="https://github.com/m9rc0/Genymotion_ARM_Translation">
  <img src="https://img.shields.io/badge/php-done-brightgreen.svg" alt="php">
</a>
<a href="https://github.com/m9rc0/Genymotion_ARM_Translation">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg">
</a>
</p>

## Genymotion 目前支持的目录

```
  ./
  ├── Genymotion-ARM-Translation_for_4.4.zip
  ├── Genymotion-ARM-Translation_for_5.1.zip
  ├── Genymotion-ARM-Translation_for_6.0.zip
  ├── Genymotion-ARM-Translation_for_8.0.zip
  └── README.md
```

## Genymotion 不能安装APK的解决方法：

1. 下载Genymotion-ARM-Translation-for[版本] 工具转换包；
2. 将下载号的工具包直接拖拽到Genymotion中，
3. 进行操作 （如果失败）
```
  1. adb shell
  2. cd /sdcard/Download/
  3. sh /system/bin/flash-archive.sh /sdcard/Download/Genymotion-ARM-Translation.zip
```
4. 重启模拟器。
