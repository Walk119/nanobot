import requests
import json
def baidu_search():
    '''
    curl --location 'https://qianfan.baidubce.com/v2/ai_search/web_search' \
--header 'X-Appbuilder-Authorization: Bearer <您的API Key>' \
--header 'Content-Type: application/json' \
--data '{"messages":[{"content":"搜索关键词","role":"user"}],"search_source":"baidu_search_v2"}'<sup>3</sup>
    :return:
    '''
    url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
    header = {
    'X-Appbuilder-Authorization':"Bearer bce-v3/ALTAK-e85us8SJVDyv0hVuwdfsA/c5923d943b84a1a98d0013c18ba8446ad41f839d",
        "Content-Type": "application/json"
    }
    params = {
           "messages": [
    {
      "content": "河北各个城市最近的天气",
      "role": "user"
    }
  ],
  "search_source": "baidu_search_v2",
  "resource_type_filter": [{"type": "web","top_k": 10}],
  "search_filter": {
    "match": {
      "site": [
        "www.weather.com.cn"
      ]
    }
  },
  "search_recency_filter": "year"
        }
    res = requests.post(url, data=json.dumps(params), headers=header, verify=False)
    print(res)
    print(res.text)