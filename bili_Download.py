# This Python file uses the following encoding: utf-8
import os
import sys
import argparse
import requests
import re
import json
import html
from tqdm import tqdm
import subprocess

# Default Path
DF_Path = os.path.dirname(os.path.realpath(sys.argv[0]))

def make_a_parser(): 
    parser = argparse.ArgumentParser(description="Bilibili Video Downloader")
    parser.add_argument(
        "-a",
        "--address",
        dest="Address",
        type=str,
        default=None,
        action="store",
        help="Input the HTTP/HTTPS address of video page.",
    )
    parser.add_argument(
        "-o",
        "--output",
        dest="Output",
        type=str,
        default=DF_Path,
        action="store",
        help="Output folder location of Video(s).",
    )
    parser.add_argument(
        "-l",
        "--download-list",
        dest="DownList",
        type=str,
        default=None,
        action="store",
        help="The List of Download partition video.",
    )
    parser.add_argument(
        "-vq",
        "--video-quality",
        dest="VideoQuality",
        type=int,
        default=0,
        action="store",
        help='Videos quality. You can use "-c" or "--check" to view it, default is 0.',
    )
    parser.add_argument(
        "-ar",
        "--audio-quality",
        dest="AudioQuality",
        type=int,
        default=0,
        action="store",
        help='Audio quality. You can use "-c" or "--check" to view it, default is 0.',
    )
    parser.add_argument(
        "-c", "--check", action="store_true", help="Show video and audio download stream."
    )
    parser.add_argument(
        "-mp3",
        "--audio-mp3",
        dest="AudioMP3",
        action="store_true",
        help="download mp3 Audio Only",
    )
    parser.add_argument(
        "-m4a",
        "--audio-m4a",
        dest="AudioM4A",
        action="store_true",
        help="download m4a Audio Only",
    )
    parser.add_argument(
        "-aac",
        "--audio-aac",
        dest="AudioAAC",
        action="store_true",
        help="download aac Audio Only",
    )
    parser.add_argument(
        "-v", "--version", action="version", version="A-SoulMP3maker == 1.0"
    )
    return parser.parse_args()

args = make_a_parser()
assert args.Address is not None
# print(args)


class bili_downloader(object):
    # Parameter Initialize
    def __init__(self, args):
        self.index_url = args.Address
        self.d_list = args.DownList
        self.VQuality = args.VideoQuality
        self.AQuality = args.AudioQuality
        self.output = args.Output
        self.re_playinfo = "window.__playinfo__=([\s\S]*?)</script>"
        self.re_INITIAL_STATE = "window.__INITIAL_STATE__=([\s\S]*?);\(function"
        self.vname_expression = "<title(.*?)</title>"
        self.chunk_size = 1024
        self.index_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        self.second_headers = {
            "accept": "*/*",
            "Connection": "keep-alive",
            "accept-encoding": "identity",
            "accept-language": "zh-CN,zh;q=0.9",
            "origin": "https://www.bilibili.com",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
        }
        with open("setting.conf", "r", encoding="utf-8") as f:
            tempr = json.loads(f.read())
            self.index_headers["cookie"] = tempr["cookie"]
            self.second_headers["cookie"] = tempr["cookie"]
            self.systemd = sys.platform
            f.close()

    # File name conflict replace
    def name_replace(self, name):
        vn = name.replace(" ", "_").replace("\\", "").replace("/", "")
        vn = vn.replace("*", "").replace(":", "").replace("?", "").replace("<", "")
        vn = vn.replace(">", "").replace('"', "").replace("|", "")
        return vn

    # Change /SS movie address
    def ssADDRCheck(self, inurl):
        checking1 = re.findall("/play/ss", inurl.split("?")[0], re.S)
        checking2 = re.findall("/play/ep", inurl.split("?")[0], re.S)
        if checking1 != []:
            res = requests.get(inurl, headers=self.index_headers, stream=False)
            dec = res.content.decode("utf-8")
            INITIAL_STATE = re.findall(self.re_INITIAL_STATE, dec, re.S)
            temp = json.loads(INITIAL_STATE[0])
            self.index_url = temp["mediaInfo"]["episodes"][0]["link"]
            return 1, temp["mediaInfo"]["episodes"][0]["link"]
        elif checking2 != []:
            return 1, inurl
        else:
            return 0, inurl

    # Searching Key Word
    def search_preinfo(self, index_url):
        # Get Html Information
        index_url = self.ssADDRCheck(index_url)
        res = requests.get(index_url[1], headers=self.index_headers, stream=False)
        dec = res.content.decode("utf-8")
        # Use RE to find Download JSON Data
        playinfo = re.findall(self.re_playinfo, dec, re.S)
        # Get the url of video cover, add to self
        try:
            self.cover_url = re.findall(
                r"http://i..hdslb.com/bfs/archive/.*?\....", res.text
            )[0]
        except Exception as e:
            self.cover_url = None
            print("获取封面地址失败:", e)
        INITIAL_STATE = re.findall(self.re_INITIAL_STATE, dec, re.S)
        # If Crawler can GET Data
        if playinfo == [] or INITIAL_STATE == []:
            print("Session等初始化信息获取失败。")
            return 0, "", "", {}
        re_init = json.loads(INITIAL_STATE[0])
        re_GET = json.loads(playinfo[0])
        if index_url[0] == 0:
            now_cid = re_init["videoData"]["pages"][re_init["p"] - 1]["cid"]
            try:
                makeurl = (
                    "https://api.bilibili.com/x/player/playurl?cid="
                    + str(now_cid)
                    + "&qn=116&type=&otype=json&fourk=1&bvid="
                    + re_init["bvid"]
                    + "&fnver=0&fnval=976&session="
                    + re_GET["session"]
                )
                self.second_headers["referer"] = index_url[1]
                res = requests.get(
                    makeurl, headers=self.second_headers, stream=False, timeout=10
                )
                re_GET = json.loads(res.content.decode("utf-8"))
                # print(json.dumps(re_GET))
            except Exception as e:
                print("获取Playlist失败:", e)
                return 0, "", "", {}
        # If Crawler can GET Data
        try:
            # Get video name
            vn1 = re.findall(self.vname_expression, dec, re.S)[0].split(">")[1]
            vn1 = vn1.replace("_哔哩哔哩_bilibili", "")
            vn2 = ""
            if "videoData" in re_init:
                vn2 = re_init["videoData"]["pages"][re_init["p"] - 1]["part"]
            elif "mediaInfo" in re_init:
                vn2 = (
                    re_init["epInfo"]["titleFormat"]
                    + ":"
                    + re_init["epInfo"]["longTitle"]
                )
            video_name = self.name_replace(vn1) + "[" + self.name_replace(vn2) + "]"
            video_name = html.unescape(video_name)
            # List Video Quality Table
            temp_v = {}
            for i in range(len(re_GET["data"]["accept_quality"])):
                temp_v[str(re_GET["data"]["accept_quality"][i])] = str(
                    re_GET["data"]["accept_description"][i]
                )
            # List Video Download Quality
            down_dic = {"video": {}, "audio": {}}
            i = 0
            # Get Video identity information and Initial SegmentBase.
            for dic in re_GET["data"]["dash"]["video"]:
                if str(dic["id"]) in temp_v:
                    qc = temp_v[str(dic["id"])]
                    down_dic["video"][i] = [
                        qc,
                        [dic["baseUrl"]],
                        "bytes=" + dic["SegmentBase"]["Initialization"],
                    ]
                    for a in range(len(dic["backupUrl"])):
                        down_dic["video"][i][1].append(dic["backupUrl"][a])
                    i += 1
                else:
                    continue
            # List Audio Stream
            i = 0
            # re_GET["data"]["dash"]["audio"].sort(key=lambda t:t.bandwidth)
            for dic in re_GET["data"]["dash"]["audio"]:
                au_stream = dic["codecs"] + "  音频带宽：" + str(dic["bandwidth"])
                down_dic["audio"][i] = [
                    au_stream,
                    [dic["baseUrl"]],
                    "bytes=" + dic["SegmentBase"]["Initialization"],
                ]
                for a in range(len(dic["backupUrl"])):
                    down_dic["audio"][i][1].append(dic["backupUrl"][a])
                i += 1
            # Get Video Length
            length = re_GET["data"]["dash"]["duration"]
            # Return Data
            return 1, video_name, length, down_dic
        except Exception as e:
            print("PreInfo:", e)
            return 0, "", "", {}

        #

    def search_videoList(self, index_url):
        res = requests.get(index_url, headers=self.index_headers, stream=False)
        dec = res.content.decode("utf-8")
        INITIAL_STATE = re.findall(self.re_INITIAL_STATE, dec, re.S)
        if INITIAL_STATE != []:
            re_init = json.loads(INITIAL_STATE[0])
            init_list = {}
            if "videoData" in re_init:
                init_list["bvid"] = re_init["bvid"]
                init_list["p"] = re_init["p"]
                init_list["pages"] = re_init["videoData"]["pages"]
                return 1, init_list
            elif "mediaInfo" in re_init:
                init_list["bvid"] = re_init["mediaInfo"]["media_id"]
                init_list["p"] = re_init["epInfo"]["i"]
                init_list["pages"] = re_init["mediaInfo"]["episodes"]
                return 2, init_list
            else:
                return 0, {}
        else:
            return 0, {}

    # Show preDownload Detail
    def show_preDetail(self):
        # flag,video_name,length,down_dic,init_list = self.search_preinfo()
        temp = self.search_preinfo(self.index_url)
        preList = self.search_videoList(self.index_url)
        if temp[0] and preList[0] != 0:
            if preList[0] == 1:
                # Show video pages
                print("当前需要下载的BV号为：", preList[1]["bvid"])
                print("当前BV包含视频数量为%d个" % len(preList[1]["pages"]))
                print("-----------具体分P视频名称与下载号-----------")
                for sp in preList[1]["pages"]:
                    print("{}-->分P名称：{}".format(sp["page"], sp["part"]))
            elif preList[0] == 2:
                # Show media pages
                print("当前需要下载的媒体号为：", preList[1]["bvid"])
                print("当前媒体包含视频数量为%d个" % len(preList[1]["pages"]))
                print("-----------具体分P视频名称与下载号-----------")
                for sp in preList[1]["pages"]:
                    print("{}-->分P名称：{}".format(sp["title"], sp["share_copy"]))
            print("--------------------我是分割线--------------------")
            # Show Video Download Detail
            print("当前下载视频名称：", temp[1])
            print("当前下载视频长度： {} 秒".format(temp[2]))
            print("当前可下载视频流：")
            for i in range(len(temp[3]["video"])):
                print("{}-->视频画质：{}".format(i, temp[3]["video"][i][0]))
                ic = 1
                for bc_url in temp[3]["video"][i][1]:
                    print("	下载地址{}：{}".format(ic, bc_url.split("?")[0]))
                    ic += 1
            # Show Audio Download Detail
            print("--------------------我是分割线--------------------")
            print("当前可下载音频流：")
            for i in range(len(temp[3]["audio"])):
                print("{}-->音频编码：{}".format(i, temp[3]["audio"][i][0]))
                ic = 1
                for bc_url in temp[3]["audio"][i][1]:
                    print("	下载地址{}：{}".format(ic, bc_url.split("?")[0]))
                    ic += 1
        else:
            print("尚未找到源地址，请检查网站地址或充值大会员！")
            exit(1)

    # Download Stream fuction
    def d_processor(self, url_list, output_dir, output_file, dest) -> str:
        """
        函数返回值报告了下载流的码率
        """
        for line in url_list:
            print("使用线路：", line.split("?")[0])
            # 下载流信息
            try:
                # video stream length sniffing
                video_bytes = requests.get(
                    line, headers=self.second_headers, stream=False
                )
                vc_range = video_bytes.headers["Content-Range"].split("/")[1]
                print("获取{}流范围为：{}".format(dest, vc_range))
                print(
                    "{}文件大小：{} MB".format(
                        dest, round(float(vc_range) / self.chunk_size / 1024), 4
                    )
                )
                # Get the full video stream
                self.second_headers["range"] = "bytes=0" + "-" + vc_range
                m4sv_bytes = requests.get(
                    line, headers=self.second_headers, stream=True
                )
                pbar = tqdm(
                    total=int(vc_range),
                    initial=0,
                    unit="b",
                    leave=True,
                    desc="正在" + dest,
                    unit_scale=True,
                )
            except Exception as e:
                print("{}下载出错：{}".format(dest, e))
                os.remove(output_file)
                exit(1)
            try:
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                with open(output_file, "ab") as f:
                    for chunks in m4sv_bytes.iter_content(chunk_size=self.chunk_size):
                        if chunks:
                            f.write(chunks)
                            pbar.update(self.chunk_size)
                pbar.close()
            except Exception as e:
                print("{}写入出错：{}".format(dest, e))
                os.remove(output_file)
                exit(1)
            if os.path.getsize(output_file) != 0:
                print("{}成功！".format(dest))
                break
            else:
                print("下载失败，正在尝试下一条线路")

    # Convert m4s to other
    def ffmpeg_convertmp3(self, input_a, output_add, type, rate=-1):
        rate = str(int(rate) // 1000)
        if type == "aac":
            # aac和m4a不需要转码，改个后缀就行
            os.rename(input_a, output_add + ".aac")
        elif type == "m4a":
            os.rename(input_a, output_add + ".m4a")
        else:
            # 需要调用ffmpeg转码的参数
            if type == "mp3":
                fcommand = (
                    ('"' + input_a + '" ')
                    + "-loglevel quiet -c:a mp3 "
                    + "-ab "
                    + rate
                    + ('k "' + output_add + '.mp3"')
                )
            # 拼装ffmpeg和它的参数，然后执行
            ffcommand = self.where_ffmpeg() + fcommand
            try:
                print("启动ffmpeg:\t" + ffcommand)
                if subprocess.call(ffcommand, shell=True):
                    raise Exception("{} 执行失败。".format(ffcommand))
                print("音频转换完成！")
                os.remove(input_a)
            except Exception as e:
                print("音频转换失败：", e)
                exit(1)

    def where_ffmpeg(self) -> str:
        """
        返回可调用ffmpeg的命令
        """
        if self.systemd == "win32" and os.path.exists("./ffmpeg.exe"):
            ffpath = os.path.dirname(os.path.realpath(sys.argv[0]))
            return ffpath + r"/ffmpeg.exe -i "
        if subprocess.run("ffmpeg -version").returncode == 0:
            return "ffmpeg -i "
        else:
            print("无法确定FFMpeg命令。")
            exit(1)

    # Download Audio only
    def Download_audio(self, index="", type="m4a"):
        # Get video pre-detial
        if index == "":
            flag, self.video_name, _, down_dic = self.search_preinfo(self.index_url)
            index = self.index_url
        else:
            flag, self.video_name, _, down_dic = self.search_preinfo(index)
        # If we can access the video page
        if flag:
            # Judge file whether exists
            audio_dir = self.output + r"/" + self.video_name + "_audio.m4s"
            if os.path.exists(audio_dir[:-10] + r"." + type):
                print("音频文件：{}\n已存在,跳过下载。".format(audio_dir))
                exit(1)
            if os.path.exists(audio_dir):
                print("临时文件：{}\n已存在,删除后重新下载。".format(audio_dir))
                os.remove(audio_dir)
            print("需要下载的音频：", self.video_name)
            # Perform audio stream length sniffing
            self.second_headers["range"] = down_dic["audio"][self.AQuality][2]
            # Switch between main line and backup line(audio).
            self.d_processor(
                down_dic["audio"][self.AQuality][1], self.output, audio_dir, "下载音频"
            )
            Brate = re.findall("(?<=音频带宽：)\d*", down_dic["audio"][self.AQuality][0])[0]
            # Convert audio into mp3 (USE FFMPEG)
            # Convert audio m4s into mp3
            self.ffmpeg_convertmp3(
                audio_dir, self.output + r"/" + self.video_name, type, Brate
            )
            # Merge cover image to mp3 if exist
            cover_bytes = self.Download_cover()
            self.Merge_cover(type, cover_bytes)
            if int(Brate) < 156000:
                print("[warning]\t音频码率低，大约只有", int(Brate) // 1000, "kbps")
                exit(2)
        else:
            print("下载失败：尚未找到源地址，请检查网站地址或充值大会员！")
            exit(1)

    def Merge_cover(self, type, cover: bytes) -> None:
        import music_tag

        mysong = music_tag.load_file(self.output + r"/" + self.video_name + "." + type)
        if cover:
            mysong["artwork"] = cover
        mysong["title"] = self.video_name
        mysong["artist"] = "A-Soul"
        mysong["album"] = u"A-Soul唱过的歌"
        mysong["comment"] = u"来源：" + self.index_url
        mysong.save()

    # Downloads Cover only
    def Download_cover(self) -> bytes:
        if self.cover_url:
            cover = requests.get(self.cover_url, headers=self.index_headers)
        if cover.status_code == 200:
                return cover.content
        print("封面下载失败，跳过整合", self.cover_url)
        return None

    # Args to List
    def args2list(self):
        strlist = self.d_list.split(",")
        se_list = []
        for num in strlist:
            divi_num = num.split("-")
            if len(divi_num) == 1:
                se_list.append(int(divi_num[0]))
            elif len(divi_num) == 2:
                ovlist = list(map(int, divi_num))
                for i in range(ovlist[0], ovlist[1]):
                    se_list.append(i)
                se_list.append(ovlist[1])
            else:
                continue
        return se_list

    # For Download partition Video
    def Download_List(self):
        r_list = self.args2list()
        all_list = self.search_videoList(self.index_url)
        preIndex = self.index_url.split("?")[0]
        if all_list[0] == 1:
            if r_list[0] == 0:
                for p in all_list[1]["pages"]:
                    self.Download_audio(preIndex + "?p=" + str(p["page"]))
                print("列表视频下载完成！")
            else:
                listLEN = len(all_list[1]["pages"])
                for i in r_list:
                    if i <= listLEN:
                        self.Download_audio(preIndex + "?p=" + str(i))
                    else:
                        continue
                print("列表视频下载完成！")
        if all_list[0] == 2:
            if r_list[0] == 0:
                for p in all_list[1]["pages"]:
                    self.Download_audio(p["link"])
                print("媒体视频下载完成！")
            else:
                listLEN = len(all_list[1]["pages"])
                for i in r_list:
                    if i <= listLEN:
                        self.Download_audio(all_list[1]["pages"][i - 1]["link"])
                    else:
                        continue
                print("媒体视频下载完成！")
        else:
            print("未找到视频列表信息。")


if __name__ == "__main__":
    rundownloader = bili_downloader(args)
    if args.check:
        rundownloader.show_preDetail()
    elif args.AudioMP3:
        rundownloader.Download_audio(type="mp3")
    elif args.AudioM4A:
        rundownloader.Download_audio(type="m4a")
    elif args.AudioAAC:
        rundownloader.Download_audio(type="aac")
    elif args.DownList != None:
        rundownloader.Download_List()
    else:
        rundownloader.Download_audio(type="mp3")
