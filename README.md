# bilibili弹幕网视频下载器😀

[![maven](https://img.shields.io/badge/Python-3.8.8-blue.svg)](https://www.python.org/)  [![mavel](https://img.shields.io/badge/GPL-3.0-red.svg)](https://github.com/JimmyLiang-lzm/biliDownloader/blob/master/LICENSE) ![mavel](https://img.shields.io/badge/requests-2.26.0-green.svg) ![mavel](https://img.shields.io/badge/tqdm-4.62.1-green.svg) 
  [![maven](https://img.shields.io/badge/BiliDownloader-GUI-pink.svg)](https://github.com/JimmyLiang-lzm/biliDownloader_GUI)  [![mavel](https://img.shields.io/badge/README-EN-blue.svg)](https://github.com/JimmyLiang-lzm/biliDownloader/blob/master/README_EN.md)

## 特性✨

1. 本程序基于`Python 3.8.8`进行编写，代码可读性强，易于移植；
2. 可使用参数直接进行控制，方便与服务器环境下使用；
3. 仅需一句代码即可进行视频下载，省略繁琐的操作；
4. 可自动合成视频，也可以进行音视频分离下载；
5. 可通过探查获取不同清晰度的音视频流，并进行下载；
6. 下载过程中若主下载线路阻塞，软件将自动选择备用线路进行下载；
7. 可进行付费番剧或大会员高质量视频的下载（2021-10-06更新）；
8. 可方便进行多集数与分P视频的下载（2021-10-06更新）；
9. 可下载交互视频（2021-10-21更新）；
10. 可在配置文件中设置代理IP访问“仅限港澳台地区”视频（2021-11-05更新）；
11. 增加B站音乐探查与下载功能（2021-11-05更新）。

## 如何使用？🕹

### 1. Python环境下的安装和使用

**安装**：

1. 首先确保你的Python版本为3.8.8或以上，随后按照以下代码进行环境构建；

```shell
git clone https://github.com/JimmyLiang-lzm/biliDownloader.git
cd biliDownloader
pip3 install -r requirements.txt
```

2. 进行**FFMpeg**程序的下载，👉[点击这里](http://ffmpeg.org/download.html)👈进入官网进行下载：

   * **Windows部署**：将下载的压缩包解压后，复制压缩文件中的`ffmpeg.exe`并粘贴到`biliDownloader`程序根目录下即可。
   * **Ubuntu部署**：可利用以下代码进行简单安装，若需要使用比较新的版本，请进入官网下载并且编译。

   ```shell
   sudo add-apt-repository -y ppa:djcj/hybrid
   sudo apt update
   sudo apt install -y ffmpeg
   ```

3. 更改初始化参数，进入根目录中的`setting.conf`文件中，将`"sys":"XXX"`中的`XXX`修改成你使用的系统平台。使用Windows平台时请修改为`windows`，使用Ubuntu平台时请修改为`unix`。

**使用：**

若要检查视频下载地址，可直接使用以下代码进行查看，其中`HTTPAddress`代表网页地址：

```shell
python3 bili_Download.py -a HTTPAddress -c
```

若要进行视频下载，可直接使用以下代码进行下载，`OutputPath`代表输出文件夹：

```shell
python3 bili_Download.py -a HTTPAddress -o OutputPath
```

在进行多视频分集下载时，需要在下载视频的后尾增加`-l`与ListNUM参数，ListNUM由数字、‘,’与‘-’构成，例如`-l 1,3,5-9`其中数字代表指定下载的集数，通过半角逗号进行区分，通过横线可以指定下载视频5到视频9的全部分集：

```shell
python3 bili_Download.py -a HTTPAddress -o OutputPath -l ListNUM
```

### 2. Windows系统环境下的安装与使用

**安装：**

1. 进入本项目**release**中进行下载，下载完成后进行解压；
2. 进行**FFMpeg**程序的下载，👉[点击这里](https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2021-08-14-git-acd079843b-full_build.7z)👈进行下载，解压后将"bin->ffmpeg.exe"解压到"bili_Download"文件夹中。
3. 更改初始化参数，打开根目录`bili_Download`文件夹中的`setting.conf`文件，将`"sys":"XXX"`中的`XXX`修改成`windows`。

**使用：**

为了方便在Windows系统中进行使用，请点击解压目录中的`Start.bat`批处理脚本，若要检查视频下载地址，可直接使用以下代码进行查看，其中`HTTPAddress`代表网页地址：

```shell
bili_Download.exe -a HTTPAddress -c
```

若要进行视频下载，可直接使用以下代码进行下载，`OutputPath`代表输出文件夹：

```shell
bili_Download.exe -a HTTPAddress -o OutputPath
```

在进行多视频分集下载时，需要在下载视频的后尾增加`-l`与ListNUM参数，ListNUM由数字、‘,’与‘-’构成，例如`-l 1,3,5-9`其中数字代表指定下载的集数，通过半角逗号进行区分，通过横线可以指定下载视频5到视频9的全部分集：

```shell
bili_Download.exe -a HTTPAddress -o OutputPath -l ListNUM
```

若不使用批处理脚本，则需要在`bili_Download.exe`前面加入**绝对地址**。

### 3. 其他

利用Google Colab下载视频（免安装但要配合科学上网）：[<img src="https://colab.research.google.com/assets/colab-badge.svg" align="center">](https://colab.research.google.com/drive/1_t-MXomiiyvHehWh_2ExzuEeAbU8culF)

## 参数🛠

为了能正确使用本程序，参数如下：

* `-a`, `--address`：输入视频页面的HTTP/HTTPS地址，若参数中不带有`-ma`，`--music-address`，`-v`，`--version`，`-h`，`--help`时，此项为必填项；
* `-ma`, `--music-address`：输入音频页面的HTTP/HTTPS地址，若参数中不带有`-a`，`--address`，`-v`，`--version`，`-h`，`--help`时，此项为必填项；
* `-o`, `--output`：下载视频到本地的输出文件夹地址，默认值为程序根目录；
* `-l`, `--download-list`：下载的分集和分P视频列表，若选用则必须输入列表标号，例如“1,2,3-6”；
* `-vq`, `--video-quality`：选择视频清晰度，接受数据类型为整数型数据，可使用`-c`或`--check`进行查看，默认值为**0**；
* `-ar`, `--audio-quality`：选择音频清晰度，接受数据类型为整数型数据，可使用`-c`或`--check`进行查看，默认值为**0**；
* `-s`, `--synthesis`：在视频下载完成后是否执行合成，仅支持输入`0`或`1`；其中`0`表示不进行合成，``1``表示进行合成；默认值为``1``；**此选项只有在完成FFMpeg部署之后才能实现！**
* `-c`, `--check`：检查视频页面是否有可用于下载的音频流与视频流，并显示出来；当此参数出现时，将不会进行视频下载；
* `-i`, `--interact`：下载整个交互视频；
* `-v`, `--version`：查看软件版本信息；
* `-h`, `--help`：显示软件帮助信息。

## 关于大会员视频下载

大会员视频下载已于**2021年10月6日更新**，您可以将您的大会员cookie粘贴到根目录`setting.conf`文件`"cookie":"XXX"`的XXX中即可。您可以尝试使用`-c`, `--check`进行检查。如何获取Cookie请[点击这里](https://jimmyliang-lzm.github.io/2021/10/05/Get_bilibili_cookie/)🤞

## 代理IP设置

将您已知的代理IP地址和端口号以`http://(IP):(Port)`形式填入根目录`setting.conf`文件`"Proxy":"XXX"`的XXX中即可，例如`"Proxy":"http://127.0.0.1:1080"`。

## 声明⚖

本项目受GPL-3.0许可协议保护，所有程序仅用于学习与交流，请勿用于任何商业用途！

## 致谢🤝

💖💖如果您觉得此程序有用，请不吝留下一个**Star**或者**fork**呗，感激不尽！💖💖

