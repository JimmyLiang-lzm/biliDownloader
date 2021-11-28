## 项目介绍

为了方便下载的ASoul唱过的歌，并且在MP3或者iTunes里能有一个好看的封面和完善的歌曲信息，本项目在[JimmyLiang-lzm/biliDownloader（基于版本:5f61cae5fa016c591f57a5553fe6faf9fddf6493）](https://github.com/JimmyLiang-lzm/biliDownloader)的基础上增加修改了一些功能，完成了一个专用于下载A-Soul成员在B站上的投稿视频并转换为带标签MP3的工具。

>   不知道提供下载会不会构成侵权，先给小伙伴们说一声对不起🙇←🏃

## ASoulMP3maker

### 安装

在python的3.8和3.9下测试通过，理论上python3都可以用，使用前请先安装对应的python库并切换工作目录。

```shell
cd ASoulMP3maker
pip install -r requirements.txt
```

-   **Windows部署**：
    1. 需要手动进行**FFMpeg**程序的下载，👉[点击这里](http://ffmpeg.org/download.html)👈进入官网进行下载。
    1. 将下载的压缩包解压后，复制压缩文件中的`ffmpeg.exe`并粘贴到`ASoulMP3maker`程序根目录下即可。
-   **Linux和Mac OS部署**：
    1.   借助apt、brew等包管理工具安装。

### 使用

#### 下载单个视频并转换

```shell
python3 bili_Download.py -a [HTTPAddress] -mp3
# 或者
python3 bili_Download.py -a [HTTPAddress] -m4a
```
1.   将`[HTTPAddress]`换成你要下载的视频地址，如`https://www.bilibili.com/video/BV1ER4y1E7qn`

2.  在某一次更新中增加了补充歌手名称和专辑名称功能。将歌手名固定为A-Soul，专辑名为《A-Soul唱过的歌》，并在歌曲的注释信息中添加了下载的来源地址。

3. 参数的m4a和mp3用来控制下载音频文件的类型

<img src="https://i.loli.net/2021/11/28/TSIRH25DmjUX8po.png" alt="image-20211128141922577" style="zoom: 33%;" />

#### 批量下载

将需要下载的视频链接写在downloadlist.txt中，再运行下面的命令，就能将音频下载到当前目录下的download文件夹中。
```shell
python3 ASoulMP3maker.py -mp3
# 或者
python3 ASoulMP3maker.py -m4a
```
> 作者在downloadlist.txt中添加了几首歌作为测试，正式使用前可以删掉

#### 其他相关

1.   **音质**：似乎B站推流出来默认就是最高音质优先，我测试了一下下载的都是最高码率音频。如果有问题请提issue。
2.   **流量**：只消耗打开b站网页版的流量和下载音频的流量，不产生下载视频画面的流量。



#### 原版下载器的功能

修改过程中保留了[JimmyLiang-lzm/biliDownloader（版本:5f61cae5fa016c591f57a5553fe6faf9fddf6493）](https://github.com/JimmyLiang-lzm/biliDownloader)中的所用功能，可以查看对应版本的[README.md](https://github.com/JimmyLiang-lzm/biliDownloader/blob/91752cf232125e0d25ebc902d3c8abc2e9ebb2b3/README.md)使用。

>   原版中的系统类型选项改为自动判断，不需要手动填写。

## 感谢

谢谢[JimmyLiang-lzm/biliDownloader)](https://github.com/JimmyLiang-lzm/biliDownloader)完成的基础工作。

## 声明

本项目受GPL-3.0许可协议保护，所有程序仅用于学习与交流，请勿用于任何商业用途！
