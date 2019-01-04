​<h1 align="center">:rocket: Genymotion_ARM_Translation :rocket: </h1>

<p align="center">
<a href="https://github.com/m9rc0">
  <img src="https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=m9rc0">
</a>
<a href="https://github.com/m9rc0/Genymotion_ARM_Translation">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg">
</a>
</p>

## Genymotion 目前支持的目录

```
├── LICENSE
├── README.md
└── package
    ├── Genymotion-ARM-Translation_for_4.4.zip
    ├── Genymotion-ARM-Translation_for_5.1.zip
    ├── Genymotion-ARM-Translation_for_6.0.zip
    └── Genymotion-ARM-Translation_for_8.0.zip
```

## 对应安卓版本

* [4.4](/package/Genymotion-ARM-Translation_for_4.4.zip)
* [5.1](//package/Genymotion-ARM-Translation_for_5.1.zip)
* [6.0](/package/Genymotion-ARM-Translation_for_6.0.zip)
* [8.0](/package/Genymotion-ARM-Translation_for_8.0.zip)

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
