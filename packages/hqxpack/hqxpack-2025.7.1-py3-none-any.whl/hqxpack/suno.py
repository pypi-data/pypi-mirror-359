import http.client
import json
import time
import requests

apiid = '155483848179675738'
token = 'sk-4B8D896C31404B34848EDD802A332796'
def create(msg,audiopath,videopath):
    def check(data):
        if 'null' in data:
            data = data.replace('null','"null"')
        if 'false' in data:
                data = data.replace('false','"false"')
        if 'true' in data:
            data = data.replace('true','"true"')
        return data

    conn = http.client.HTTPSConnection("suno.x-mi.cn")
    payload = json.dumps({
        "inputType": 10,
        "mvVersion": "chirp-v3-alpha",
        "makeInstrumental": 0,
        "action": "generate",
        "idea": msg
    })
    headers = {
        'x-apiid': apiid,
        'x-token': token,
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/apiclouds/v1/suno/generate", payload, headers)
    res = conn.getresponse()
    data = res.read().decode('utf-8')
    data = check(data)
    data = eval(data)
    print(type(data),data)

    print("------项目构建成功------")
    payload = json.dumps({
        "id": data['data']['id']
    })
  

    print('------开始查询进度------')
    while True:
        time.sleep(5)
        conn.request("POST", "/apiclouds/v1/suno/query", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        data = check(data)
        data = eval(data)
        if data['data']['list'][0]['progress'] == '100%':
            break
        print('当前进度：',data['data']['list'][0]['progress'])
    print('------已完成，开始下载文件------')
    audioUrl = data['data']['list'][0]['audioUrl']
    videoUrl = data['data']['list'][0]['videoUrl']
    print("音频地址：",audioUrl)
    print("视频地址：",videoUrl)
    audioPath =  audiopath # 保存到本地的文件名
    videPath = videopath # 保存到本地的文件名
    def download_video(url, audioPath):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(audioPath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    def download_mp3(url, videPath):
        response = requests.get(url)
        response.raise_for_status()
        with open(videPath, 'wb') as f:
            f.write(response.content)

    download_mp3(audioUrl, audioPath)
    download_video(videoUrl, videPath)
    print('------文件已下载------')