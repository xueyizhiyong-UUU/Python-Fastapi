import json
b = {"name":"xiaohong",
     "age": 18}

def WriteJson():

    with open("readme.json",'r') as f:
        temp = json.loads(f.read())
        print(temp["usersecret0"])
        # print(temp["usersecret0"]["documentsecret1"])

        print(type(temp["usersecret0"]["documentsecret1"]))
        b.update(temp["usersecret0"]["documentsecret1"])
        print(b)
        return temp["usersecret0"]["documentsecret0"]

a = WriteJson()
