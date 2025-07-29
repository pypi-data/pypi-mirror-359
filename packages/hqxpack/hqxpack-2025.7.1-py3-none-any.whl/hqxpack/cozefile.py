import requests
import json
import base64

def file_to_base64(file_path):
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read())
    return encoded_string.decode('utf-8')

token = "pat_Syzvn1TIopTodFAUxzKrT29cPqfVhrwG55VqwKn6D4OCVt4r4j47ysaSrncIrX9I"
data_id = "7435529655661133875"

def upload(filepath,filetype):
    headers = {
        'Authorization': 'Bearer '+token,
        'Content-Type': 'application/json',
        'Agw-Js-Conv': 'str'
    }
    data = {
        "dataset_id": data_id,
        "document_bases": [
            {
                "name": filepath,
                "source_info": {
                    "file_base64": file_to_base64(filepath),
                    "file_type": filetype
                }
            }
        ],
        "chunk_strategy": {
            "separator": "========",
            "max_tokens": 800,
            "remove_extra_spaces": False,
            "remove_urls_emails": False,
            "chunk_type": 1
        }
    }
    url = 'https://api.coze.cn/open_api/knowledge/document/create'
    response = requests.post(url, headers=headers, json=data)
    print(response.status_code)
    return response.json()

def delete(doc_id):
    headers = {
        'Authorization': 'Bearer '+token,
        'Content-Type': 'application/json',
        'Agw-Js-Conv': 'str'
    }

    # 定义请求的 URL
    url = 'https://api.coze.cn/open_api/knowledge/document/delete'

    # 定义请求的数据
    data = {
        "document_ids": [
            doc_id
        ]
    }
    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data))
    # 打印响应内容
    print(response.status_code)
    print(response.json())

