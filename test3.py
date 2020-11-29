#json string:
import json
import requests
data = [{'id': 'CET.AHU.Electricity.A3_转发通道1_A3E3222AA-3 IT机房设备服务器 研发楼机房自带控制箱3_正向有功电度', 'v': 48640, 'q': True, 't': 1592970636247},{'id': 'CET.AHU.Electricity.A2_A2N3112NM-A2E3221BM_A2E3221BD-3 服务器1_正向有功电度', 'v': 48640, 'q': True, 't': 1592970636247}]
s = json.loads('{"name":"test", "type":{"name":"seq", "parameter":["1", "2"]}}')

data2 = {"timestamp":12215,"values": [{'id': 'CET.AHU.Electricity.A3_转发通道1_A3E3222AA-3 IT机房设备服务器 研发楼机房自带控制箱3_正向有功电度', 'v': 48640, 'q': True, 't': 1592970636247},{'id': 'CET.AHU.Electricity.A2_A2N3112NM-A2E3221BM_A2E3221BD-3 服务器1_正向有功电度', 'v': 48640, 'q': True, 't': 1592970636247}]}
print(data2["values"])
# print(s)
# print(s.keys())
# print(s["name"])
# print(s["type"]["name"])
# print(s["type"]["parameter"][1])
print(data[0])
print(data[0]["v"])

# 遍历拿到值
print(len(data))
# 定义字典
context = []

for res in data2["values"]:
    print(res)
    DocumentList = {}
    id = res["id"]
    v = res["v"]
    q = res["q"]
    t = res["t"]

    # DocumentList["name"] = i[0]
    # DocumentList["num"] = i[1]
    # DocumentList["secret"] = i[2]
    #
    # context.append(DocumentList)
    print(id,v,q,t)

    d = {
        'id': id,
        'v': v,
        'q': q,
        't': t
    }
    response = requests.get('http://httpbin.org/get', params=d)
    print(response.text)


    # todo：套循环做拿到值调用接口数据
