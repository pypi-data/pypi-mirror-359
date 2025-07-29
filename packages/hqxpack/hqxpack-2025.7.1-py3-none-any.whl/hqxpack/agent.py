import requests


class Agent():
    def __init__(self,appid= 'tnf39I7NQBuNhpL3BTxgr4pNE4Aj0r1n',appkey= 'NTIoUximpp2tMAHXjjbwZfhPQ9H534nU') -> None:
        self.appid = appid
        self.appkey = appkey
        self.url = "https://openapi.baidu.com/rest/2.0/lingjing/assistant/getAnswer"
        tkUrl = f"https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.appid}&client_secret={self.appkey}"
        res = requests.get(tkUrl).json()
        self.access_token = res['access_token']
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        self.data = {
            "message": '{"content": {"type": "text", "value": {"showText": "科创赛有哪些赛道"}}}',
            "source": "*",
            "from": "*",
            "openId": "*"
        }
        self.params = {
            'access_token':self.access_token
        }
    def updateToken(self):
        tkUrl = f"https://openapi.baidu.com/oauth/2.0/token?grant_type=client_credentials&client_id={self.appid}&client_secret={self.appkey}"
        res = requests.get(tkUrl).json()
        self.access_token = res['access_token']
        self.params = {
            'access_token':self.access_token
        }
    def ask(self,question):
        try:
            question = question.replace('\n',' ')
        except:
            pass
        self.data = {
            "message": '{"content": {"type": "text", "value": {"showText": "'+question+'"}}}',
            "source": "*",
            "from": "*",
            "openId": "*"
        }
        response = requests.post(self.url, headers=self.headers, data=self.data, params=self.params)
        return response.json()['data']['content'][0]['data']
