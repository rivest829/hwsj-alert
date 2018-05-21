import json, time
import sys
import simplejson
import urllib2

reload(sys)
sys.setdefaultencoding('utf-8')

LOGFILE_NAME = "hwsj_grafana_alert.log"
user = "@all"
itemid = 1
corpid = 'ww24ca597fcf00a406'
corpsecret = 'uKlxMWEi76sZzAHXvhRNvxKkYDqj5YVnksm78FftNlM'


def setlog(send_data):
    with open(LOGFILE_NAME, "a") as log_file:
        log_file.write(time.strftime('%Y-%m-%d %H:%M:%S') + "    " + send_data + "\n\n")


def gettoken(corpid, corpsecret):
    gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
    try:
        token_file = urllib2.urlopen(gettoken_url)
    except urllib2.HTTPError as e:
        setlog(e.code + "\n" + e.read().decode("utf8"))
        sys.exit()
    token_data = token_file.read().decode('utf-8')
    token_json = json.loads(token_data)
    token_json.keys()
    token = token_json['access_token']
    return token


def senddata(access_token, user, subject, content, itemid):
    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    send_values = {
        "touser": user,
        "toparty": "2",
        "msgtype": "text",
        "agentid": "1000002",
        "text": {
            "content": subject + '\n' + content
        },
        "safe": "0"
    }
    send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
    setlog(send_data)
    send_request = urllib2.Request(send_url, send_data)
    response = json.loads(urllib2.urlopen(send_request).read())


def send_to_wechat(subject, content):
    accesstoken = gettoken(corpid, corpsecret)
    senddata(accesstoken, user, subject, content, itemid)