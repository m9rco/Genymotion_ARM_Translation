​<h1 align="center">:rocket: Genymotion_ARM_Translation :rocket: </h1>

<p align="center">
<a href="https://github.com/m9rc0">
  <img src="https://img.shields.io/website-up-down-green-red/https/shields.io.svg?label=m9rc0">
</a>
<a href="https://github.com/m9rc0/Genymotion_ARM_Translation">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg">
</a>
</p>

## Genymotion Translation

```
├── LICENSE
├── README.md
└── package
    ├── Genymotion-ARM-Translation_for_4.4.zip
    ├── Genymotion-ARM-Translation_for_5.1.zip
    ├── Genymotion-ARM-Translation_for_6.0.zip
    ├── Genymotion-ARM-Translation_for_7.X.zip
    ├── Genymotion-ARM-Translation_for_8.0.zip
    └── Genymotion-ARM-Translation_for_9.0.zip
```

## Android version mapping

* [4.3](/package/Genymotion-ARM-Translation_for_4.3.zip)
* [4.4](/package/Genymotion-ARM-Translation_for_4.4.zip)
* [5.1](/package/Genymotion-ARM-Translation_for_5.1.zip)
* [6.0](/package/Genymotion-ARM-Translation_for_6.0.zip)
* [7.X](/package/Genymotion-ARM-Translation_for_7.X.zip)
* [8.0](/package/Genymotion-ARM-Translation_for_8.0.zip)
* [9.0](/package/Genymotion-ARM-Translation_for_9.0.zip)

## Genymotion Can't install the APK solution:

1. download Genymotion-ARM-Translation-for[v]
2. Will download the toolkit drag and drop into the Genymotion directly,
3. If failure
```
  1. adb shell
  2. cd /sdcard/Download/
  3. sh /system/bin/flash-archive.sh /sdcard/Download/Genymotion-ARM-Translation.zip
  4. adb reboot
```
4. Resetting the Emulator

## Install Adb

```bash
  brew cask install android-platform-tools
```

## FAQ / Troubleshooting

### APK still doesn't install after installing ARM_Translation tool

If you are still getting this error message, follow the guide:

```
  An error occured while deploying the file.
  This probably means that the app contains ARM native code and your Genymotion device cannot run ARM instructions. You should either build your native code to x86 or install an ARM translation tool in your device.
```

1. Verify if you have installed ARM_Translation successfully.
 - Run `getprop ro.product.cpu.abilist` through ADB shell. If it shows `x86,armeabi-v7a,armeabi`, ARM_Translation has been installed successfully.
 - If you don't know how to run ADB shell, follow [this guide](https://docs.genymotion.com/desktop/041_Deploying_an_app/#install-the-arm-translation-tools) to get ABI information.

2. Check if armeabi-v7a is enough for your APK.
  - Run `unzip -l YOUR_APP.apk | grep -o ' lib/[^/]*/' | uniq`. If the **only** output is `lib/arm64-v8a/`, it means your APK doesn't support armv7 (32bit). You need another armv8 (64bit) translation tool. [This project](https://github.com/niizam/Genymotion_A11_libhoudini) might help.


