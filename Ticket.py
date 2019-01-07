#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

import requests
import urllib.parse
import sys
import time
import random
import re
import info
import mail
from PIL import Image
from requests import urllib3
import datetime


def print_s(string):
    time_info = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    print("[{}] {}".format(time_info, string))


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
        self.station_map_reverse = {}
        self.submit_token = ""
        self.key_check_is_change = ""
        self.passenger_list = []
        self.passenger_ticket_str = ""
        self.old_passenger_str = ""
        self.order_id = ""
        self.select_date = ""
        self.select_train = []
        self.select_seat = ""
        self.seat_code = {
            "硬座": "1",
            "软座": "2",
            "硬卧": "3",
            "软卧": "4",
            "二等座": "O",
            "一等座": "M",
            "商务座": "9"
        }
        self.seat_num = {
            "硬座": 29,
            "软座": 24,
            "硬卧": 28,
            "软卧": 23,
            "二等座": 30,
            "一等座": 31,
            "商务座": 32,
            "动卧": 33,
            "高级软卧": 21
        }
        self.last_train_dict = {}

    def get_stations(self):
        print_s("获取站名编码...")
        station_url = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
        response = self.session.get(station_url)
        if response.status_code == 200:
            print_s("站名编码获取成功")
            result = response.text.split('@')[1:]
            for item in result:
                station_name = item.split('|')[1]
                station_code = item.split('|')[2]
                self.station_map[station_name] = station_code
                self.station_map_reverse[station_code] = station_name

    def query_tickets(self, from_station, to_station, train_date):
        for date_d in train_date:
            for from_s in from_station:
                for to_s in to_station:
                    res = self.query(from_s, to_s, date_d)
                    if res:
                        return True
                    time.sleep(1)
        return False

    def query(self, from_station, to_station, train_date):
        print_s("查询余票...")
        print_s("出发站：{}   到达站：{}  乘车日期：{}".format(from_station, to_station, train_date))
        train_key = '{}|{}|{}'.format(self.station_map[from_station], self.station_map[to_station], train_date)
        query_url = 'https://kyfw.12306.cn/otn/leftTicket/queryZ'
        param = {
            'leftTicketDTO.train_date': train_date,
            'leftTicketDTO.from_station': self.station_map[from_station],
            'leftTicketDTO.to_station': self.station_map[to_station],
            "purpose_codes": "ADULT"
        }
        response = self.session.get(url=query_url, params=param)
        res = False
        if response.status_code == 200:
            print_s("余票查询成功")
            train_list = response.json()["data"]["result"]
            train_counts = len(train_list)
            print_s('车次 {} 列，所有指定车次查询结果:'.format(train_counts))

            select_train, select_seat = self.filter(train_list)
            if select_train == '' or select_seat == '':
                # 查询无票，检查是否有新开列车符合条件
                select_train, select_seat = self.check_new_trains(train_list, train_key)
                if select_train != '' and select_seat != '':
                    train_info = select_train.split('|')
                    self.select_train = train_info
                    self.select_seat = select_seat
                    self.select_date = train_date
                    res = True
                else:
                    res = False
            else:
                train_info = select_train.split('|')
                self.select_train = train_info
                self.select_seat = select_seat
                self.select_date = train_date
                res = True
            self.last_train_dict[train_key] = train_list
        else:
            print_s("余票查询失败")
            print(response)
            res = False
        return res

    def print_s_train_detail(self, trains):
        for train in trains:
            infos = train.split("|")
            print_s("车次 %-10s %s 至 %-10s 硬卧|%-10s 软卧|%-10s 二等座|%-10s 一等座|%-10s 硬座|%-10s 软座|%-10s" % (
                infos[3],
                self.station_map_reverse[infos[6]],
                self.station_map_reverse[infos[7]],
                infos[28],
                infos[23],
                infos[30],
                infos[31],
                infos[29],
                infos[24]))

    def check_new_trains(self, train_list, check_key):
        has_key = check_key in self.last_train_dict.keys()
        if not has_key:
            return '', ''
        old_trains = self.last_train_dict[check_key]
        if len(old_trains) < len(train_list) and len(old_trains) != 0:
            print_s('上次车次共{} 本次车次共{}'.format(len(old_trains), len(train_list)))
            print_s('指定车次无票，发现新开列车')
            old_train_nums = []
            for train in old_trains:
                old_train_nums.append(train.split("|")[3])
            new_trains = []
            for new_train in train_list:
                if old_train_nums.count(new_train.split("|")[3]) > 0:
                    continue
                new_trains.append(new_train)

            def filter_train(trains):
                info_array = trains.split("|")
                if info_array[8] > info.start_time and info_array[9] > info.arrive_time:
                    return True
                return False

            if len(new_trains) > 0:
                # 检查新车是否满足条件
                new_trains = list(filter(filter_train, new_trains))
            return self.further_filter(new_trains)
        else:
            return '', ''

    def login_captcha_check(self):
        retry_count = 0
        while True:
            if retry_count > 5:
                print_s("重试次数达5次，系统退出...")
                sys.exit()

            print_s("获取验证码图片...")
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

            print_s("验证码校验中...")
            captcha_check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
            data = {
                "answer": answer_str[1:],
                "login_site": "E",
                "rand": "sjrand"
            }
            response = self.session.post(captcha_check_url, data).json()
            if response["result_code"] == "4":
                print_s(response["result_message"])
                break
            else:
                print_s("验证码校验失败，开始重试...")
                retry_count += 1
                continue

    def login(self):
        self.login_captcha_check()
        print_s("用户名密码登录...")
        login_url = "https://kyfw.12306.cn/passport/web/login"
        data = {
            "username": info.user_name,
            "password": info.password,
            "appid": "otn"
        }
        response = self.session.post(login_url, data)
        login_result = response.json()
        if login_result["result_code"] == 0:
            print_s(login_result["result_message"])
            self.session.cookies["uamtk"] = login_result["uamtk"]
        else:
            print_s("用户名密码错误，系统退出...")
            print_s(login_result)
            sys.exit()

        print_s("登录第一次验证...")
        login_first_verify_url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
        data = {
            "appid": "otn"
        }
        verify_result = self.session.post(login_first_verify_url, data).json()
        tk = ""
        if verify_result["result_code"] == 0:
            print_s(verify_result)
            tk = verify_result["newapptk"]
        else:
            print_s("验证失败，系统退出...")
            sys.exit()

        print_s("登录第二次验证...")
        login_second_verify_url = "https://kyfw.12306.cn/otn/uamauthclient"
        data = {
            "tk": tk
        }
        verify_result = self.session.post(login_second_verify_url, data).json()
        if verify_result["result_code"] == 0:
            print_s(verify_result)
            print_s("验证成功，当前登录用户：{}".format(verify_result["username"]))
        else:
            print_s("验证失败，系统退出...")
            sys.exit()

    def check_user_login_status(self):
        retry_count = 0
        while True:
            if retry_count >= 3:
                print_s("登录失败")
                return False
            print_s("检查用户登录状态...")
            check_user_url = "https://kyfw.12306.cn/otn/login/checkUser"
            data = {
                "_json_att": ""
            }
            response = self.session.post(check_user_url, data).json()
            if response['httpstatus'] == 200:
                if not response["data"]["flag"]:
                    print_s("用户未登录，开始登录...")
                    self.login()
                    retry_count += 1
                    continue
                else:
                    return True
            else:
                print_s("检查用户登录状态失败...")
                retry_count += 1
                continue

    def submit_order_request(self):
        print_s("提交订单请求...")
        submit_order_url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"
        data = {
            "secretStr": urllib.parse.unquote(self.select_train[0]),
            "train_date": self.select_date,
            "back_train_date": "2018-10-08",
            "tour_flag": "dc",
            "purpose_codes": "ADULT",
            "query_from_station_name": self.station_map_reverse[self.select_train[6]],
            "query_to_station_name": self.station_map_reverse[self.select_train[7]],
            "undefined": ""
        }
        response = self.session.post(submit_order_url, data).json()
        if response["status"]:
            print_s("订单请求提交成功")
            return True
        else:
            print_s("订单请求提交失败，退出...")
            print_s(response)
            return False

    def get_submit_token(self):
        print_s("获取提交订单Token...")
        token_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        data = {
            "_json_att": ""
        }
        response = self.session.post(token_url, data)
        token = re.findall(r"globalRepeatSubmitToken = '(.*?)'", response.text)[0]
        key = re.findall(r"key_check_isChange':'(.*?)'", response.text)[0]
        if token != "" and key != "":
            print_s("获取提交订单Token成功")
            self.submit_token = token
            self.key_check_is_change = key
            return True
        else:
            print_s("获取提交订单Token失败，退出...")
            return False

    def get_passenger_list(self):
        print_s("获取乘客列表...")
        passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
        data = {
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.submit_token
        }
        response = self.session.get(url=passenger_url, params=data).json()
        if response["status"]:
            print_s("获取乘客列表成功")
            self.passenger_list = response["data"]["normal_passengers"]
            return True
        else:
            print_s("获取乘客列表失败，退出...")
            return False

    def confirm_passengers(self):
        pass

    def get_order_captcha(self):
        captcha_url = "https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&{}".format(
            random.random())
        picture = self.session.get(captcha_url).content
        with open("order_captcha.jpg", "wb") as f:
            f.write(picture)

    def check_order_info(self):
        retry_count = 0
        while True:
            if retry_count > 2:
                print_s("重试次数达2次，退出...")
                return False

            print_s("核对订单信息...")
            check_order_url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
            passengers = []
            for select_name in info.passenger_names:
                for p in self.passenger_list:
                    if select_name == p["passenger_name"]:
                        passenger_info = {
                            "passenger_flag": p["passenger_flag"],
                            "passenger_type": p["passenger_type"],
                            "passenger_name": p["passenger_name"],
                            "passenger_id_type_code": p["passenger_id_type_code"],
                            "passenger_id_no": p["passenger_id_no"],
                            "mobile_no": p["mobile_no"]
                        }
                        passengers.append(passenger_info)
                        print_s("已选择乘客：{}".format(passenger_info['passenger_name']))
                        break

            for passenger_info in passengers:
                self.passenger_ticket_str += "%s,%s,%s,%s,%s,%s,%s,N_" % (self.seat_code[self.select_seat],
                                                                          passenger_info["passenger_flag"],
                                                                          passenger_info["passenger_type"],
                                                                          passenger_info["passenger_name"],
                                                                          passenger_info["passenger_id_type_code"],
                                                                          passenger_info["passenger_id_no"],
                                                                          passenger_info["mobile_no"])
                self.old_passenger_str += "%s,%s,%s,%s_" % (passenger_info["passenger_name"],
                                                            passenger_info["passenger_id_type_code"],
                                                            passenger_info["passenger_id_no"],
                                                            passenger_info["passenger_type"])
            # 去除最后一个下划线
            self.passenger_ticket_str = self.passenger_ticket_str[0:-1]
            data = {
                "cancel_flag": "2",
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
                print_s("核对订单信息完成")
                return True
            else:
                print_s("核对订单信息失败，开始重试...")
                print_s(response)
                retry_count += 1
                continue

    def get_queue_count(self):
        print_s("确认坐席...")
        queue_count_url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        data = {
            "train_date": time.strftime("%a %b %d %Y %H:%M:%S",
                                        time.strptime(self.select_date, "%Y-%m-%d")) + " GMT+0800 (中国标准时间)",
            "train_no": self.select_train[2],
            "stationTrainCode": self.select_train[3],
            "seatType": self.seat_code[self.select_seat],
            "fromStationTelecode": self.select_train[6],
            "toStationTelecode": self.select_train[7],
            "leftTicket": self.select_train[12],
            "purpose_codes": "00",
            "train_location": self.select_train[15],
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": self.submit_token
        }
        response = self.session.post(queue_count_url, data).json()
        if response["status"]:
            print_s("确认成功")
            return True
        else:
            print_s("确认坐席失败")
            print_s(response)
            return False

    def confirm_order(self):
        retry_count = 0
        while True:
            if retry_count > 6:
                print_s("重试次数达6次，系统退出...")
                return False

            print_s("提交订单...")
            confirm_order_url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"
            data = {
                "passengerTicketStr": self.passenger_ticket_str,
                "oldPassengerStr": self.old_passenger_str,
                "randCode": "",
                "purpose_codes": "00",
                "key_check_isChange": self.key_check_is_change,
                "leftTicketStr": self.select_train[12],
                "train_location": self.select_train[15],
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
                print_s("订单已提交")
                return True
            else:
                print_s("订单提交失败，开始重试...")
                print_s(response)
                retry_count += 1
                continue

    def query_order_wait_time(self):
        print_s("查询剩余排队时间...")
        query_count = 1
        while query_count < 10000:
            print_s("当前第{}次查询...".format(query_count))
            query_url = "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime"
            data = {
                "random": str(round(time.time() * 1000)),
                "tourFlag": "dc",
                "_json_att": "",
                "REPEAT_SUBMIT_TOKEN": self.submit_token
            }
            response = self.session.get(url=query_url, params=data).json()
            if response["data"]["queryOrderWaitTimeStatus"]:
                print_s("查询成功")
                wait_time = response["data"]["waitTime"]
                print_s("剩余排队时间：{}".format(wait_time))
                if wait_time == -1:
                    self.order_id = response["data"]["orderId"]
                    print_s("订单处理完毕")
                    break
                elif wait_time == -2:
                    print_s("取消次数太多，今日无法订票...")
                    print_s(response)
                    return False
                else:
                    query_count += 1
                    time.sleep(1)
                    continue
        return True

    def query_order_result(self):
        retry_count = 0
        while True:
            if retry_count > 10:
                print_s("重试次数达10次，系统退出...")
                return False

            print_s("查询订单处理结果...")
            order_result_url = "https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue"
            data = {
                "orderSequence_no": self.order_id,
                "_json_att": "",
                "REPEAT_SUBMIT_TOKEN": self.submit_token
            }
            response = self.session.post(order_result_url, data).json()
            print_s(response)
            if response["data"]["submitStatus"]:
                print_s("车票预订成功 订单号：{}".format(self.order_id))
                if info.mail_notification:
                    mail.send_email('车票预订成功，订单号: {}，车次: {} {}至{} 坐席: {}，请尽快登录12306支付^_^'.format(self.order_id,
                                                                                            self.select_train[3],
                                                                                            self.select_train[6],
                                                                                            self.select_train[7],
                                                                                            self.select_seat))
                return True
            elif response["status"]:
                print_s("车票预订失败")
                print_s(response)
                return False
            else:
                print_s("车票预订查询失败，开始重试...")
                print_s(response)
                retry_count += 1
                continue

    def book(self):

        delay_time = 1.0
        res = self.check_user_login_status()
        if not res:
            return res

        res = self.submit_order_request()
        if not res:
            return res

        res = self.get_submit_token()
        if not res:
            return res

        res = self.get_passenger_list()
        if not res:
            return res
        time.sleep(delay_time)

        res = self.check_order_info()
        if not res:
            return res

        res = self.get_queue_count()
        time.sleep(delay_time)
        if not res:
            return res

        res = self.confirm_order()
        if not res:
            return res

        res = self.query_order_wait_time()
        if not res:
            return res
        res = self.query_order_result()

        return res

    def filter(self, train_list):
        # 过滤函数
        def filter_train(train_str):
            for train_num in info.trains:
                if train_num in train_str:
                    return True
            return False

        # 筛选符合条件的车次
        if not len(info.trains) == 0:
            train_list = list(filter(filter_train, train_list))
        return self.further_filter(train_list)

    def further_filter(self, train_list):
        # 坐席优先
        self.print_s_train_detail(train_list)
        for seat in info.seats:
            for train in train_list:
                train_info = train.split("|")
                seat_info = train_info[self.seat_num[seat]]
                if seat_info == '' or seat_info == '无' or seat_info == '0':
                    continue
                else:
                    if seat_info == '有':
                        return train, seat
                    else:
                        # 暂时不支持部分提交
                        if int(seat_info) >= len(info.passenger_names):
                            return train, seat
                        else:
                            return '', ''
        return '', ''

    def grab(self):
        duration = info.query_frequece
        retry_count = 0
        while True:
            if retry_count > info.retry_count:
                print_s("重试达上限，系统退出...")
                sys.exit()
            if self.query_tickets(info.from_station, info.to_station, info.date):
                print_s('当前有票,   车次 {}   坐席 {}'.format(self.select_train[3], self.select_seat))
                res = self.book()
                if not res:
                    time.sleep(duration)
                    continue
                break
            else:
                print_s('查询无票，开始重试...')
                retry_count += 1
                time.sleep(duration)
                continue

    def scheduled_book(self):
        print_s("===> 等待抢票...")
        start_time = datetime.datetime(info.assign_time[0], info.assign_time[1], info.assign_time[2],
                                       info.assign_time[3], info.assign_time[4], info.assign_time[5])
        while datetime.datetime.now() < start_time:
            time.sleep(1)
        print_s('===> 开始抢票！！！')
        self.grab()


ticket = Tickets()
ticket.get_stations()
ticket.login()
if len(info.assign_time) == 0:
    ticket.grab()
else:
    ticket.scheduled_book()
