<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%>
<%
String path = request.getContextPath();
String basePath = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+path+"/";
System.out.println(basePath);
String siteUrl = request.getScheme()+"://"+request.getServerName()+":"+request.getServerPort()+"/";
session.setAttribute("basePath",basePath);
String r = Math.random()+"";
request.setAttribute("r", r);
String userID = request.getParameter("userID");
String requestNumber=request.getParameter("requestNumber");
%>
<!DOCTYPE>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html;charset=UTF-8" />
<%-- <%@ include file="include/heard.jsp"%> --%>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1, user-scalable=no">
<title>Preview</title>
</head>
<body style="">
<script src="${basePath}js/jquery.min.js"></script>
<script src="${basePath}js/bowser.min.js"></script>
<script src="${basePath}js/jquery.cookie.js"></script>
<script src="${basePath}js/beService.js?${r} "></script>

 <!-- <script src="https://g.alicdn.com/dingding/dingtalk-jsapi/2.7.13/dingtalk.open.js"></script> -->
 <script type="text/javascript">
 var userID = "<%=userID%>";
 var requestNumber = "<%=requestNumber%>";
 console.log(userID);
 console.log(requestNumber);

 $.ajax({
    type:'get',
    url:"http://127.0.0.1:8082/ck/service/getPreviewUrl",
    cache:false,
    dataType:'json',
    data:{
        "requestNumber":requestNumber,
        "userID":userID
    },
    success:function(mydata){
        console.log(mydata);
		console.log(mydata["data"]);
		window.location.href=mydata["data"];
		//window.location.href='http://www.baidu.com';
    }


})

</script>
</body>
</html>
