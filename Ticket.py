#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

import requests
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


    def get_stations(self):

        stationUrl = 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9035'
        response = self.session.get(stationUrl, verify=False)
        print(response.text)

    def leftTicketsQuery(self):
        pass
        """
        余票查询地址：https://kyfw.12306.cn/otn/leftTicket/queryO
        参数： leftTicketDTO.train_date=20180806，leftTicketDTO.from_station={}，leftTicketDTO.to_station={}，purpose_codes={}
        """
        queryUrl = 'https://kyfw.12306.cn/otn/leftTicket/queryO'
        param = {
            'leftTicketDTO.train_date':"2018-10-20",
            'leftTicketDTO.from_station':'SHH',
            'leftTicketDTO.to_station':'BJP',
            "purpose_codes":"ADULT"
        }
        response = self.session.get(url=queryUrl, params=param, headers=self.session.headers, verify=False)
        print("code: {}".format(response.status_code))
        print(response.json())


ticket = Tickets()
ticket.get_stations()
ticket.leftTicketsQuery()
