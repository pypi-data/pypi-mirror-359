from openai import OpenAI
def ask(prompt):
    client = OpenAI(api_key="sk-f07c256885334df5aedbc8148807dad1", 
                    base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    answ = response.choices[0].message.content # 解析接口的返回值
    return answ
