# Bilibili Video Downloader😀

[![maven](https://img.shields.io/badge/Python-3.8.8-blue.svg)](https://www.python.org/)  [![mavel](https://img.shields.io/badge/GPL-3.0-red.svg)](https://github.com/JimmyLiang-lzm/biliDownloader/blob/master/LICENSE) ![mavel](https://img.shields.io/badge/requests-2.26.0-green.svg) ![mavel](https://img.shields.io/badge/tqdm-4.62.1-green.svg) 

## feature✨

1. This program is written based on `Python 3.8.8`, the code is readable and easy to transplant;
2. Parameters can be used for direct control, which is convenient for use in server; 
3. Only one line of code is needed to download the video, omitting tedious operations;
4. Automatically synthesize video, and also can separate audio and video for download;
5. Can obtain audio and video streams of different definitions, and can be selectively downloaded;
6. If the main download line is blocked during the download process, the software will automatically select the alternate line for downloading;
7. Can download paid cartoon or VIP high-quality video (Updated 2021-10-06);
8. Downloadable segmented video batches (Updated 2021-10-06);
9. Downloadable interactive video (Updated 2021-10-22).


## How to use?🕹

### 1. Installation and use in Python environment

**Installation**:

1. First make sure that your Python version is 3.8.8 or above, and then build the environment according to the following code;

```shell
git clone https://github.com/JimmyLiang-lzm/biliDownloader.git
cd biliDownloader
pip3 install -r requirements.txt
```

2. Download the **FFMpeg** program, 👉[click here](http://ffmpeg.org/download.html) 👈 and enter the official website to download:

   * **Windows deployment**: After decompressing the downloaded compressed package, copy the `ffmpeg.exe` from the compressed file and paste it into the root directory of the `biliDownloader` program.
   * **Ubuntu deployment: **You can use the following code for simple installation. If you need to use a latest version, please download and compile it from the official website.

   ```shell
   sudo add-apt-repository -y ppa:djcj/hybrid
   sudo apt update
   sudo apt install -y ffmpeg
   ```

3. Change the initialization parameters, enter the `setting.conf` file in the root directory, and modify the `XXX` in `"sys":"XXX"` to the system platform you are using. Please change to `windows` when using Windows platform, and change to `ubuntu` when using Ubuntu platform.

**Use:**

You can directly use the following code to view the video download address, where `HTTPAddress` represents the web page address:

```shell
python3 bili_Download.py -a HTTPAddress -c
```

You can directly use the following code to download, `OutputPath` represents the output folder:

```shell
python3 bili_Download.py -a HTTPAddress -o OutputPath
```

### 2. Installation and use under Windows

**Installation:**

1. Enter the **release** from this project to download, and unzip after downloading;
2. Download the **FFMpeg** program, 👉[click here](https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-2021-08-14-git-acd079843b-full_build.7z)👈 to download. After finished, unzip "bin->ffmpeg.exe" to the "bili_Download" folder.
3. Change the initialization parameters. Open the `setting.conf` file in the root folder `bili_Download`, and modify the `XXX` in `"sys":"XXX"` to `windows`.

**Use:**

In order to facilitate use in Windows, please click on batch script `Start.bat` in the unzipped directory. To check the video download address, you can directly use the following code to view, where `HTTPAddress` represents the web page address:

```shell
bili_Download.exe -a HTTPAddress -c
```

You can directly use the following code to download, `OutputPath` represents the output folder:

```shell
bili_Download.exe -a HTTPAddress -o OutputPath
```

If you **DO NOT** use batch scripts, you need to add **absolute address** before `bili_Download.exe`.

## Parameters🛠

In order to use this program correctly, the parameters are as follows:

* `-a`, `--address`: Enter the HTTP/HTTPS address of the video page, if the parameter does not contain `-v`, `--version`, `-h`, `--help`, then this item is required;
* `-o`, `--output`: Download the video to the local output folder address, the default value is the program root directory;
* `-vq`, `--video-quality`: Select the video resolution, accept the data type as integer data, you can use `-c` or `--check` to view, the default value is **0**;
* `-ar`, `--audio-quality`: Select audio quality, accept data type as integer data, you can use `-c` or `--check` to view, the default value is **0**;
* `-s`, `--synthesis`: Whether to perform synthesis after the video is downloaded, only `0` or `1` is supported. Among them, `0` means no synthesis, `1` means synthesis; the default value is ``1``; **this The option can only be realized after the deployment of FFMpeg!**
* `-c`, `--check`: Check whether there are audio streams and video streams available for download on the video page, and display them; when this parameter appears, no video download will be performed;
* `-i`, `--interact`: Download the entire interactive video;
* `-v`, `--version`: View software version information;
* `-h`, `--help`: Display software help information.

## About VIP video download

VIP video download has been updated on **October 6, 2021**, you can paste your VIP cookie into the XXX of the root directory `setting.conf` file `"cookie":"XXX"`. You can try to use `-c`, `--check` to check. How to get cookies please [click here](https://jimmyliang-lzm.github.io/2021/10/05/Get_bilibili_cookie/)🤞

## Declaration⚖

This project is protected by the **GPL-3.0** license agreement, all programs are only used for learning and communication, please **DO NOT** use it for any commercial purposes!

## Sponsor🤝

💖💖If you find this program useful, please don’t hesitate to leave a **Star** or **fork**, thank you very much!💖💖