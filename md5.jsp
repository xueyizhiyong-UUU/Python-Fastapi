<%@page import="net.sf.json.JSONObject"%><%@page import="com.packages.util.HttpUtil"%><%@page import="java.util.*"%><%@page import="com.packages.core.ResultBean"%><%@page import="cn.base.SK_MD5"%><%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8"%><%
ResultBean result = new ResultBean();
SK_MD5 md5 = new SK_MD5();
String str = request.getParameter("str");
if(str==null){
	str="";
}
String s1=md5.getMD5ofStr(str);
result.setCode(0);
result.setData(s1);
JSONObject obj = JSONObject.fromObject(result);
response.setContentType("text/json; charset=UTF-8");  
out.write(obj.toString());
%>