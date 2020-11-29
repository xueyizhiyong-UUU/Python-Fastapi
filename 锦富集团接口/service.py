from fastapi import FastAPI
import pymysql
import configparser
import uvicorn.lifespan.off
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from idna.core import unicode
import json


app=FastAPI()
origins=[
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


class DBUtil:
    def __init__(self):
        conf=configparser.ConfigParser()
        conf.read("config.ini")
        self.host=conf.get("DataBase","host")
        self.port=int(conf.get("DataBase","port"))
        self.database=conf.get("DataBase","database")
        self.user=conf.get("DataBase","user")
        self.password=conf.get("DataBase","password")
        self.conn=None
        self.cur=None

    def ConnectTODB(self):
        flag=False
        try:
            self.conn=pymysql.connect(host=self.host,port=self.port,user=self.user,password=self.password,database=self.database)
            self.cur=self.conn.cursor()
            flag=True
        except Exception as e:
            print(e)
            return flag
        return flag

    def disConnDB(self):
        if self.cur!=None:
            self.cur.close()
        if self.conn!=None:
            self.conn.close()

    # 获取在线预览url
    def mysqlMethod(self, DocumentNum, DocumentName, CreateTime):

        if DocumentName is None:
            arg1 = "%%"
        else:
            arg1 = '%'+DocumentName+'%'
        if DocumentNum is None:
            arg2 = "%%"
        else:
            arg2 = '%'+DocumentNum+'%'
        if CreateTime is None:
            SQL = """select skt1.skf3,skt1.skf16,skt32.skf1970 from skt1,skt32 WHERE skt1.skf3 like '%s' and skt1.skf16 like '%s' and skt1.skf241=skt32.skf413 """ % (arg1, arg2)
            # SQL = """ SELECT skt1.skf3 FROM skt1 WHERE DATE( SKT1.SF_CREATE_TIME) = DATE( '%s' ) """ % CreateTime
            # print(SQL)
            # SQL = "select * from skt1"
            self.cur.execute(SQL)  # 执行sql语句

            results = self.cur.fetchall()  # 获取查询的所有记录

            # print(results)
            context = []
            for i in results:
                DocumentList={}
                DocumentList["name"]=i[0]
                DocumentList["num"] = i[1]
                DocumentList["secret"] = i[2]

                context.append(DocumentList)


        else:
            SQL = """select skt1.skf3,skt1.skf16,skt1.skf1949 from skt1,skt32 WHERE skt1.skf3 like '%s' and skt1.skf16 like '%s'
                      and DATE( SKT1.SF_CREATE_TIME) = DATE( '%s' )  and skt1.skf241=skt32.skf413 """ % (arg1, arg2, CreateTime)
            # SQL = """ SELECT skt1.skf3 FROM skt1 WHERE DATE( SKT1.SF_CREATE_TIME) = DATE( '%s' ) """ % CreateTime
            # print(SQL)
            # SQL = "select * from skt1"
            self.cur.execute(SQL)  # 执行sql语句

            results = self.cur.fetchall()  # 获取查询的所有记录
            context = []
            for i in results:
                DocumentList={}
                DocumentList["name"]=i[0]
                DocumentList["num"] = i[1]
                DocumentList["secret"] = i[2]

                context.append(DocumentList)

        return context


class Item(BaseModel):

    # 档案名称
    DocumentName: str = ""
    # 档案编号
    DocumentNum: str = ""
    # 创建时间
    CreateTime: str = ""


# 检索返回接口
@app.get('/ck/service/GetSearch')
def GetSearch(DocumentName:str = None, DocumentNum: str = None, CreateTime: str = None):
    dbutil = DBUtil()
    # print("2")
    # print(DocumentNum, DocumentName, CreateTime)
    # print(preview.borrowingNum)
    # print(type(is_document))
    if dbutil.ConnectTODB():

        context = dbutil.mysqlMethod(DocumentNum, DocumentName, CreateTime)
        dbutil.disConnDB()
        results = {"code": 0, "context": context, "msg": "成功"}
        # return RedirectResponse(finalUrl)
        return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


if __name__ == "__main__":

    uvicorn.run(app, host="0.0.0.0", port=8083)

