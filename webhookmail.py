#!/usr/bin/python
# coding:utf-8
# gunicorn -b :9527 webhookmail:app

from __future__ import print_function
import falcon
from wsgiref import simple_server
from email.mime.text import MIMEText
import smtplib
import json
import send_to_wechat
import time,threading
import get_elastic_search
LOGFILE_NAME = "hwsj_grafana_alert.log"

smtpServer = "mx.example.com"
smtpUser = "sender@example.com"
smtpPass = "password"
sender = "sender@example.com"
reciver = "reciver@example.com"


def sendMail(reciver, subject, message):
    server = smtplib.SMTP(smtpServer, 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtpUser, smtpPass)
    server.set_debuglevel(1)
    msg = MIMEText(message, "plain", "utf8")
    msg["Subject"] = subject
    server.sendmail(sender, [reciver], msg.as_string())
    server.quit()

def errorlog_monitoring():
    while True:
        errorLog_num=get_elastic_search.count_error_log("5m")
        if errorLog_num>100:
            title="日志告警"
            msg="告警监控项：" + "ElasticSearch告警" + \
                      "\n告警消息：" + "5分钟内错误日志数大于100，注意排查" + \
                      "\nERROR日志条数：" + str(errorLog_num) + \
                      "\n打开网页查看告警历史:" + "http://47.254.148.9:9527"
            send_to_wechat.send_to_wechat(title,msg)
        print(errorLog_num)
        time.sleep(300)

def start_monitoring():
    thread=threading.Thread(target=errorlog_monitoring)
    thread.setDaemon(True)
    thread.start()

class WebHook(object):
    def on_post(self, req, resp):
        body = req.stream.read()
        postData = json.loads(body.decode('utf-8'))
        if postData['state'] == 'ok':
            title = postData['title']
            msg = "恢复监控项：" + postData['ruleName'] + \
                  "\n恢复消息：" + postData['message'] + \
                  "\n打开网页查看详情:" + postData['ruleUrl']
        else:
            title = postData['title']
            msg = "告警监控项：" + postData['ruleName'] + \
                  "\n告警消息：" + postData['message'] + \
                  "\n当前值：" + str(postData['evalMatches'][0]['value']) + \
                  "\n打开网页查看详情:" + postData['ruleUrl']
        send_to_wechat.send_to_wechat(title, msg)
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = "OK"


class getlog(object):
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        with open(LOGFILE_NAME, "r") as log_file:
            log = log_file.read()
        resp.body = log

start_monitoring()
app = falcon.API()
app.add_route('/alert', WebHook())
app.add_route('/', getlog())
if __name__ == '__main__':
    httpd = simple_server.make_server('0.0.0.0', 9527, app)
    httpd.serve_forever()
