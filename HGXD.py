from fastapi import FastAPI
from starlette.responses import RedirectResponse
import uvicorn
import requests
import pymysql
import datetime
import hashlib
import configparser
import uvicorn.lifespan.off
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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



def test():
    pass

# 调用saas设备管理系统接口
def MySaas(myString):
    # print('myString:'+myString)
    getMD5fromSrv = "http://saas.chenksoft.com:80/ckapi/api/139/v2/Equipment_failure_record.jsp"
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


@app.post('/HGXD/emqx')
def emqx():

    pass


