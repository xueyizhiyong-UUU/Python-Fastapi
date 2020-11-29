
import requests
import uvicorn

import json


def getJson():
    url = 'http://127.0.0.1:8080/ckapi/api/1/v2/sksearch_info.jsp'
    params={"token": "chenksoft!@!",
            "search_id": "2020080400002-5"}
    response = requests.get(url=url, params=params)
    response.encoding = 'utf-8'

    data = response.text
    dictdata = json.loads(data)
    print(type(dictdata))
    print(dictdata.keys())
    context = {"preview": 1,
               "borrow": 1,
               "print": 1,
               "download": 1
               }
    for i in dictdata["data"]:
        print(i["skt1.skf16"])
        # 拼接字典
        i.update(context)

    print(dictdata)

getJson()
