#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

import requests
import info
# from requests.packages import urllib3

class Tickets(object):

    def __init__(self):
        # 消除证书警告
        # requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

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
        self.station_map = {}


    def get_stations(self):

        stationUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
        response = self.session.get(stationUrl, verify=False)
        if response.status_code == 200:
            print("站名编码获取成功")
            result = response.text.split('@')[1:]
            for item in result:
                station_name = item.split('|')[1]
                station_code = item.split('|')[2]
                self.station_map[station_name] = station_code
                # print("车站：{} 编码：{}".format(station_name, station_code))

    def leftTicketsQuery(self, from_station, to_station, train_date):

        queryUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryO'
        param = {
            'leftTicketDTO.train_date':train_date,
            'leftTicketDTO.from_station':from_station,
            'leftTicketDTO.to_station':to_station,
            "purpose_codes":"ADULT"
        }
        response = self.session.get(url=queryUrl, params=param, headers=self.session.headers, verify=False)
        if response.status_code == 200:
            print("余票查询成功")
            trainList = response.json()["data"]["result"]
            for train in trainList:
                print("车次 {}：{}".format(train.split("|")[3], train))

    def login(self):
        pass

ticket = Tickets()
ticket.get_stations()
ticket.leftTicketsQuery(info.from_station, info.to_station, info.date)