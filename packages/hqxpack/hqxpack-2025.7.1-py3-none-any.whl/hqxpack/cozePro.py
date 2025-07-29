import requests
import json
def help():
    text = '''
        系统介绍：
            coze官网：https://www.coze.cn/
            通过API方式访问cozeAI,支持将cozeAI部署到开发者自己的应用中
        令牌与ID：
            1、需要更新token与id
            2、token获取网址：https://www.coze.cn/open/api
                需要先登录自己的coze账户,点击添加新令牌，生成token
                注意：每个token只显示一次，需要及时复制并保存
            3、id：
                选择个人中心或团队空间的bots,点击进入后，可在url中获取
                例如：
                https://www.coze.cn/space/7357362486913564724/bot/7384409533428416575
                其中/bot/后的数字就是id
        操作：
            from hqx import coze             # 导入coze工具包
            coze.help()                      # 获取帮助，打印coze库的介绍
            robot1 = coze.Coze(token="xxx",id="xxx") # 创建智能体，可以重复调用创建多个
            robot2 = coze.Coze()
            robot2.id = "xxx"    # id与token也可以创建后再进行修改
            robot2.token = "xxx"
            ans = robot2.ask("your question") # 发起询问
            print(ans)
    '''
    print(text)

class Coze():

    def __init__(self,token="pat_wMyx905BAlhgqkmXRn0cimzijggm0VWkcMqgKcAEg6Twq6CwNStKzEQaPifLhPjr",id="7384409533428416575") -> None:
        self.url = "https://api.coze.cn/open_api/v2/chat"
        self.token = token
        self.id = id

    def help(self):
        text = '''
        系统介绍：
            coze官网：https://www.coze.cn/
            通过API方式访问cozeAI,支持将cozeAI部署到开发者自己的应用中
        令牌与ID：
            1、需要更新token与id
            2、token获取网址：https://www.coze.cn/open/api
                需要先登录自己的coze账户,点击添加新令牌，生成token
                注意：每个token只显示一次，需要及时复制并保存
            3、id：
                选择个人中心或团队空间的bots,点击进入后，可在url中获取
                例如：
                https://www.coze.cn/space/7357362486913564724/bot/7384409533428416575
                其中/bot/后的数字就是id
        操作：
            from hqx import coze             # 导入coze工具包
            coze.help()                      # 获取帮助，打印coze库的介绍
            robot1 = coze.Coze(token="xxx",id="xxx") # 创建智能体，可以重复调用创建多个
            robot2 = coze.Coze()
            robot2.id = "xxx"    # id与token也可以创建后再进行修改
            robot2.token = "xxx"
            ans = robot2.ask("your question") # 发起询问
            print(ans)
    '''
        print(text)
    def ask(self,question):
        headers = {
            #                        pat开始就是你的API令牌，需要自行创建
            "Authorization": "Bearer "+self.token, 
            "Content-Type": "application/json",
            "Accept": "*/*",
            "Host": "api.coze.cn",
            "Connection": "keep-alive"
        }
        data = {
            "conversation_id": "101",
            "bot_id": self.id, # 这里更换bot的id，进入你的bot，url中bot后的数字就是id
            "user": "hqx",
            "query":question,
            "stream": False
        }
        response = requests.post(self.url, headers=headers, data=json.dumps(data))
        msg = response.json()
        try:
            for i in msg['messages']:
                if i['type']=='answer':
                    return i['content']
        except:
            pass
        return '询问失败'
        

