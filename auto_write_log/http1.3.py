#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import json
import execjs
import re
import datetime
import time

# 用户信息
user_name = ''
user_password = ''

# 初始cookie
cookie = 'JSESSIONID=?; account=*; JSESSIONID=F7CA3ECCC94049D2AE66993667A2F2F2'
cookie = cookie.replace("*",user_name)

# 头部信息
headers = {  
    'Host':"192.168.14.233:8086",
    'Accept-Language':"zh-CN,zh;q=0.9,en;q=0.8",
    'Accept-Encoding':"gzip, deflate",
    'Content-Type':"application/x-www-form-urlencoded;charset=UTF-8",
    'Connection':"keep-alive",
    'User-Agent':"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    'Cookie':cookie,
    'Origin':'http://192.168.14.233:8086'
}

# 登陆
def login(url, password):
    values = {
        'userAccount':user_name,
        'userPassword':password,
        'rememberMe':'true'
    }
    
    data = urllib.parse.urlencode(values).encode('utf-8')
    request = urllib.request.Request(url, data, headers)
    html = urllib.request.urlopen(request).read().decode('utf-8')
    #print(json.loads(html))

# 读取js
def get_js(filename):  
    f = open(filename, 'r')  
    line = f.readline()  
    jsstr = ''  
    while line:  
        jsstr = jsstr + line  
        line = f.readline()  
    return jsstr

# 密码加密
def get_password(deskey,password):
    shafilename = "sha.js"
    desfilename = "des.js"
    jsstr = get_js(shafilename)  
    ctx = execjs.compile(jsstr)
    # sha密文
    hex_sha = ctx.call("hex_sha1",password)

    jsstr = get_js(desfilename)  
    ctx = execjs.compile(jsstr)
    # des加密
    password = ctx.call("strEnc",hex_sha,deskey)
    return password

# 获取cookie中JSESSIONID
def get_cookie():
    url_getjse = "http://192.168.14.233:8086/quick/"
 
    response = urllib.request.urlopen(url_getjse)
 
    responseinfo = str(response.info())
    # 取得JSESSIONID
    it = re.finditer(r"JSESSIONID=(.*?);",responseinfo) 
    for match in it: 
        jse_str = str(match.group())
        # 分隔
        jse_list = jse_str.split('=')
        # 取值
        jse_value = str(jse_list[1])
        # 去掉分号
        jse_value = jse_value[:-1]
        return jse_value  

# 获取deskey
def get_deskey():
    # 获取Date()
    ctx = execjs.compile("""
     function date() {         
         var d1 = new Date();
         var d2 = d1.toString()
         return d2; 
     }
     """)
    date = ctx.call("date")
    # unicode空格转换
    date = date.replace(" ","%20")
    # 地址
    url = "http://192.168.14.233:8086/quick/user/getDesKey.do?time=" + date    
    # 头
    values = {
        'time':date
    }
    
    data = urllib.parse.urlencode(values).encode('utf-8')
    request = urllib.request.Request(url, data, headers)   
    html = urllib.request.urlopen(request).read().decode('utf-8')
    deskey_dict = json.loads(html)
    return deskey_dict['desKey']

def getweekly(weekly):
    if weekly == "w": #星期几
        return time.strftime("%w",time.localtime())
    if weekly == "W": #一年中的第几周，且是星期一作为周的第一天
        return time.strftime("%W",time.localtime())

def write_log():
    # 获取当前是第几周
    reportWeek = getweekly('W')
    # 获取当前日期与本周第一天的差值
    b_differ = int(getweekly('w'))-1
    # 获取当前日期与本周最后一天的差值
    e_differ = 7- int(getweekly('w'))
    today = datetime.datetime.now()
    b_week_date = today + datetime.timedelta(days = -b_differ)
    e_week_date = today + datetime.timedelta(days = e_differ)
    # 获取年份
    reportYear = today.strftime('%Y')
    # 获取本周的第一天
    startDate = b_week_date.strftime('%Y-%m-%d')
    # 获取本周最后一天
    endDate = e_week_date.strftime('%Y-%m-%d')
    # 日报标题
    reportName = '交易产品一部-章怀广-' + reportYear + '年第' + reportWeek + '周周报'
    # 日报内容
    listJsonString =r'[{"workType":"项目","workAdress":"深圳金证大楼","taskProgress":"100","taskCostTime":"1","staffGrade":"70","taskStartDate":"2018-04-23","taskEndDate":"2018-04-23","taskName":"win版融资融券","taskContent":"1.\n2.\n3.","nextPlan":"","staffRemark":""},{"workType":"项目","workAdress":"深圳金证大楼","taskProgress":"100","taskCostTime":"1","staffGrade":"70","taskStartDate":"2018-04-24","taskEndDate":"2018-04-24","taskName":"win版融资融券","taskContent":"1.\n2.\n3.","nextPlan":"","staffRemark":""},{"workType":"项目","workAdress":"深圳金证大楼","taskProgress":"100","taskCostTime":"1","staffGrade":"70","taskStartDate":"2018-04-25","taskEndDate":"2018-04-25","taskName":"win版融资融券","taskContent":"1.\n2.\n3.","nextPlan":"","staffRemark":""},{"workType":"项目","workAdress":"深圳金证大楼","taskProgress":"100","taskCostTime":"1","staffGrade":"70","taskStartDate":"2018-04-26","taskEndDate":"2018-04-26","taskName":"win版融资融券","taskContent":"1.\n2.\n3.","nextPlan":"","staffRemark":""},{"workType":"项目","workAdress":"深圳金证大楼","taskProgress":"100","taskCostTime":"1","staffGrade":"70","taskStartDate":"2018-04-27","taskEndDate":"2018-04-27","taskName":"win版融资融券","taskContent":"1.\n2.\n3.","nextPlan":"","staffRemark":""}]'
    # 逐个日期替换从2018-04-23开始，连续五天
    str_date = '2018-04-23'
    replace_date = b_week_date
    loopnum = 5
    while loopnum >1 :
        # 替换第一天
        listJsonString = listJsonString.replace(str_date,replace_date.strftime('%Y-%m-%d'))
        # 替换日期加1
        replace_date = replace_date + datetime.timedelta(days =1)
        # 待替换日期加1
        date_time = datetime.datetime.strptime(str_date,'%Y-%m-%d')
        next_date_time = date_time + datetime.timedelta(days=1)
        str_date = next_date_time.strftime("%Y-%m-%d")
        loopnum -=1
        
    url = 'http://192.168.14.233:8086/quick/workReport/insertWrokly.do'
    
    values = {
        'startDate':startDate,
        'endDate':endDate,
        'reportYear':reportYear,
        'reportWeek':reportWeek,
        'reportId':'',
        'reportName':reportName,
        'listJsonString':listJsonString
    }
    
    data = urllib.parse.urlencode(values).encode('utf-8')
    request = urllib.request.Request(url, data, headers)
    html = urllib.request.urlopen(request).read().decode('utf-8')
    #print(json.loads(html))
    result_dict = json.loads(html)
    return result_dict['code']
    

if __name__ == "__main__":    
    url_login = "http://192.168.14.233:8086/quick/user/ajaxlogin.do"  
    # 取cookie
    cookievalue = get_cookie()
    print("取cookie成功")
    # 修改cookie
    cookie = cookie.replace("?",cookievalue)
    headers['Cookie'] = cookie
    # 取deskey
    deskey = get_deskey()
    print("取deskey成功")
    # 密码加密
    password = get_password(deskey,user_password)
    print("密码加密成功")
    # 登录
    login(url_login, password)
    print("登录成功")
    # 写日报
    result = write_log()
    if result == '1':
        print("写日报成功")
    else:
        print("写日报失败")
    
