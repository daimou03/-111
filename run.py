#encoding=gbk
import random
import json
from time import localtime
from requests import get, post
from datetime import datetime, date
from zhdate import ZhDate
import sys
import os


def get_color():
    # ��ȡ�����ɫ
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF), range(n)))
    color_list = get_colors(100)
    return random.choice(color_list)


def get_access_token():
    # appId
    app_id = config["app_id"]
    # appSecret
    app_secret = config["app_secret"]
    post_url = ("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}"
                .format(app_id, app_secret))
    try:
        access_token = get(post_url).json()['access_token']
    except KeyError:
        print("��ȡaccess_tokenʧ�ܣ�����app_id��app_secret�Ƿ���ȷ")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token

#������Ϣ
def get_weather(region):
    try:
        rb=get('http://wthrcdn.etouch.cn/weather_mini?city={}'.format(region))
        data = json.loads(rb.text)
        # �ط�
        place=data['data']['city']
        #�ߵ���
        temperature="����"+data['data']['forecast'][0]['high']+"������"+data['data']['forecast'][0]['low']
        #����
        weather=data['data']['forecast'][0]['type']
        #����
        Suggest=data['data']['ganmao']
        #���ʽ�����������
        print("������Ϣ",data)
        # print(len(data))
        ## print(data['data']['city'])#�ط�
        # print(data['data']['forecast'][0]['high'])#���¶�
        # print(data['data']['forecast'][0]['low'])#���¶�
        # print(data['data']['forecast'][0]['type'])#�����仯
        # print(data['data']['ganmao'])
        return temperature,weather,Suggest
    except:
        print("��Ϣ����ʧ�ܣ���������λ����Ϣ�Ƿ���ȷ")

def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # �ж��Ƿ�Ϊũ������
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # ��ȡũ�����յĽ����Ӧ���º���
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("�������յ������Ƿ��ڽ������")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # ��������
        year_date = date(year, birthday_month, birthday_day)

    else:
        # ��ȡ�������յĽ����Ӧ�º���
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # ��������
        year_date = date(year, birthday_month, birthday_day)
    # ����������ݣ������û����������������������Ҫ+1
    if today > year_date:
        if birthday_year[0] == "r":
            # ��ȡũ���������յ��º���
            r_last_birthday = ZhDate((year + 1), r_mouth, r_day).to_datetime().date()
            birth_date = date((year + 1), r_last_birthday.month, r_last_birthday.day)
        else:
            birth_date = date((year + 1), birthday_month, birthday_day)
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    elif today == year_date:
        birth_day = 0
    else:
        birth_date = year_date
        birth_day = str(birth_date.__sub__(today)).split(" ")[0]
    return birth_day

##��ɽ�ʰ�ÿ��һ��
# def get_ciba():
#     url = "http://open.iciba.com/dsapi/"
#     headers = {
#         'Content-Type': 'application/json',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
#     }
#     r = get(url, headers=headers)
#     note_en = r.json()["content"]
#     note_ch = r.json()["note"]
#     return note_ch

##�İ�
def wenan():

    # result =get('https://api.xygeng.cn/one')#��2022.9.10����
    # result = requests.get('https://v1.hitokoto.cn/')#̨�ʻ���ʫ��
    result = get('https://v.api.aa1.cn/api/api-wenan-wangyiyunreping/index.php?aa1=json')#����������
    content = result.content.decode("utf8")
    # print(content)#��ӡ����
    # ���ｫstr���͵�contentת������dict���͵�
    content = json.loads(content)
    print(content)
    # data=content['data']['content']+" ���� "+content['data']['origin']
    # data=content['hitokoto']+" ���� "+content['from']
    data=content[0]['wangyiyunreping']
    return data

def send_message(to_user, access_token, region_name, weather, temp, wind_dir, note_ch):
# def send_message(to_user, access_token, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["������", "����һ", "���ڶ�", "������", "������", "������", "������"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # ��ȡ��һ������ӵ����ڸ�ʽ
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # ��ȡ��һ������ڲ�
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # ��ȡ������������
    birthdays = {}
    for k, v in config.items():
        if k[0:5] == "birth":
            birthdays[k] = v
    data = {
        "touser": to_user,
        "template_id": config["template_id"],
        "url": "http://weixin.qq.com/download",
        "topcolor": "#FF0000",
        "data": {
            "date": {
                "value": "{} {}".format(today, week),
                "color": get_color()
            },

            "region": {
                "value": region_name,
                "color": get_color()
            },

            "weather": {
                "value": weather ,
                "color": get_color()
            },

            "temp": {
                "value": temp,
                "color": get_color()
            },

            "love_day": {
                "value": love_days,
                "color": get_color()
            },
            "wind_dir": {
                "value": wind_dir,
                "color": get_color()
            },
            "note_ch": {
                "value": note_ch,
                "color": get_color()
            }
        }
    }
    for key, value in birthdays.items():
        # ��ȡ�����´����յ�ʱ��
        birth_day = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "����{}һ��Ҫ����ѽ��ף{}һЦ������".format(value["name"], value["name"])
        else:
            birthday_data = "����{}�����ڻ���{}�죬���������".format(value["name"], birth_day)
        # ���������ݲ���data
        data["data"][key] = {"value": birthday_data, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("������Ϣʧ�ܣ�����ģ��id�Ƿ���ȷ")
    elif response["errcode"] == 40036:
        print("������Ϣʧ�ܣ�����ģ��id�Ƿ�Ϊ��")
    elif response["errcode"] == 40003:
        print("������Ϣʧ�ܣ�����΢�ź��Ƿ���ȷ")
    elif response["errcode"] == 0:
        print("������Ϣ�ɹ�")
    else:
        print(response)



try:
    with open("config.txt", encoding="utf-8") as f:
        config = eval(f.read())
except FileNotFoundError:
    print("������Ϣʧ�ܣ�����config.txt�ļ��Ƿ������λ��ͬһ·��")
    os.system("pause")
    sys.exit(1)
except SyntaxError:
    print("������Ϣʧ�ܣ����������ļ���ʽ�Ƿ���ȷ")
    os.system("pause")
    sys.exit(1)

def yx():
    # ��ȡaccessToken
    accessToken = get_access_token()
    # ���յ��û�
    users = config["user"]
    # ���������ȡ������Ϣ
    region = config["region"]
    temp,weather, wind_dir = get_weather(region)
    note_ch = config["note_ch"]

    if note_ch == "":
        # ��ȡ�ʰ�ÿ�ս��
        # note_ch, note_en = get_ciba()
        #��ȡ�������İ�
        note_ch = wenan()
        print("�İ�:",note_ch)
    # ���ں�������Ϣ
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch)
        # send_message(user, accessToken, note_ch, note_en)
    # os.system("pause")

if __name__ == '__main__':
    yx()#���з���