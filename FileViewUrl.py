from fastapi import FastAPI
from starlette.responses import RedirectResponse
import uvicorn
import requests
import pymysql
import datetime
import hashlib
import configparser
import uvicorn.logging
import uvicorn.loops
import uvicorn.loops.auto
import uvicorn.protocols
import uvicorn.protocols.websockets
import uvicorn.protocols.websockets.auto
import uvicorn.protocols.http
import uvicorn.protocols.http.auto
import uvicorn.lifespan
import uvicorn.lifespan.on
import uvicorn.lifespan.off
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from idna.core import unicode

app = FastAPI()
origins = [
    "http://127.0.0.1:8080",
    "http://127.0.0.1"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# md5加密
def encryptByMD5(myString):
    # print('myString:'+myString)
    getMD5fromSrv = "http://127.0.0.1:8080/ckapi/api/md5.jsp"
    params = {"str": myString}
    try:
        MD5FromSrv = requests.get(url=getMD5fromSrv, params=params).json()
    except Exception as e:
        print(e)
        return ""
    if MD5FromSrv["code"] != 0:
        return ""
    finalMD5Str = MD5FromSrv["data"]
    # print('finalMD5Str:'+finalMD5Str)
    return finalMD5Str


class DBUtil():
    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read("config.ini")
        self.host = conf.get("DataBase", "host")
        self.port = int(conf.get("DataBase", "port"))
        self.database = conf.get("DataBase", "database")
        self.user = conf.get("DataBase", "user")
        self.password = conf.get("DataBase", "password")
        self.conn = None
        self.cur = None

    def ConnectTODB(self):
        flag = False
        try:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, password=self.password,
                                        database=self.database)
            self.cur = self.conn.cursor()
            flag = True
        except Exception as e:
            print(e)
            return flag
        return flag

    def disConnDB(self):
        if self.cur != None:
            self.cur.close()
        if self.conn != None:
            self.conn.close()


    # 获取在线预览url
    def mysqlMethod(self, documentNumber, userID):
        # result_list=[]#定义列表
        # 获取服务器地址
        self.cur.execute("select skf991,skf689 from skt57")  # 获取服务器地址和单位号
        result = self.cur.fetchone()  # 取一条结果集
        url = result[0]  # 服务器地址
        Unit_number = result[1]  # 单位号

        # print(Unit_number)

        # 获取用户user
        User_SQL = "SELECT USER FROM tblemployee WHERE id='%s'" % userID
        # print(User_SQL)
        self.cur.execute(User_SQL)  # 获取User
        result = self.cur.fetchone()  # 取一条结果集
        User = result[0]  # 附件版本编号
        # print(User)

        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print('当前服务器时间：'+now_time)

        # todo 档案版本都是空，因为不需要更新

        # 获取附件路径
        Route_SQL = "SELECT skf377 FROM skt28 WHERE skf906='%s'" % documentNumber
        # print(Route_SQL)
        self.cur.execute(Route_SQL)  # 获取路径
        result = self.cur.fetchone()  # 取所有结果集
        Route = result[0]
        # print(Route)
        url = url + 'SK_CFW_Servlet.do?method=filedownload&action=directpreview&domainid=' + Unit_number + '&userid=' + userID + '&timestamp=' + now_time + '&filepath=' + Route + '&data='
        # print('拼接URL：'+url)

        BeforeMD5 = Unit_number + userID + now_time + '30' + Route + '0020182018'
        # print('BeforeMD5:'+BeforeMD5)
        finalUrl = url + encryptByMD5(BeforeMD5) + '&time=30&isShowPrint=0&isShowLoadFile=0'
        # print('finalUrl:'+finalUrl)
        # finalUrl="http://www.baidu.com"

        return finalUrl


# class Preview(BaseModel):
#     # 用户id
#     userID: str = ""
#
#     # 文档编号
#     documentNumber: str = ""
#


@app.get("/ck/service/getPreviewUrl")
def getPreviewUlr(userID: str,documentNumber: str):
    dbutil = DBUtil()
    # print(preview.borrowingNum)
    # print(type(is_document))
    if dbutil.ConnectTODB():
        finalUrl = dbutil.mysqlMethod(documentNumber, userID)
        # print("链接数据库")
        # results = {"code": 0, "data": [{"url": finalUrl}], "msg": "成功"}
        return RedirectResponse(finalUrl)
        # return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)

