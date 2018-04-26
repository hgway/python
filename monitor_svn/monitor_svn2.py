#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

#运行脚本需安装python2.7 如缺少第三方库请使用pip进行安装
import xml.etree.ElementTree as ET
import subprocess
import os
import time
import smtplib
from email.mime.text import MIMEText

#以下信息根据实际情况更改
msg_from = '123456@qq.com'          #发送方邮箱
passwd = 'XXXXX'                    #填入发送方邮箱的授权码
msg_to = '12345678@qq.com'          #收件人邮箱
monitorremark = 'ZQSPB-1220'        #监控的需求号
svnPath = "D:\SPB"                  #svn工作目录 
logPath = "D:\svnmonitorlog"        #运行脚本日志目录
time_span = 5                       #脚本调用间隔时间，单位秒

#初始化
b_version = 0
e_version = 0
init = 0
mode = 0
    
#获取时间
def get_time(): 
    timestampsave = time.time()
    timestructsave = time.localtime(timestampsave)
    timesave = time.strftime('%Y-%m-%d %H:%M:%S', timestructsave)
    return timesave

#获取svn版本
def get_max_reversion():
    global mode
    if mode == 0:#获取当前更新版本,第一次调用使用
        command = 'svn info | find "Revision"'
    else:#获取最新版本
        command = 'svn info -r HEAD | find "Revision"'
    os.chdir(svnPath) #切换到对应目录
    result = subprocess.check_output(command,shell=True);#子进程运行
    result = result.split(':')[1]#第二个分割符内容
    result = int(str(result))
    mode = 1
    return result

#获取服务器地址
def get_service_address():
    command = 'svn info | find "Relative URL"'
    os.chdir(svnPath)
    result = subprocess.check_output(command,shell=True);
    result = result.split(':')[1]
    result = str(result)
    return result

#获取版本之间的日志存入xml
def create_log():
    global b_version
    global e_version
    log_command = "svn log -v --xml -r"
    os.chdir(svnPath)
    e_version = get_max_reversion()
    if b_version != e_version:
        command = log_command+str(b_version+1)+":"+str(e_version) + ">" + logPath + "\svnchangexml.log"
        subprocess.check_output(command,shell=True);#subprocess不会弹窗
        #os.system(log_command+str(b_version+1)+":"+str(e_version) + ">" + fileName)

#解析xml判断是否有目标需求的处理
def CheckNewUpdate(): 
    fileName = logPath + "\svnchangexml.log"
    tree = ET.parse(fileName)#解析
    root = tree.getroot()#根目录
    for msg in root.iter("msg"):
        remark = msg.text
        if monitorremark in remark:
            address = get_service_address()
            sendmail(remark,address)    

#发送qq邮件
def sendmail( remark, address):
    subject= u"svn更新通知"                                    
    content= u"您关注的需求" + monitorremark + u"有了新的更新，请及时查阅！\r\n备注为:" + remark + u"\r\n服务器地址为：" + address + "\r\n"
    msg = MIMEText(content, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = msg_from
    msg['To'] = msg_to
    Path = logPath + "\sendemail.log"
    try:
        s = smtplib.SMTP_SSL("smtp.qq.com",465)#邮件服务器及端口号
        s.login(msg_from, passwd)#登录
        s.sendmail(msg_from, msg_to, msg.as_string())
        with open(Path,'a') as f:#记录成功日志
            time = get_time()
            sendtext = time + ":" + monitorremark +u"需求变更发送到"+ msg_to + u"成功!\r\n"     
            f.write(sendtext.encode("utf-8"))
    except s.SMTPException,e:
        with open(Path,'a') as f:#记录失败日志
            time = get_time()
            sendtext = time + ":" + monitorremark +u"需求变更发送到"+ msg_to + u"失败!\r\n" 
            f.write(sendtext.encode("utf-8"))
    finally:
        s.quit()

#目录是否存在
def Check_folder(): 
    if not os.path.exists(logPath):  # 如果目录不存在则创建
        os.makedirs(logPath)
        
#主函数
def main():
    global init
    global b_version
    global e_version
    Check_folder()
    while(True):
        create_log()
        if (init == 0 or b_version != e_version):
            print("begin_verion:" + str(b_version) + " end_version:" + str(e_version))
            CheckNewUpdate()  
            b_version = e_version
            init = 1
        time.sleep(time_span)

if __name__=="__main__":
    b_version = get_max_reversion()
    main()
