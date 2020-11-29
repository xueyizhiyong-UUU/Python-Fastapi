#数据库查询结果，用json返回
import json
import requests

# 调用三个存储过程
ListURL1 = "http://172.18.2.216:8081/ckapi/api/1/v2/SKupdate_list_id.jsp"
ListURL2 = "http://172.18.2.216:8081/ckapi/api/1/v2/SKupdate_power.jsp"
ListURL3 = "http://172.18.2.216:8081/ckapi/api/1/v2/SKupdate_mylist.jsp"
params1 = {'token': "chenksoft!@!",
           'list_id': 86}
params2 = {'token': 'chenksoft!@!',
           'list_id': 86,
           'loge_user': 5
           }
params3 = {'token': 'chenksoft!@!',
           'list_id': 86}
try:
    res1 = requests.get(url=ListURL1, params=params1).json()
    res2 = requests.get(url=ListURL2, params=params2).json()
    res3 = requests.get(url=ListURL3, params=params3).json()

except Exception as e:
    print(e)
