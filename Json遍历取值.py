# coding:utf-8
import requests
import json

key_list = []
def get_dict_allkeys(dict_a):
    """
    遍历嵌套字典，获取json返回结果的所有key值
    :param dict_a:
    :return: key_list
    """
    if isinstance(dict_a, dict):  # 使用isinstance检测数据类型
        # 如果为字典类型，则提取key存放到key_list中
        for x in range(len(dict_a)):
            temp_key = list(dict_a.keys())[x]
            temp_value = dict_a[temp_key]
            key_list.append(temp_key)
            get_dict_allkeys(temp_value)  # 自我调用实现无限遍历
    elif isinstance(dict_a, list):
        # 如果为列表类型，则遍历列表里的元素，将字典类型的按照上面的方法提取key
        for k in dict_a:
            if isinstance(k, dict):
                for x in range(len(k)):
                    temp_key = list(k.keys())[x]
                    temp_value = k[temp_key]
                    key_list.append(temp_key)
                    get_dict_allkeys(temp_value) # 自我调用实现无限遍历
    return key_list

def getJson():
    url = 'http://127.0.0.1:8080/ckapi/api/1/v2/sksearch_info.jsp'
    print(url)
    params={"token": "chenksoft!@!",
            "search_id": "2020080400002-5"}
    response = requests.get(url=url, params=params)
    response.encoding = 'utf-8'

    data = response.text
    dictdata = json.loads(data)
    print(type(dictdata))
    return dictdata

if __name__=="__main__":
    data = getJson()
    # 获取得到的dict形式 data数据
    print(data)
    get_keys = get_dict_allkeys(data)
    print(get_keys)