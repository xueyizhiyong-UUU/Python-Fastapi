from fastapi import FastAPI
from starlette.responses import RedirectResponse
import uvicorn
import requests
import pymysql
import datetime
import hashlib
import json
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
    "http://172.18.2.216:8081",
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
    getMD5fromSrv = "http://172.18.2.216:8081/ckapi/api/md5.jsp"
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

    # 全文检索套用权限返回接口
    def secretpower(self, searchid, username):

        # 连接数据库，查询出用户工号对应的自身密级权限
        usecretsql = 'SELECT MAX(tblpost.SKF360) FROM tblpost,tblemployee,tblemployee_post WHERE tblemployee.User = %s AND tblemployee.ID = tblemployee_post.EmployeeID AND tblpost.ID = tblemployee_post.PostID'
        try:
            self.cur.execute(usecretsql, username)
            results = self.cur.fetchone()
            # 如果输入的username不存在
            if results is not None:

                usersecret = results[0]
                print(usersecret)
            else:
                res = '用户名不存在'
                return res
        except Exception as e:
            print(e)

        # 获取每个json返回的skt1.skf16编号
        url = 'http://172.18.2.216:8081/ckapi/api/1/v2/sksearch_info.jsp'
        params = {"token": "chenksoft!@!",
                  "search_id": searchid}
        response = requests.get(url=url, params=params)
        response.encoding = 'utf-8'

        data = response.text
        dictdata = json.loads(data)
        print(type(dictdata))
        print(dictdata.keys())

        # 读取配置文件
        with open("readme.json", 'r') as f:
            temp = json.loads(f.read())

        # 遍历得到档案编号
        for i in dictdata["data"]:
            print(i["skt1.skf16"])

            # 查询出档案编号对应的档案密级
            dsecretsql = 'SELECT skf1951 FROM skt1 WHERE skf16 = %s'
            try:
                self.cur.execute(dsecretsql, [i["skt1.skf16"]])
                results = self.cur.fetchone()
                # 如果输入的documentNum不存在
                if results is not None:
                    documentsecret = results[0]
                else:
                    res = '档案编号不存在，或该档案没有对应密级'
                    return res
            except Exception as e:
                print(e)

            # 核心逻辑：判断用户密级和档案密集返回字段
            # 做拼接，使返回的接口参数带有权限信息
            # 公开岗位返回的
            if usersecret == 0:
                # 绝密档案返回的
                if documentsecret == 4:
                    # 给字典加上权限字段
                    i.update(temp["usersecret0"]["documentsecret4"])
                # 内部公开档案返回的
                elif documentsecret == 1:
                    i.update(temp["usersecret0"]["documentsecret1"])
                # 秘密档案返回的
                elif documentsecret == 2:
                    i.update(temp["usersecret0"]["documentsecret2"])
                # 机密档案返回的
                elif documentsecret == 3:
                    i.update(temp["usersecret0"]["documentsecret3"])
                # 公开岗位返回的
                else:
                    i.update(temp["usersecret0"]["documentsecret0"])
            # 内部公开岗位返回的
            # 内部公开岗位返回的
            elif usersecret == 1:
                # 绝密档案返回的
                if documentsecret == 4:
                    i.update(temp["usersecret1"]["documentsecret4"])
                # 内部公开档案返回的
                elif documentsecret == 1:
                    i.update(temp["usersecret1"]["documentsecret1"])
                # 秘密档案返回的
                elif documentsecret == 2:
                    i.update(temp["usersecret1"]["documentsecret2"])
                # 机密档案返回的
                elif documentsecret == 3:
                    i.update(temp["usersecret1"]["documentsecret3"])
                # 公开岗位返回的
                else:
                    i.update(temp["usersecret1"]["documentsecret0"])
            # 秘密岗位返回的
            elif usersecret == 2:
                # 绝密档案返回的
                if documentsecret == 4:
                    i.update(temp["usersecret2"]["documentsecret4"])
                # 内部公开档案返回的
                elif documentsecret == 1:
                    i.update(temp["usersecret2"]["documentsecret1"])
                # 秘密档案返回的
                elif documentsecret == 2:
                    i.update(temp["usersecret2"]["documentsecret2"])
                # 机密档案返回的
                elif documentsecret == 3:
                    i.update(temp["usersecret2"]["documentsecret3"])
                # 公开档案返回的
                else:
                    i.update(temp["usersecret2"]["documentsecret0"])
            # 机密岗位返回的
            elif usersecret == 3:
                # 绝密档案返回的
                if documentsecret == 4:
                    i.update(temp["usersecret3"]["documentsecret4"])
                # 内部公开档案返回的
                elif documentsecret == 1:
                    i.update(temp["usersecret3"]["documentsecret1"])
                # 秘密档案返回的
                elif documentsecret == 2:
                    i.update(temp["usersecret3"]["documentsecret2"])
                # 机密档案返回的
                elif documentsecret == 3:
                    i.update(temp["usersecret3"]["documentsecret3"])
                # 公开档案返回的
                else:
                    i.update(temp["usersecret3"]["documentsecret0"])
            # 绝密密岗位返回的
            elif usersecret == 4:
                # 绝密档案返回的
                if documentsecret == 4:
                    i.update(temp["usersecret4"]["documentsecret4"])
                # 内部公开档案返回的
                elif documentsecret == 1:
                    i.update(temp["usersecret4"]["documentsecret1"])
                # 秘密档案返回的
                elif documentsecret == 2:
                    i.update(temp["usersecret4"]["documentsecret2"])
                # 机密档案返回的
                elif documentsecret == 3:
                    i.update(temp["usersecret4"]["documentsecret3"])
                # 公开档案返回的
                else:
                    i.update(temp["usersecret4"]["documentsecret0"])
            else:
                res = "岗位密级权限不正确"
                return res

        # 最后返回需要的接口参数
        return dictdata

    # 新建目录
    def CreateList(self, uplistid, listname, is_list, username):
        # 在数据库里新建目录或档案

        # 首先查询给的username 的ID

        gonghao = 'SELECT tblemployee.ID FROM tblemployee WHERE tblemployee.User = %s'
        try:
            self.cur.execute(gonghao, [username])
            results1 = self.cur.fetchall()  # 获取查询的所有记录
            # 遍历拿到user用户id
            for row in results1:
                userid = row[0]

        except Exception as e:
            # 有异常，回滚事务
            print("异常：" % e)
            self.conn.rollback()

        # 查询给的目录名称是否存在，若存在直接返回目录id，若不存在则新建
        sql3 = 'SELECT SKT32.SKF413 FROM skt32 WHERE skf414 = %s'
        try:
            self.cur.execute(sql3, listname)
            results = self.cur.fetchone()
            if results is not None:
                row1 = results[0]
                contest = {
                    "data": "目录已存在",
                    "Listid": row1,
                    "state":1

                }

                return contest
            else:
                # 给我上级目录id查询他的层级，再+1，得到新的目录层级
                chengji = 'SELECT SKT32.SKF422 FROM skt32 WHERE skf413 = %s'
                try:
                    self.cur.execute(chengji, [uplistid])
                    results2 = self.cur.fetchall()  # 获取查询的所有记录
                    # 遍历拿到层级
                    for row in results2:
                        CJ = row[0]
                        reallyCJ = CJ + 1
                except Exception as e:
                    # 有异常，回滚事务
                    print("异常：" % e)
                    self.conn.rollback()

                # is_list 1 为档案类型，0为目录，默认目录
                if is_list == 1:
                    list_type = "档案类型"
                    sql2 = ' INSERT INTO SKT32 ( SKT32.SKF414,SKT32.SKF415,SKT32.SKF422,SKT32.SKF1199,SKT32.SKF1058,SKT32.SKF1284,SKT32.SKF1593 ) VALUES (%s,%s,%s,%s,%s,%s,%s)'

                    try:
                        self.cur.execute(sql2, [listname, uplistid, reallyCJ, 2, list_type, 57, uplistid])
                        # 提交
                        self.conn.commit()
                        is_work = True
                    except Exception as e:
                        # 有异常，回滚事务
                        print("异常：" % e)
                        self.conn.rollback()
                else:
                    list_type = "目录"
                    sql = ' INSERT INTO SKT32 ( SKT32.SKF414,SKT32.SKF415,SKT32.SKF422,SKT32.SKF1199 ) VALUES (%s,%s,%s,%s)'

                    try:
                        self.cur.execute(sql, [listname, uplistid, reallyCJ, 2])
                        # 提交
                        self.conn.commit()
                        is_work = True
                    except Exception as e:
                        # 有异常，回滚事务
                        print("异常：" % e)
                        self.conn.rollback()

                # 查询数据库中新建的目录id
                if is_work:
                    # 新建目录成功，查询最大目录id
                    sql1 = 'select MAX(skt32.skf413) from skt32'
                    self.cur.execute(sql1)
                    results3 = self.cur.fetchall()  # 获取查询的所有记录
                    for row in results3:
                        List_id = row[0]
                else:
                    # 新建目录失败
                    return

                # 调用三个存储过程
                ListURL1 = "http://172.18.2.216:8081/ckapi/api/1/v2/SKupdate_list_id.jsp"
                ListURL2 = "http://172.18.2.216:8081/ckapi/api/1/v2/SKupdate_power.jsp"
                ListURL3 = "http://172.18.2.216:8081/ckapi/api/1/v2/SKupdate_mylist.jsp"
                params1 = {'token': 'chenksoft!@!',
                           'list_id': List_id}
                params2 = {'token': 'chenksoft!@!',
                           'list_id': List_id,
                           'loge_user': userid
                           }
                params3 = {'token': 'chenksoft!@!',
                           'list_id': List_id}
                try:
                    res1 = requests.get(url=ListURL1, params=params1).json()
                    res2 = requests.get(url=ListURL2, params=params2).json()
                    res3 = requests.get(url=ListURL3, params=params3).json()
                except Exception as e:
                    print(e)

                # 返回新建的目录id
                return List_id


        except Exception as e:
            print("异常：" % e)

            print(e)

    # 写入借阅信息
    def BorrowInfo(self, borrowingNum, documentNumber, reasonApplication, username, startTime, overTime, preview,
                   download, print,
                   approvalStatus, Approve_time, Approve_name, Approver, Approval_operation, Approval_comments,
                   is_document, lend):

        # 获取用户user
        User_SQL = "SELECT ID FROM tblemployee WHERE USER='%s'" % username
        # print(User_SQL)
        self.cur.execute(User_SQL)  # 获取User
        result = self.cur.fetchone()  # 取所有结果集
        userID = result[0]  # 用户名

        # 写入借阅信息
        sql = "insert into skt21(skt21.skf791,skt21.skf297 ,skt21.skf622 ,skt21.skf296, skt21.skf300 , skt21.skf301, skt21.skf623, skt21.skf624,skt21.skf693,skt21.skf299,skt21.skf1290,skt21.skf2000,skt21.skf2001,skt21.skf2002,skt21.skf2003,skt21.skf355 )VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        try:
            self.cur.execute(sql, (
            borrowingNum, documentNumber, reasonApplication, userID, startTime, overTime, preview, download, print,
            approvalStatus, lend, Approve_name, Approver, Approval_operation, Approval_comments, Approve_time))

            # 提交
            self.conn.commit()
        except Exception as e:
            # 有异常，回滚事务
            print("异常：" % e)
            self.conn.rollback()

        #  查询档案对应的附件信息
        sql2 = "select skf374,skf375,skf891 from skt28 where skf906 = %s"
        try:
            self.cur.execute(sql2, (documentNumber))
        except Exception as e:
            # 有异常，回滚事务
            print("异常：" % e)
            self.conn.rollback()

        results = self.cur.fetchall()  # 获取查询的所有记录
        context = []
        for i in results:
            DocumentList = {}
            DocumentList["routeid"] = i[0]
            DocumentList["routename"] = i[1]
            DocumentList["routetype"] = i[2]

            context.append(DocumentList)

        return context

    # 获取在线预览url
    def mysqlMethod(self, documentNumber, username, Routeid):
        # result_list=[]定义列表
        # 获取服务器地址
        self.cur.execute("select skf991,skf689 from skt57")  # 获取服务器地址和单位号
        result = self.cur.fetchone()  # 取所有结果集
        weburl = result[0]  # 服务器地址
        Unit_number = result[1]  # 单位号

        # print(Unit_number)

        # 获取用户user
        User_SQL = "SELECT ID FROM tblemployee WHERE USER='%s' " % username
        # print(User_SQL)
        self.cur.execute(User_SQL)  # 获取User
        result = self.cur.fetchone()  # 取所有结果集
        usertestID = result[0]  # 用户名
        userID = "%d" % usertestID
        # print(User)

        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print('当前服务器时间：'+now_time)

        # 获取附件路径
        Route_SQL = "SELECT skf377 FROM skt28 WHERE skf906= %s AND skf374= %s "
        # print(Route_SQL)
        self.cur.execute(Route_SQL, (documentNumber, Routeid))  # 获取路径
        result = self.cur.fetchone()  # 取所有结果集
        Route = result[0]
        # print(Route)
        url = weburl + 'SK_CFW_Servlet.do?method=filedownload&action=directpreview&domainid=' + Unit_number + '&userid=' + userID + '&timestamp=' + now_time + '&filepath=' + Route + '&data='
        # print('拼接URL：'+url)

        BeforeMD5 = Unit_number + userID + now_time + '30' + Route + '0020182018'
        # print('BeforeMD5:'+BeforeMD5)
        finalUrl = url + encryptByMD5(BeforeMD5) + '&time=30&isShowPrint=0&isShowLoadFile=0'
        # print('finalUrl:'+finalUrl)
        # finalUrl="http://www.baidu.com"

        return finalUrl

    # 获取目录或者库房路径
    def documentClassification(self):
        # todo:未补全
        pass

    # 档案下载获取url
    def documentDownloadUrl(self, documentNumber, username,Routeid):

        # 获取服务器地址
        self.cur.execute("select skf991,skf689 from skt57")  # 获取服务器地址和单位号
        result = self.cur.fetchone()  # 取所有结果集
        weburl = result[0]  # 服务器地址
        Unit_number = result[1]  # 单位号

        # print(Unit_number)

        # 获取用户user
        User_SQL = "SELECT ID FROM tblemployee WHERE USER='%s'" % username
        # print(User_SQL)
        self.cur.execute(User_SQL)  # 获取User
        result = self.cur.fetchone()  # 取所有结果集
        usertestID = result[0]  # 用户名
        userID = "%d" % usertestID
        # print(User)

        # 获取附件编号
        Annex_SQL = "SELECT skf376 FROM skt28 WHERE skf906=%s and skf374=%s"
        self.cur.execute(Annex_SQL, (documentNumber, Routeid))  # 获取附件编号
        result = self.cur.fetchone()  # 取所有结果集
        Annex = result[0]

        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print('当前服务器时间：'+now_time)

        # 获取附件路径
        Route_SQL = "SELECT skf377 FROM skt28 WHERE skf906=%s AND skf374= %s"
        # print(Route_SQL)
        self.cur.execute(Route_SQL, (documentNumber, Routeid))  # 获取路径
        result = self.cur.fetchone()  # 取所有结果集
        Route = result[0]
        # print(Route)
        url = weburl + 'SK_CFW_Servlet.do?method=filedownload&action=watermarkpreview&domainid=' + Unit_number + '&userid=' + userID + '&timestamp=' + now_time + '&filepath=' + Route + '&data='
        # print('拼接URL：'+url)
        BeforeMD5 = Unit_number + userID + now_time + '30' + Route + '01' + Annex + '000020182018'

        finalUrl = url + encryptByMD5(
            BeforeMD5) + '&time=30&isShowPrint=0&isShowLoadFile=1&fileids=' + Annex + '&waterMarkName=&isCopy=0&isShowPreview=0&isShowTop=0&isDirectPreview=0'
        # print(finalUrl)

        return finalUrl

    # 档案打印获取url
    def documentPrintUrl(self, documentNumber, username,Routeid):
        # 获取服务器地址
        self.cur.execute("select skf991,skf689 from skt57")  # 获取服务器地址和单位号
        result = self.cur.fetchone()  # 取所有结果集
        weburl = result[0]  # 服务器地址
        Unit_number = result[1]  # 单位号

        # print(Unit_number)

        # 获取用户user
        User_SQL = "SELECT ID FROM tblemployee WHERE USER='%s'" % username
        # print(User_SQL)
        self.cur.execute(User_SQL)  # 获取User
        result = self.cur.fetchone()  # 取所有结果集
        usertestID = result[0]  # 用户名
        userID = "%d" % usertestID
        # print(User)

        # 获取附件编号
        Annex_SQL = "SELECT skf376 FROM skt28 WHERE skf906=%s AND skf374=%s"
        self.cur.execute(Annex_SQL, (documentNumber, Routeid))  # 获取附件编号
        result = self.cur.fetchone()  # 取所有结果集
        Annex = result[0]

        now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # print('当前服务器时间：'+now_time)

        # 获取附件路径
        Route_SQL = "SELECT skf377 FROM skt28 WHERE skf906=%s AND skf374= %s"
        # print(Route_SQL)
        self.cur.execute(Route_SQL, (documentNumber, Routeid))  # 获取路径
        result = self.cur.fetchone()  # 取所有结果集
        Route = result[0]
        # print(Route)
        url = weburl + 'SK_CFW_Servlet.do?method=filedownload&action=watermarkpreview&domainid=' + Unit_number + '&userid=' + userID + '&timestamp=' + now_time + '&filepath=' + Route + '&data='
        # print('拼接URL：'+url)
        BeforeMD5 = Unit_number + userID + now_time + '30' + Route + '10' + Annex + '000120182018'

        finalUrl = url + encryptByMD5(
            BeforeMD5) + '&time=30&isShowPrint=1&isShowLoadFile=0&fileids=' + Annex + '&waterMarkName=&isCopy=0&isShowPreview=0&isShowTop=0&isDirectPreview=1'
        # print(finalUrl)

        return finalUrl

    # 查询档案保密级别
    def getDocumentSecret(self, documentNumber):

        SQL = "SELECT skt1.skf1951 FROM skt1 WHERE skt1.SKF16 = %s"
        self.cur.execute(SQL, [documentNumber])  # 获取该文档密级信息
        result = self.cur.fetchall()  # 取所有结果集
        print(result)

        return result

    # 修改档案保密级别
    def setDcumentSecret(self, secret, documentNumber):
        SQL = 'UPDATE skt1 SET skt1.skf1951 = %s WHERE skt1.skf16= %s'
        is_work = False
        try:
            # 执行SQL语句
            self.cur.execute(SQL, [secret, documentNumber])
            # 提交事务
            self.conn.commit()
            is_work = True
        except Exception as e:
            # 有异常，回滚事务
            print("异常：" % e)
            self.conn.rollback()

        return is_work

    # 查询档案保密期限
    def getDocumentDeadline(self, documentNumber):

        SQL = "SELECT skt1.skf1956 FROM skt1 WHERE skt1.SKF16 = %s"
        self.cur.execute(SQL, [documentNumber])  # 获取该文档密级信息
        result = self.cur.fetchall()  # 取所有结果集
        print(result)

        return result

    # 修改档案保密期限
    def setDocumentDeadline(self, deadline, documentNumber):

        SQL = "UPDATE skt1 SET skt1.skf1956 = %s WHERE skt1.skf16= %s "
        is_work = False
        try:
            # 执行SQL语句
            self.cur.execute(SQL, [deadline, documentNumber])
            # 提交事务
            self.conn.commit()
            is_work = True
        except Exception as e:
            # 有异常，回滚事务
            print("异常：" % e)
            self.conn.rollback()

        return is_work

    # 档案销毁
    def setDocumentDestroy(self, documentNumber, is_type):
        SQL1 = "UPDATE skt1 SET skf1022 = 1 WHERE  skf16 = %s "
        SQL2 = 'DELETE FROM skt1 WHERE skf16 = %s and skf1952 = "2" '

        is_work = False

        # 是实体档案做删除处理
        if is_type == "2":
            try:
                # 执行SQl语句
                self.cur.execute(SQL2, [documentNumber])
                # 提交事务
                self.conn.commit()
                is_work = True
            except Exception as e:
                # 有异常，回滚事务
                print("异常：" % e)
                self.conn.rollback()
        else:
            # 做软删处理
            try:
                # 执行SQl语句
                self.cur.execute(SQL1, [documentNumber])
                # 提交事务
                self.conn.commit()
                is_work = True
            except Exception as e:
                # 有异常，回滚事务
                print("异常：" % e)
                self.conn.rollback()

        return is_work


# 档案借阅接口类
class Preview(BaseModel):
    # 用户工号
    userID: str = ""

    # 是否电子档案
    is_document: str = ""
    # 借阅编号
    borrowingNum: str = ""
    # 文档编号
    documentNumber: str = ""
    # 申请理由
    reasonApplication: str = ""
    # 开始时间
    startTime: str = ""
    # 借阅结束时间
    overTime: str = ""
    # 预览权限
    preview: bool = 0
    # 下载权限
    download: bool = 0
    # 打印权限
    print: bool = 0
    # 借出权限
    lend: bool = 0
    # 审批状态
    approvalStatus: str = ""
    # 审批时间
    Approve_time: str = ""
    # 审批节点名称
    Approve_name: str = ""
    # 审批人
    Approver: str = ""
    # 审批操作
    Approval_operation: str = ""
    # 审批意见
    Approval_comments: str = ""


# 档案密级类
class Secret(BaseModel):
    # 档案密级
    Secret: str = ""
    # 档案编号
    DocumentNumber: str = ""


# 档案保密期限类
class Deadline(BaseModel):
    # 档案密级
    Deadline: str = ""
    # 档案编号
    DocumentNumber: str = ""


# 档案销毁类
class Destroy(BaseModel):
    # 档案编号
    DocumentNumber: str = ''

    # 档案类型
    DocumentType: str = ''


# 档案借阅接口
@app.post("/ck/service/documentBorrow")
def documentBorrow(preview: Preview):
    dbutil = DBUtil()
    # print(preview.borrowingNum)
    # print(type(is_document))

    # 判断审批是否通过 3为通过
    if preview.approvalStatus == "3":
        # 区分电子档案与实体档案：电子档案为0，实体档案为1
        if preview.is_document == "0" or preview.is_document == "2":
            if dbutil.ConnectTODB():
                context = dbutil.BorrowInfo(preview.borrowingNum, preview.documentNumber, preview.reasonApplication,
                                             preview.userID, preview.startTime, preview.overTime, preview.preview,
                                             preview.download,
                                             preview.print, preview.approvalStatus, preview.Approve_time,
                                             preview.Approve_name, preview.Approver, preview.Approval_operation,
                                             preview.Approval_comments, preview.is_document, preview.lend)

                # print("链接数据库")
                results = {"code": 0, "data": context, "msg": "成功"}
                # return RedirectResponse(finalUrl)
                return results
            else:
                results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
                return results
        else:
            results = {"code": 0, "data": "档案为实体档案，到档案室借阅", "msg": "成功"}
            return results

    else:
        results = {"code": 3, "data": "审批未通过", "msg": "失败"}
        return results


# 档案在线预览接口
@app.get('/ck/service/getPreviewUrl')
def getPreviewUlr(documentNumber: str, userID: str, routeid: str):
    dbutil = DBUtil()
    # print(preview.borrowingNum)
    # print(type(is_document))
    if dbutil.ConnectTODB():
        finalUrl = dbutil.mysqlMethod(documentNumber, userID, routeid)
        # print("链接数据库")
        # results = {"code": 0, "data": [{"url": finalUrl}], "msg": "成功"}
        return RedirectResponse(finalUrl)
        # return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


# 下载电子档案接口
@app.get('/ck/service/getDownload')
def getDownload(documentNumber: str, userID: str, routeid: str):
    dbutil = DBUtil()
    if dbutil.ConnectTODB():
        finalUrl = dbutil.documentDownloadUrl(documentNumber, userID,routeid)
        # print("链接数据库")
        # results = {"code": 0, "data": [{"url": finalUrl}], "msg": "成功"}
        return RedirectResponse(finalUrl)
        # return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


# 打印电子档案接口
@app.get('/ck/service/documentPrint')
def documentPrint(documentNumber: str, userID: str, routeid: str):
    dbutil = DBUtil()

    if dbutil.ConnectTODB():
        finalUrl = dbutil.documentPrintUrl(documentNumber, userID,routeid)
        # print("链接数据库")
        # results = {"code": 0, "data": [{"url": finalUrl}], "msg": "成功"}
        return RedirectResponse(finalUrl)
        # return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


# 档案保密级别查询接口
@app.get('/ck/service/getSecret')
def getSecret(documentNumber: str):
    dbutil = DBUtil()

    if dbutil.ConnectTODB():
        data = dbutil.getDocumentSecret(documentNumber)
        # print("链接数据库")
        results = {"code": 0, "data": data, "msg": "成功"}
        print(data)

        return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


# 档案保密级别修改接口
@app.post('/ck/service/setSecret')
def setSecret(secret: Secret):
    dbutil = DBUtil()
    # print(secret.Secret,secret.DocumentNumber)
    if dbutil.ConnectTODB():
        is_work = dbutil.setDcumentSecret(secret.Secret, secret.DocumentNumber)
        # print(is_work)
        # 查看返回值是否正确，如果正确，说明数据库已修改
        if is_work:
            results = {"code": 0, "data": "修改成功", "msg": "成功"}
            return results
        else:
            results = {"code": 1, "data": "修改失败", "msg": "失败"}
            return results


# 查询档案保密期限
@app.get('/ck/service/getDeadline')
def getDeadline(documentNumber: str):
    dbutil = DBUtil()

    if dbutil.ConnectTODB():
        data = dbutil.getDocumentDeadline(documentNumber)
        # print("链接数据库")
        results = {"code": 0, "data": data, "msg": "成功"}
        print(data)

        return results
    else:
        results = {"code": 1, "data": "URL返回失败", "msg": "失败"}
        return results


# 档案保密期限修改接口
@app.post('/ck/service/setDeadline')
def setDeadline(deadline: Deadline):
    dbutil = DBUtil()
    # print(secret.Secret,secret.DocumentNumber)
    if dbutil.ConnectTODB():
        is_work = dbutil.setDocumentDestroy(deadline.Deadline, deadline.DocumentNumber)
        # print(is_work)
        # 查看返回值是否正确，如果正确，说明数据库已修改
        if is_work:
            results = {"code": 0, "data": "修改成功", "msg": "成功"}
            return results
        else:
            results = {"code": 1, "data": "修改失败", "msg": "失败"}
            return results


# 档案删除接口
@app.post('/ck/service/documentDestroy')
def documentDestroy(destroy: Destroy):
    dbutil = DBUtil()
    if dbutil.ConnectTODB():
        is_work = dbutil.setDocumentDestroy(destroy.DocumentNumber, destroy.DocumentType)
        # print(is_work)
        # 查看返回值是否正确，如果正确，说明数据库已修改
        if is_work:
            results = {"code": 0, "data": "删除成功", "msg": "成功"}
            return results
        else:
            results = {"code": 1, "data": "删除失败", "msg": "失败"}
            return results


# 目录新建接口
@app.get('/ck/service/createList')
def createList(uplistid: int, username: str, listname: str, is_list: int):
    dbutil = DBUtil()
    if dbutil.ConnectTODB():
        Listid = dbutil.CreateList(uplistid, listname, is_list, username)
        # print(is_work)
        # 查看返回值是否正确，如果正确，说明数据库已修改
        if Listid:
            results = {"code": 0, "Listid": Listid, "msg": "成功"}
            return results
        else:
            results = {"code": 1, "data": "新建目录失败", "msg": "失败"}
            return results


# 全文检索套用权限返回接口
@app.get('/ck/service/sksearch_info')
def secretPower(searchid: str, username: str):
    dbutil = DBUtil()
    if dbutil.ConnectTODB():
        res = dbutil.secretpower(searchid, username)
        # 查看返回值是否正确，如果正确，说明数据库已修改

        return res
    else:
        results = {"code": 1, "data": "数据库连接失败", "msg": "失败"}
        return results


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8083)

