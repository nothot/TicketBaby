#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

# 12306 Account
# ---------------------------------------------
user_name = ""
password = ""

# ---------------------------------------------
# --------------- 疯狂抢票 ---------------------
# ---------------------------------------------

# 乘车日期，可多选，必填，至少填一个, 顺序代表优先级
date = [
    "2019-01-31", "2019-02-01"
]

# 出发站，可多选，必填，至少填一个, 顺序代表优先级
from_station = [
    "上海"
]

# 到达站，可多选，必填，至少填一个, 顺序代表优先级
to_station = [
    "武汉", "恩施"
]

# 乘客，可多选，必填，至少填一个
passenger_names = [
    "某某"
]

# 坐席，可多选，必填，至少填一个, 顺序代表优先级
seats = [
    "硬卧", "软卧"
]

# 指定车次，可多选, 顺序代表优先级，非必填，不填默认所有车次
trains = [
    "K973", "Z59"
]

# --------------------------------------------
# -------------- 高级选项 ---------------------
# --------------------------------------------

# 发现新开列车，检查发车时间和到达时间是否满足要求，是则自动购买
# --------------------------------------------
check_new_train = True
start_time = "18:30"    # 发车在该时间之后
arrive_time = "04：00"  # 到达在该时间之后

# 抢票重试上限
# --------------------------------------------
retry_count = 10000000

# 查票频率
# --------------------------------------------
query_frequece = 5.0

# 指定时间开抢，默认空
# --------------------------------------------
assign_time = ()  # 年月日时分秒
# assign_time = (2018, 12, 18, 10, 17, 1)  # 年月日时分秒

# 抢票成功邮件通知
# --------------------------------------------
mail_notification = True    # 默认发送通知
mail_host = "smtp.126.com"  # 发件服务器，示例为126邮箱
mail_account = "xxxxxxx@126.com"   # 邮箱账号
mail_password = "xxxxxx"      # 邮箱密码（网易需使用授权码）
mail_receivers = [              # 收件接收邮箱
    'xxxxxxxxx@qq.com'
]
