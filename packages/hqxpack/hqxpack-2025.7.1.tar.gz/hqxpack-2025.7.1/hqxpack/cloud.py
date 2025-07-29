import requests as r
string = '''from hqx import gpt 
gpt.appid = '510db3c5'
gpt.api_secret = 'MTE3YjcyMjk4NzdiMmIwOGQ0NzI4N2Zh'
gpt.api_key = '7af8b13e405dfdfc4e5a75f35c00d459'
'''
def post(string=string):
    html = f'''
    <pre>
        {string}
    </pre>
'''
    r.post('http://120.26.43.1:7000',data=html.encode())
    print('http://120.26.43.1:7000')
