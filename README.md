## 项目介绍

为了方便下载的ASoul唱过的歌，并且在MP3或者iTunes里能有一个好看的封面和完善的歌曲信息，本项目在[JimmyLiang-lzm/biliDownloader（基于版本:5f61cae5fa016c591f57a5553fe6faf9fddf6493）](https://github.com/JimmyLiang-lzm/biliDownloader)的基础上增加修改了一些功能，完成了一个专用于下载A-Soul成员在B站上的投稿视频并转换为带标签MP3的工具。

>   不知道提供下载会不会构成侵权，先给小伙伴们说一声对不起🙇←🏃

## ASoulMP3maker

### 安装

在python的3.8和3.9下测试通过，理论上python3都可以用，使用前请先安装对应的python库并切换工作目录。
> **windows用户请确保命令行中通过python命令调用的是python3**。对于从微软商店安装python3的用户，请卸载并安装官网版本。或将代码./ASoulMP3maker.py中的第16行的井号(#)删掉

```shell
cd ASoulMP3maker
pip3 install -r requirements.txt
```

-   **Windows部署**：
    1. 如果已经在环境变量中添加了ffmpeg，则无需手动复制ffmpeg到当前目录。换言之，如果要使用系统中的ffmpeg，请保证当前目录下没有ffmpeg.exe
    2. 否则需要手动进行**FFMpeg**程序的下载，👉[点击这里](http://ffmpeg.org/download.html)👈进入官网进行下载。
    3. 将下载的压缩包解压后，复制压缩文件中的`ffmpeg.exe`并粘贴到`ASoulMP3maker`程序根目录下即可。
-   **Linux和Mac OS部署**：
    1.   借助apt、brew等包管理工具安装。

### 使用

#### 下载单个视频并转换

```shell
python3 bili_Download.py -a <HTTPAddress> -mp3
# 或者
python3 bili_Download.py -a <HTTPAddress> -m4a
python3 bili_Download.py -a <HTTPAddress> -aac
```
1.   将`<HTTPAddress>`换成你要下载的视频地址，如`https://www.bilibili.com/video/BV1ER4y1E7qn`。

2.  在某一次更新中增加了补充歌手名称和专辑名称功能。将歌手名固定为A-Soul，专辑名为《A-Soul唱过的歌》，并在歌曲的注释信息中添加了下载的来源地址。

3. 地址后面跟着的`m4a、aac和mp3`用来控制下载音频文件的类型。

<img src="https://i.loli.net/2021/11/28/TSIRH25DmjUX8po.png" alt="image-20211128141922577" style="zoom: 33%;" />

#### 批量下载

将需要下载的视频链接写在downloadlist.txt中`一行一个地写`，再运行下面的命令，就能将音频下载到当前目录下的download文件夹中。`如果批量下载运行出错，请先试试单个下载能不能正常工作`
```shell
python3 ASoulMP3maker.py -mp3
# 或者
python3 ASoulMP3maker.py -m4a
python3 ASoulMP3maker.py -aac
```
> 作者在downloadlist.txt中添加了几首歌作为测试，正式使用前可以删掉

#### 其他相关

1.   **音质**：似乎B站推流出来默认就是最高音质优先，我测试了一下下载的都是最高码率音频，每次。如果有问题请提issue。
2.   **流量**：只消耗打开b站网页版的流量和下载音频的流量，不产生下载视频画面的流量。
3.   **代码**：想在保持原有代码的结构的基础上完成这个项目，因此有的地方实现的不够优雅🧎‍♀️

#### TODO
1. GUI
2. 在长方形封面后加模糊叠底
3. 你来提

#### 原版下载器的功能

修改过程中删除了和视频油管的功能而保留了部分控制功能，如分p视频的下载等，具体可以查看对应版本的[README.md](https://github.com/JimmyLiang-lzm/biliDownloader/blob/91752cf232125e0d25ebc902d3c8abc2e9ebb2b3/README.md)，并配合python-argparse的help功能使用。

>   原版中的系统类型选项改为自动判断，不需要手动填写。

## 感谢

谢谢[JimmyLiang-lzm/biliDownloader)](https://github.com/JimmyLiang-lzm/biliDownloader)完成的基础工作，感谢豆瓣@喵呜提供的宝贵建议。

## 声明

本项目受GPL-3.0许可协议保护，所有程序仅用于学习与交流，请勿用于任何商业用途！
