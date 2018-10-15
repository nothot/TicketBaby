#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

import requests
import urllib.parse
import sys
import time
import re
import info
from PIL import Image
from requests import urllib3


class Tickets(object):

    def __init__(self):
        # 消除证书警告
        urllib3.disable_warnings()

        self.session = requests.session()
        self.session.headers = {
            'Host': 'kyfw.12306.cn',
            'Origin': 'https://kyfw.12306.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
        }
        self.session.verify = False
        self.station_map = {}
        self.secret_str = ""
        self.submit_token = ""
        self.key_check_is_change = ""
        self.passenger_list = []
        self.train_no = ""
        self.train_code = ""
        self.left_tickets = ""
        self.train_location = ""
        self.passenger_ticket_str = ""
        self.old_passenger_str = ""
        self.order_id = ""

    def get_stations(self):
        print("获取站名编码...")
        station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
        response = self.session.get(station_url)
        if response.status_code == 200:
            print("站名编码获取成功")
            result = response.text.split('@')[1:]
            for item in result:
                station_name = item.split('|')[1]
                station_code = item.split('|')[2]
                self.station_map[station_name] = station_code

    def query(self, from_station, to_station, train_date):
        print("查询余票...")
        print("出发站：{}   到达站：{}  乘车日期：{}".format(from_station, to_station, train_date))
        query_url = 'https://kyfw.12306.cn/otn/leftTicket/queryO'
        param = {
            'leftTicketDTO.train_date': train_date,
            'leftTicketDTO.from_station': from_station,
            'leftTicketDTO.to_station': to_station,
            "purpose_codes":"ADULT"
        }
        response = self.session.get(url=query_url, params=param)
        if response.status_code == 200:
            print("余票查询成功")
            train_list = response.json()["data"]["result"]
            for train in train_list:
                print("车次 {}：{}".format(train.split("|")[3], train))
            train_info = train_list[1].split("|")
            self.secret_str = urllib.parse.unquote(train_info[0])
            self.train_no = train_info[2]
            self.train_code = train_info[3]
            self.left_tickets = train_info[12]
            self.train_location = train_info[15]

    def login_captcha_check(self):
        retry_count = 0
        while True:
            if retry_count > 5:
                print("重试次数达5次，系统退出...")
                sys.exit()

            print("获取验证码图片...")
            captcha_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5160082611736014"
            picture = self.session.get(captcha_url).content
            with open("captcha.jpg", "wb") as f:
                f.write(picture)
            image = Image.open("captcha.jpg")
            image.show()
            answer = input("输入验证码图片答案（图片从左上到右下编号1~8），以空格分隔：")
            captcha_location_map = {
                '1': (31, 35),
                '2': (116, 46),
                '3': (191, 24),
                '4': (243, 50),
                '5': (22, 114),
                '6': (117, 94),
                '7': (167, 120),
                '8': (251, 105)
            }
            answer_str = ""
            for i in answer.split(" "):
                ans = "," + str(captcha_location_map[i][0]) + "," + str(captcha_location_map[i][1])
                answer_str += ans

            print("验证码校验中...")
            captcha_check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
            data = {
                "answer": answer_str[1:],
                "login_site": "E",
                "rand": "sjrand"
            }
            response = self.session.post(captcha_check_url, data).json()
            if response["result_code"] == "4":
                print(response["result_message"])
                break
            else:
                print("验证码校验失败，开始重试...")
                retry_count += 1
                continue

    def login(self):
        self.login_captcha_check()
        print("用户名密码登录...")
        login_url = "https://kyfw.12306.cn/passport/web/login"
        data = {
            "username": info.user_name,
            "password": info.password,
            "appid": "otn"
        }
        response = self.session.post(login_url, data)
        login_result = response.json()
        if login_result["result_code"] == 0:
            print(login_result["result_message"])
            self.session.cookies["uamtk"] = login_result["uamtk"]
        else:
            print("用户名密码错误，系统退出...")
            print(login_result)
            sys.exit()

        print("登录第一次验证...")
        login_first_verify_url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {
            "appid": "otn"
        }
        verify_result = self.session.post(login_first_verify_url, data).json()
        tk = ""
        if verify_result["result_code"] == 0:
            print(verify_result)
            tk = verify_result["newapptk"]
        else:
            print("验证失败，系统退出...")
            sys.exit()

        print("登录第二次验证...")
        login_second_verify_url = "https://kyfw.12306.cn/otn/uamauthclient"
        data = {
            "tk":tk
        }
        verify_result = self.session.post(login_second_verify_url, data).json()
        if verify_result["result_code"] == 0:
            print(verify_result)
            print("验证成功，当前登录用户：{}".format(verify_result["username"]))
        else:
            print("验证失败，系统退出...")
            sys.exit()

    def check_user_login_status(self):
        retry_count = 0
        while True:
            if retry_count > 3:
                print("重试次数达3次，系统退出...")
                sys.exit()

            print("检查用户登录状态...")
            check_user_url = "https://kyfw.12306.cn/otn/login/checkUser"
            data = {
                "_json_att": ""
            }
            response = self.session.post(check_user_url, data).json()
            if not response["data"]["flag"]:
                print("用户未登录，开始登录...")
                self.login()
                retry_count += 1
                continue
            break

    def submit_order_request(self):
        print("提交订单请求...")
        submit_order_url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        data = {
            "secretStr": self.secret_str,
            "train_date": info.date,
            "back_train_date": "2018-11-06",
            "tour_flag": "dc",
            "purpose_codes": "ADULT",
            "query_from_station_name": info.from_station,
            "query_to_station_name": info.to_station,
            "undefined": ""
        }
        response = self.session.post(submit_order_url, data).json()
        if response["status"]:
            print("订单请求提交成功")
        else:
            print("订单请求提交失败，系统退出...")
            sys.exit()

    def get_submit_token(self):
        print("获取提交订单Token...")
        token_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        data = {
            "_json_att": ""
        }
        response = self.session.post(token_url, data)
        token = re.findall(r"globalRepeatSubmitToken = '(.*?)'", response.text)[0]
        key = re.findall(r"key_check_isChange':'(.*?)'", response.text)[0]
        if token != "" and key != "":
            print("获取提交订单Token成功")
            self.submit_token = token
            self.key_check_is_change = key
        else:
            print("获取提交订单Token失败，系统退出...")
            sys.exit()

    def get_passenger_list(self):
        print("获取乘客列表...")
        passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        data = {
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.submit_token
        }
        response = self.session.get(url=passenger_url, params=data).json()
        if response["status"]:
            print("获取乘客列表成功")
            self.passenger_list = response["data"]["normal_passengers"]
        else:
            print("获取乘客列表失败，系统退出...")
            sys.exit()

    def confirm_passengers(self):
        pass

    def check_order_info(self):
        retry_count = 0
        while True:
            if retry_count > 3:
                print("重试次数达3次，系统退出...")
                sys.exit()

            print("核对订单信息...")
            check_order_url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
            passenger_info = {}
            for p in self.passenger_list:
                if info.passenger_name == p["passenger_name"]:
                    passenger_info = {
                        "passenger_flag": p["passenger_flag"],
                        "passenger_type": p["passenger_type"],
                        "passenger_name": p["passenger_name"],
                        "passenger_id_type_code": p["passenger_id_type_code"],
                        "passenger_id_no": p["passenger_id_no"],
                        "mobile_no": p["mobile_no"]
                    }
            print("选择乘客：{}".format(passenger_info["passenger_name"]))
            seat_type = "1"
            self.passenger_ticket_str = "%s,%s,%s,%s,%s,%s,%s,N" % (seat_type,
                                                               passenger_info["passenger_flag"],
                                                               passenger_info["passenger_type"],
                                                               passenger_info["passenger_name"],
                                                               passenger_info["passenger_id_type_code"],
                                                               passenger_info["passenger_id_no"],
                                                               passenger_info["mobile_no"])
            self.old_passenger_str = "%s,%s,%s,%s_" % (passenger_info["passenger_name"],
                                                  passenger_info["passenger_id_type_code"],
                                                  passenger_info["passenger_id_no"],
                                                  passenger_info["passenger_type"])
            data = {
                "cancel_flag":"2",
                "bed_level_order_num": "000000000000000000000000000000",
                "passengerTicketStr": self.passenger_ticket_str,
                "oldPassengerStr": self.old_passenger_str,
                "tour_flag": "dc",
                "randCode": "",
                "whatsSelect": "1",
                "_json_att": "",
                "REPEAT_SUBMIT_TOKEN": self.submit_token
            }
            response = self.session.post(check_order_url, data).json()
            if response["data"]["submitStatus"]:
                print("核对订单信息完成")
                break
            else:
                print("核对订单信息失败，开始重试...")
                retry_count += 1
                continue

    def get_queue_count(self):
        print("确认坐席...")
        queue_count_url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        data = {
            "train_date": time.strftime("%a %b %d %Y %H:%M:%S", time.strptime(info.date, "%Y-%m-%d")) + " GMT+0800 (中国标准时间)",
            "train_no": self.train_no,
            "stationTrainCode": self.train_code,
            "seatType": "1",
            "fromStationTelecode": self.station_map[info.from_station],
            "toStationTelecode": self.station_map[info.to_station],
            "leftTicket": self.left_tickets,
            "purpose_codes": "00",
            "train_location": self.train_location,
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.submit_token
        }
        response = self.session.post(queue_count_url, data).json()
        if response["status"]:
            print("确认成功")
        else:
            print("确认失败")

    def confirm_order(self):
        retry_count = 0
        while True:
            if retry_count > 5:
                print("重试次数达5次，系统退出...")
                sys.exit()

            print("提交订单...")
            confirm_order_url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
            data = {
                "passengerTicketStr": self.passenger_ticket_str,
                "oldPassengerStr": self.old_passenger_str,
                "randCode": "",
                "purpose_codes": "00",
                "key_check_isChange": self.key_check_is_change,
                "leftTicketStr": self.left_tickets,
                "train_location": self.train_location,
                "choose_seats": "",
                "seatDetailType": "000",
                "whatsSelect": "1",
                "roomType": "00",
                "dwAll": "N",
                "_json_att": "",
                "REPEAT_SUBMIT_TOKEN": self.submit_token
            }
            response = self.session.post(confirm_order_url, data).json()
            if response["data"]["submitStatus"]:
                print("订单已提交")
                break
            else:
                print("订单提交失败，开始重试...")
                retry_count += 1
                continue

    def query_order_wait_time(self):
        print("查询剩余排队时间...")
        query_count = 1
        while True:
            print("当前第{}次查询...".format(query_count))
            query_url = "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime"
            data = {
                "random":str(round(time.time() * 1000)),
                "tourFlag":"dc",
                "_json_att":"",
                "REPEAT_SUBMIT_TOKEN":self.submit_token
            }
            response = self.session.get(url=query_url, params=data).json()
            if response["data"]["queryOrderWaitTimeStatus"]:
                print("查询成功")
                wait_time = response["data"]["waitTime"]
                print("剩余排队时间：{}".format(wait_time))
                if wait_time == -1:
                    self.order_id = response["data"]["orderId"]
                    print("订单处理完毕")
                    break
                elif wait_time == -2:
                    print("取消次数太多，今日无法订票，系统退出...")
                    sys.exit()
                else:
                    query_count += 1
                    time.sleep(1)
                    continue

    def query_order_result(self):
        retry_count = 0
        while True:
            if retry_count > 3:
                print("重试次数达3次，系统退出...")
                sys.exit()

            print("查询订单处理结果...")
            order_result_url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
            data = {
                "orderSequence_no":self.order_id,
                "_json_att":"",
                "REPEAT_SUBMIT_TOKEN":self.submit_token
            }
            response = self.session.post(order_result_url, data).json()
            print(response)
            if response["data"]["submitStatus"]:
                print("车票预订成功 订单号：{}".format(self.order_id))
                break
            elif response["status"]:
                print("车票预订失败")
                break
            else:
                print("车票预订查询失败，开始重试...")
                retry_count += 1
                continue

    def book(self):

        self.check_user_login_status()
        self.submit_order_request()
        self.get_submit_token()
        self.get_passenger_list()
        self.check_order_info()
        self.get_queue_count()
        self.confirm_order()
        self.query_order_wait_time()
        self.query_order_result()



ticket = Tickets()
ticket.get_stations()
ticket.query(ticket.station_map[info.from_station], ticket.station_map[info.to_station], info.date)
# ticket.book()