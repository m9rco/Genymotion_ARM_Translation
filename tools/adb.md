`adb` 全称`Android Debug Bridge` ，安卓调试桥接器。它是Android SDK里面的一个工具，用这个工具可以直接操作管理Android模拟器或者真实Android设备。adb的工作方式比较特殊采用监听Socket TCP 5554等端口的方式让IDE和Qemu通讯，默认情况下adb会daemon相关的网络端口，所以当我们运行eclipse时adb进程就会自动运行。

1. adb devices

主要作用：查看当前已连接的设备，连接到计算机的Android设备或者模拟器将会以列表的形式显示。

输出格式：[serialNumber][state]

  如果当前没有模拟器或者设备运行，adb则会返回List of devices attached为空

 offline：表明设备没有连接到计算机或无响应
 device：设备已经连接到计算机。注意，该状态并不表示Android设备可用，当Android设备处于启动阶段时，若连接成功也会返回该状态。

2. adb install <apk文件路径>

主要作用：将指定的apk文件安装到设备上，<apk文件路径>可以从本地文件夹拖动到终端中。

常用参数：
```
adb install –r 覆盖安装

adb install –s 安装到SD卡

adb install –rs覆盖安装到SD卡

adb –s <serial number> install 选定设备安装
```

当有多个设备连接时，可以用下面的命令来直接选定设备进行安装。
```
adb [-d|-e|-s <serial number>] install <path_to_apk>

d：真机（多个设备中只有一个真机时适用）

e：模拟器（多个设备中只有一个模拟器时适用）

s：序列号

adb –d install ./test.apk

adb –s emulator-5556 install ./test.apk
```

3. adb uninstall <包名>

主要作用：卸载设备上的指定程序

查看包名路径：/data/app，系统安装包路径：/sys/data，这两个路径下文件的查看都需要root权限
```
adb uninstall –k <包名>
adb shell pm uninstall –k <包名>
```

卸载程序但是保留其配置和缓存文件，即/data/data/packname下的数据与/sdcard/程序名 的数据


4. adb push/pull

主要作用：复制文件

1）adb push <本地路径><设备路径>

把pc上的文件或文件夹复制到设备中。
```
adb push /home/test.apk /sdcard/
```

2）adb pull <设备路径><本地路径>

把设备上的文件或文件夹复制到电脑

```
adb pull /sdcard/log/test.xls /home/
```

Pull命令后可不输入本地地址，不输入时文件会复制到当前终端所在目录

5. 关闭和启动adb服务

```
sudo –s

adb kill-server  //关闭adb服务
adb start-server //启动adb服务
```

6. sudo –i和sudo –s的区别

```
sudo –i：在root用户下，使用root权限执行adb命令
sudo –s：在当前用户下，使用root权限执行adb命令
```

7. adb logcat

主要作用：查看日志，在命令行中显示调试信息

```
adb logcat >> <指定文件路径>   将logcat信息保存在指定文件中
adb logcat –help：查看logcat命令帮助文档
adb logcat -s NET 查看网络通信信息
```

每一条日志消息都有一个标记和优先级与其关联。

格式为：<priority>/<tag>

过滤不同优先级的log：adb logcat *:W（过滤比W优先级低的log）

标记是一个简短的字符串，用于标识原始消息的来源（例如“View”来源于显示系统）。

优先级是下面的字符，顺序从低到高：

* V—Verbose 明细（最低优先级）
* D—Debug 调试
* I—Info 信息
* W—Warm 警告
* E—Error 错误
* F—Fatal 严重错误
* S—Silent 无记载（最高优先级，没有什么会被记载）

建议配合Eclipse使用，查看logcat

8. adb shell

由于Android是基于Linux内核的操作系统。因此，在Android上可以执行shell命令。

常用命令如下：

```
adb shell <command>    直接运行设备命令
adb shell su –c “<command>”    直接运行root权限命令
```

9. adb shell am

```
am start –n <包名>/<包名>.<Activity名>   启动程序
am force-stop <包名>    强制停止程序
am kill <包名> 杀死与包名有关的后台进程，不影响用户体验，相当于一般的清理内存功能
am kill-all    杀死所有后台进程
```

10. adb shell pm

```
pm path <包名>   查看apk安装在手机后的路径
pm uninstall [-k] <包名>  卸载程序（-k：保留配置文件）
pm clear <包名>    清除应用缓存数据
```

11. 其他常用命令

````
adb help    显示帮助信息
adb version   显示adb版本
adb reboot    重启手机
adb shell am broadcast -a android.intent.action.MASTER_CLEAR（恢复出厂）
adb shell dumpsys window | grep init 查看手机的分辨率
adb logcat -s ActivityManager        Activity的启动时间
```
