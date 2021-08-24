import os,sys
import argparse
import requests,re,json
from tqdm import tqdm
import subprocess

# Default Path
DF_Path = os.path.dirname(os.path.realpath(sys.argv[0]))

parser = argparse.ArgumentParser(description='Bilibili Video Downloader')
parser.add_argument('-a','--address',dest='Address',type=str,default=None,action='store',help='Input the HTTP/HTTPS address of video page.')
parser.add_argument('-o','--output',dest='Output',type=str,default=DF_Path,action='store',help='Output folder location of Video(s).')
parser.add_argument('-vq','--video-quality',dest='VideoQuality',type=int,default=0,action='store',help='Videos quality. You can use "-c" or "--check" to view it, default is 0.')
parser.add_argument('-ar','--audio-quality',dest='AudioQuality',type=int,default=0,action='store',help='Audio quality. You can use "-c" or "--check" to view it, default is 0.')
parser.add_argument('-s','--synthesis',dest='Synthesis',type=int,default=1,choices=[0,1],help='Perform video synthesis after downloading audio and video streams.\nYou HAVE TO make sure FFMPEG executable program is exist.')
parser.add_argument('-c','--check',action='store_true',help='Show video and audio download stream.')
parser.add_argument('-v','--version',action='version',version='Bilibili Downloader == 1.0.0')
args = parser.parse_args()
assert not args.Address is None
#print(args)

class bili_downloader(object):
    # Parameter Initialize
    def __init__(self,args):
        self.index_url = args.Address
        self.VQuality = args.VideoQuality
        self.AQuality = args.AudioQuality
        self.output = args.Output
        self.synthesis = args.Synthesis
        self.re_expression = 'window.__playinfo__=([\s\S]*?)</script>'
        self.vname_expression = '<title(.*?)</title>'
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
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36"
        }
        with open('setting.conf', 'r', encoding='utf-8') as f:
            tempr = json.loads(f.read())
            self.index_headers["cookie"] = tempr["cookie"]
            self.second_headers["cookie"] = tempr["cookie"]
            self.systemd = tempr["sys"]
            f.close()

    # File name conflict replace
    def name_replace(self,name):
        vn = name.replace(' ', '_').replace('\\', '').replace('/', '')
        vn = vn.replace('*', '').replace(':', '').replace('?', '').replace('<', '')
        vn = vn.replace('>', '').replace('\"', '').replace('|', '')
        return vn

    # Searching Key Word
    def search_preinfo(self):
        # Get Html Information
        res = requests.get(self.index_url,headers=self.index_headers,stream=False)
        dec = res.content.decode('utf-8')
        if re.findall(self.re_expression, dec, re.S) != []:
            video_name = re.findall(self.vname_expression, dec, re.S)[0].split('>')[1]
            video_name = self.name_replace(video_name)
            re_GET = json.loads(re.findall(self.re_expression, dec, re.S)[0])
            # List Video Quality Table
            temp_v = {}
            for i in range(len(re_GET["data"]["accept_quality"])):
                temp_v[str(re_GET["data"]["accept_quality"][i])] = str(re_GET["data"]["accept_description"][i])
            # List Video Download Quality
            down_dic = {"video": {}, "audio": {}}
            i = 0
            # Get Video identity information and Initial SegmentBase.
            for dic in re_GET["data"]["dash"]["video"]:
                if str(dic["id"]) in temp_v:
                    qc = temp_v[str(dic["id"])]
                    down_dic["video"][i] = [qc, [dic["baseUrl"]], 'bytes=' + dic["SegmentBase"]["Initialization"]]
                    for a in range(len(dic["backupUrl"])):
                        down_dic["video"][i][1].append(dic["backupUrl"][a])
                    i += 1
                else:
                    continue
            # List Audio Stream
            i = 0
            for dic in re_GET["data"]["dash"]["audio"]:
                au_stream = dic["codecs"] + "  音频带宽：" + str(dic["bandwidth"])
                down_dic["audio"][i] = [au_stream, [dic["baseUrl"]],'bytes=' + dic["SegmentBase"]["Initialization"]]
                for a in range(len(dic["backupUrl"])):
                    down_dic["audio"][i][1].append(dic["backupUrl"][a])
                i += 1
            length = re_GET["data"]["dash"]["duration"]
            return True,video_name,length,down_dic
        else:
            return None,"","",{}

    # Show preDownload Detail
    def show_preDetail(self):
        #flag,video_name,length,down_dic = self.search_preinfo()
        temp = self.search_preinfo()
        if temp[0]:
            # Show Video Download Detail
            print('视频名称：', temp[1])
            print('视频长度： {} 秒'.format(temp[2]))
            print('可下载视频流：')
            for i in range(len(temp[3]["video"])):
                print("{}-->视频画质：{}".format(i, temp[3]["video"][i][0]))
                ic = 1
                for bc_url in temp[3]["video"][i][1]:
                    print("    下载地址{}：{}".format(ic, bc_url.split("?")[0]))
                    ic += 1
            # Show Audio Download Detail
            print('--------------------我是分割线--------------------')
            print('可下载音频流：')
            for i in range(len(temp[3]["audio"])):
                print("{}-->音频编码：{}".format(i, temp[3]["audio"][i][0]))
                ic = 1
                for bc_url in temp[3]["audio"][i][1]:
                    print("    下载地址{}：{}".format(ic, bc_url.split("?")[0]))
                    ic += 1
        else:
            print("尚未找到源地址，请检查网站地址或充值大会员！")


    # For Download
    def download(self):
        if os.path.exists(self.output + '/down_video.m4s'):
            print("文件：{}\n已存在。".format(self.output + '/down_video.m4s'))
            return -1
        if os.path.exists(self.output + '/down_audio.m4s'):
            print("文件：{}\n已存在。".format(self.output + '/down_audio.m4s'))
            return -1
        flag,video_name,_,down_dic = self.search_preinfo()
        # if os.path.exists(self.output + '/' + video_name + '.mp4'):
        #     print("文件：{}\n已存在。",self.output + '/' + video_name + '.mp4')
        if flag:
            print("需要下载的视频：",video_name)
            # Perform video stream length sniffing
            self.second_headers['referer'] = self.index_url
            self.second_headers['range'] = down_dic["video"][self.VQuality][2]
            # Switch between main line and backup line(video).
            for line in down_dic["video"][self.VQuality][1]:
                print('使用线路：',line.split("?")[0])
                try:
                    # video stream length sniffing
                    video_bytes = requests.get(line, headers=self.second_headers,stream=False)
                    vc_range = video_bytes.headers['Content-Range'].split('/')[1]
                    print("获取视频流范围为：", vc_range)
                    print('视频文件大小：{} MB'.format(round(float(vc_range) / self.chunk_size / 1024), 4))
                    # Get the full video stream
                    self.second_headers['range'] = 'bytes=0' + '-' + vc_range
                    m4sv_bytes = requests.get(line, headers=self.second_headers,stream=True)
                    pbar = tqdm(total=int(vc_range), initial=0, unit='b', leave=True, desc='正在下载视频', unit_scale=True)
                    with open(self.output + '/down_video.m4s', 'ab') as f:
                        for chunks in m4sv_bytes.iter_content(chunk_size=self.chunk_size):
                            if chunks:
                                f.write(chunks)
                                pbar.update(self.chunk_size)
                    pbar.close()
                    print("视频下载成功！")
                    break
                except Exception as e:
                    print("视频下载出错：",e)
                    os.remove(self.output + '/down_video.m4s')
            # Perform audio stream length sniffing
            self.second_headers['referer'] = self.index_url
            self.second_headers['range'] = down_dic["audio"][self.AQuality][2]
            # Switch between main line and backup line(audio).
            for line in down_dic["audio"][self.AQuality][1]:
                print('使用线路：', line.split("?")[0])
                try:
                    # video stream length sniffing
                    audio_bytes = requests.get(line, headers=self.second_headers, stream=False)
                    ac_range = audio_bytes.headers['Content-Range'].split('/')[1]
                    print("获取视频流范围为：", ac_range)
                    print("音频文件大小：{} MB".format(round(float(ac_range) / self.chunk_size / 1024), 4))
                    # Get the full audio stream
                    self.second_headers['range'] = 'bytes=0' + '-' + ac_range
                    m4sa_bytes = requests.get(line, headers=self.second_headers, stream=True)
                    pbar = tqdm(total=int(ac_range), initial=0, unit='b', leave=True, desc='正在下载音频', unit_scale=True)
                    with open(self.output + '/down_audio.m4s', 'ab') as f:
                        for chunks in m4sa_bytes.iter_content(chunk_size=self.chunk_size):
                            if chunks:
                                f.write(chunks)
                                pbar.update(self.chunk_size)
                    pbar.close()
                    print("音频下载成功！")
                    break
                except Exception as e:
                    print("音频下载出错：",e)
                    os.remove(self.output + '/down_audio.m4s')
            # Merge audio and video (USE FFMPEG)
            if self.synthesis:
                input_v = self.output + '/down_video.m4s'
                input_a = self.output + '/down_audio.m4s'
                output_add = self.output + '/' + video_name + '.mp4'
                print('正在启动ffmpeg......')
                ffcommand = ""
                if self.systemd == "windows":
                    ffpath = os.path.dirname(os.path.realpath(sys.argv[0]))
                    ffcommand = ffpath + '/ffmpeg.exe -i ' + input_v + ' -i ' + input_a + ' -c:v copy -c:a aac -strict experimental ' + output_add
                elif self.systemd == "linux":
                    ffcommand = 'ffmpeg -i' + input_v + ' -i ' + input_a + ' -c:v copy -c:a aac -strict experimental ' + output_add
                else:
                    print("未知操作系统：无法确定FFMpeg命令。")
                    return -2
                try:
                    if subprocess.call(ffcommand, shell=True):
                        raise Exception("{} 执行失败。".format(ffcommand))
                    print("视频合并完成！")
                    os.remove(input_v)
                    os.remove(input_a)
                except Exception as e:
                    print("视频合成失败：", e)
        else:
            print("下载失败：尚未找到源地址，请检查网站地址或充值大会员！")

if __name__ == '__main__':
    rundownloader = bili_downloader(args)
    if args.check:
        rundownloader.show_preDetail()
    else:
        rundownloader.download()
