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
    # 获取随机颜色
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
        print("获取access_token失败，请检查app_id和app_secret是否正确")
        os.system("pause")
        sys.exit(1)
    # print(access_token)
    return access_token

#天气信息
def get_weather(region):
    try:
        rb=get('http://wthrcdn.etouch.cn/weather_mini?city={}'.format(region))
        data = json.loads(rb.text)
        # 地方
        place=data['data']['city']
        #高低温
        temperature="高温"+data['data']['forecast'][0]['high']+"，低温"+data['data']['forecast'][0]['low']
        #天气
        weather=data['data']['forecast'][0]['type']
        #建议
        Suggest=data['data']['ganmao']
        #访问今天的天气情况
        print("天气信息",data)
        # print(len(data))
        ## print(data['data']['city'])#地方
        # print(data['data']['forecast'][0]['high'])#高温度
        # print(data['data']['forecast'][0]['low'])#低温度
        # print(data['data']['forecast'][0]['type'])#天气变化
        # print(data['data']['ganmao'])
        return temperature,weather,Suggest
    except:
        print("消息推送失败！！！请检查位置信息是否正确")

def get_birthday(birthday, year, today):
    birthday_year = birthday.split("-")[0]
    # 判断是否为农历生日
    if birthday_year[0] == "r":
        r_mouth = int(birthday.split("-")[1])
        r_day = int(birthday.split("-")[2])
        # 获取农历生日的今年对应的月和日
        try:
            birthday = ZhDate(year, r_mouth, r_day).to_datetime().date()
        except TypeError:
            print("请检查生日的日子是否在今年存在")
            os.system("pause")
            sys.exit(1)
        birthday_month = birthday.month
        birthday_day = birthday.day
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)

    else:
        # 获取国历生日的今年对应月和日
        birthday_month = int(birthday.split("-")[1])
        birthday_day = int(birthday.split("-")[2])
        # 今年生日
        year_date = date(year, birthday_month, birthday_day)
    # 计算生日年份，如果还没过，按当年减，如果过了需要+1
    if today > year_date:
        if birthday_year[0] == "r":
            # 获取农历明年生日的月和日
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

##金山词霸每日一句
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

##文案
def wenan():

    # result =get('https://api.xygeng.cn/one')#在2022.9.10崩了
    # result = requests.get('https://v1.hitokoto.cn/')#台词或者诗句
    result = get('https://v.api.aa1.cn/api/api-wenan-wangyiyunreping/index.php?aa1=json')#网易云热评
    content = result.content.decode("utf8")
    # print(content)#打印数据
    # 这里将str类型的content转换成了dict类型的
    content = json.loads(content)
    print(content)
    # data=content['data']['content']+" —— "+content['data']['origin']
    # data=content['hitokoto']+" —— "+content['from']
    data=content[0]['wangyiyunreping']
    return data

def send_message(to_user, access_token, region_name, weather, temp, wind_dir, note_ch):
# def send_message(to_user, access_token, note_ch, note_en):
    url = "https://api.weixin.qq.com/cgi-bin/message/template/send?access_token={}".format(access_token)
    week_list = ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"]
    year = localtime().tm_year
    month = localtime().tm_mon
    day = localtime().tm_mday
    today = datetime.date(datetime(year=year, month=month, day=day))
    week = week_list[today.isoweekday() % 7]
    # 获取在一起的日子的日期格式
    love_year = int(config["love_date"].split("-")[0])
    love_month = int(config["love_date"].split("-")[1])
    love_day = int(config["love_date"].split("-")[2])
    love_date = date(love_year, love_month, love_day)
    # 获取在一起的日期差
    love_days = str(today.__sub__(love_date)).split(" ")[0]
    # 获取所有生日数据
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
        # 获取距离下次生日的时间
        birth_day = get_birthday(value["birthday"], year, today)
        if birth_day == 0:
            birthday_data = "今天{}一定要开心呀，祝{}一笑而过！".format(value["name"], value["name"])
        else:
            birthday_data = "距离{}的日期还有{}天，奥里给！！".format(value["name"], birth_day)
        # 将生日数据插入data
        data["data"][key] = {"value": birthday_data, "color": get_color()}
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
    }
    response = post(url, headers=headers, json=data).json()
    if response["errcode"] == 40037:
        print("推送消息失败，请检查模板id是否正确")
    elif response["errcode"] == 40036:
        print("推送消息失败，请检查模板id是否为空")
    elif response["errcode"] == 40003:
        print("推送消息失败，请检查微信号是否正确")
    elif response["errcode"] == 0:
        print("推送消息成功")
    else:
        print(response)



try:
    with open("config.txt", encoding="utf-8") as f:
        config = eval(f.read())
except FileNotFoundError:
    print("推送消息失败，请检查config.txt文件是否与程序位于同一路径")
    os.system("pause")
    sys.exit(1)
except SyntaxError:
    print("推送消息失败，请检查配置文件格式是否正确")
    os.system("pause")
    sys.exit(1)

def yx():
    # 获取accessToken
    accessToken = get_access_token()
    # 接收的用户
    users = config["user"]
    # 传入地区获取天气信息
    region = config["region"]
    temp,weather, wind_dir = get_weather(region)
    note_ch = config["note_ch"]

    if note_ch == "":
        # 获取词霸每日金句
        # note_ch, note_en = get_ciba()
        #获取网易云文案
        note_ch = wenan()
        print("文案:",note_ch)
    # 公众号推送消息
    for user in users:
        send_message(user, accessToken, region, weather, temp, wind_dir, note_ch)
        # send_message(user, accessToken, note_ch, note_en)
    # os.system("pause")

if __name__ == '__main__':
    yx()#运行发送
