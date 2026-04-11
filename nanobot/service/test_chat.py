import requests

def test_chat():
    url = "http://127.0.0.1:8000/api/skills/agent/chat"
    data = {
        "message": "帮我整理一下近期中东的局势信息",
    }
    res = requests.post(url, json=data)
    print('-'*200)
    print(res)
    print(res.text)
    print(res.json())
    print('+'*200)