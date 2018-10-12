#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

{
    """
    **********************  余票查询    **********************
    余票查询地址：
        https://kyfw.12306.cn/otn/leftTicket/queryO     GET
    参数： 
        leftTicketDTO.train_date=2018-08-06，
        leftTicketDTO.from_station={}，
        leftTicketDTO.to_station={}，
        purpose_codes={}
    响应：
        预订 1
        车次 3
        始发站 4
        终点站 5 
        要坐的站 6
        要到的站 7
        出发时间 8
        到达时间 9
        历时 10
        是否可以预订（Y可以 N和IS_TIME_NOT_BUY 不可以）   11  
        leftTicket 12 ？
        日期 13
        trainLocation 15 ？
        高级软卧 21
        软卧 23
        无座 26
        硬卧 28
        硬座 29
        二等座 30
        一等座 31
        商务座 32
        动卧 33
        
    **********************  登录   **********************
    第一步：获取验证码
    
    获取验证码图片地址：
        https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5160082611736014   GET
    
    验证码验证地址：
        https://kyfw.12306.cn/passport/captcha/captcha-check    POST
    参数：
        answer=110,39,116,116
        login_site=E
        rand=sjrand
    响应：
        result_code=4 校验成功
        
    第二步：登录
    
    登录地址：
        https://kyfw.12306.cn/passport/web/login    POST
    参数：
        username=****
        password=****
        appid=otn
    响应：
        result_code=0 成功
    """
}