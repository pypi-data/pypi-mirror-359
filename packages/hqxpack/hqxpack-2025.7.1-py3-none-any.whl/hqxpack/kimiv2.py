from openai import OpenAI
from pathlib import Path
def kimi(apikey,que):
    client = OpenAI(
        api_key=apikey,
        base_url="https://api.moonshot.cn/v1",
    )

    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {"role": "system",
             "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
            {"role": "user", "content": que}
        ],
        temperature=0.3,
    )

    print(completion.choices[0].message.content)
def kimifile(apikey,que,filepath):
    clientfile = OpenAI(
        api_key=apikey,
        base_url="https://api.moonshot.cn/v1",
    )


    file_object = clientfile.files.create(file=Path(filepath), purpose="file-extract")


    file_content = clientfile.files.content(file_id=file_object.id).text


    messages = [
        {
            "role": "system",
            "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
        },
        {
            "role": "system",
            "content": file_content,
        },
        {"role": "user", "content": que},
    ]

    completion = clientfile.chat.completions.create(
        model="moonshot-v1-32k",
        messages=messages,
        temperature=0.3,
    )


    print(completion.choices[0].message)
def help():
    text = '''
    用法：from hqx import kimi
         kimi.kimi('这里填API','这里填问题')
    或使用文件接口
        from hqx import kimi
        kimi.kimifile('这里填API','这里填问题','这里填文件名')
    请注意，本插件无法在使用代理的情况下工作
    使用文件接口需把要发给Kimi智能助手的文件放在与代码相同的路径下
    文件接口与 Kimi 智能助手中上传文件功能所使用的相同，支持相同的文件格式，它们包括 .pdf .txt .csv .doc .docx .xls .xlsx .ppt .pptx 
    .webp .ico .xbm .dib .pjp .tif .pjpeg .avif .dot .apng .epub .tiff .jfif .html .json .mobi 
    .log .go .h .c .cpp .md .jpeg .png .bmp .gif .svg .svgz .cxx .cc .cs .java .js .css 
    .jsp .php .py .py3 .asp .yaml .yml .ini .conf .ts .tsx 等格式。
    '''
    print(text)