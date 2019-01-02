#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

{
    """
    ************************************************************
                            余票查询
    ************************************************************
    
    
    余票查询
    ------------------------------------------------------------
    地址：    
        https://kyfw.12306.cn/otn/leftTicket/queryA
    方式：
        GET
    参数： 
        leftTicketDTO.train_date        = 2018-08-06
        leftTicketDTO.from_station      = SHH，
        leftTicketDTO.to_station        = BJP，
        purpose_codes                   = ADULT         成人票
    响应：
        secretStr 0         提交订单需要
        预订 1
        列车编号 2            提交订单需要
        车次 3
        始发站 4
        终点站 5 
        要坐的站 6
        要到的站 7
        出发时间 8
        到达时间 9
        历时 10
        是否可以预订 11       Y可以 N和IS_TIME_NOT_BUY 不可以
        leftTicket 12       提交订单需要
        日期 13
        trainLocation 15    提交订单需要
        高级软卧 21
        软卧 23
        软座 24
        无座 26
        硬卧 28
        硬座 29
        二等座 30
        一等座 31
        商务座 32
        动卧 33
        
        
    查询列车时刻表
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/czxx/queryByTrainNo
    方式：
        GET
    参数：
        train_no                    = 550000D31490
        from_station_telecode       = SHH
        to_station_telecode         = VNP
        depart_date                 = 2018-10-14
        
        
        
    ************************************************************
                            用户登录
    ************************************************************
    
    
    第一步：获取验证码图片
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5160082611736014
    方式：
        GET
    
    验证码验证方式是坐标，大约一个验证码的宽高在70左右，所以每个验证码的坐标中点大约为
    -------------------------------------------------------
                  |                |               |
        35,35     |     105,35     |    175,35     |  245,35
                  |                |               |
    -------------------------------------------------------
                  |                |               |
       35,105     |     105,105    |    175,105    |  245,105
                  |                |               |
    -------------------------------------------------------


    第二步：验证码结果验证
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/passport/captcha/captcha-check
    方式：
        POST
    参数：
        answer          = 110,39,116,116
        login_site      = E                 固定值
        rand            = sjrand            固定值
    响应：
        result_code='4' 校验成功
        
        
    第三步：用户登录
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/passport/web/login
    方式：
        POST
    参数：
        username        = ****
        password        = ****
        appid           = otn               固定值
    响应：
        result_code=0 成功
        
        
    第四步：登录第一次验证
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/passport/web/auth/uamtk
    方式：
        POST
    参数：
        appid           = otn               固定值
    响应：
        result_code=0 通过
        权限验证，成功返回newapptk，该信息将做第二次登录验证
        
        
    第五步：登录第二次验证
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/uamauthclient
    方式：
        POST
    参数：
        tk              = newapptk          第一次验证返回信息
    响应：
        result_code=0 通过
        服务器会将tk设为cookies，并返回username
        
    
    
    ************************************************************
                            车票预订
    ************************************************************
    
    
    第一步：检查用户登录状态
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/login/checkUser
    方式：
        POST
    参数：
        _json_att        = ''    空值，可能无用
    响应：
        flag=true 已登录
        
        
    第二步：提交订单请求（即发起预定）
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest
    方式：
        POST
    参数：
        secretStr                   = ''
        train_date                  = 2018-11-01
        back_train_date             = 2018-10-13
        tour_flag                   = dc            单程票
        purpose_codes               = ADULT         成人票
        query_from_station_name     = 上海
        query_to_station_name       = 北京
        undefined                   = ''
    响应：
        status=true     订单提交请求成功
        
        
    第三步：获取提交订单需要的Token和Key
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/initDc
    方式：
        POST
    参数：
        _json_att        = ''    空值，可能无用
    响应：
        globalRepeatSubmitToken     Token
        key_check_isChange          Key
    
    
    第四步：获取乘客列表
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs
    方式：
        GET
    参数：
        _json_att               = ''    空值，可能无用
        REPEAT_SUBMIT_TOKEN     = ""    Token
    响应：
        status=true         成功
        normal_passengers   乘客列表
    
    
    第五步：获取提交订单验证码图片
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/passcodeNew/getPassCodeNew?module=passenger&rand=randp&0.6692619212397362
    方式：
        GET
    参数：
        见URL，最后一个是随机数
    响应：
        验证码图片
    备注：
        该步并非必要，在购票紧张时确认订单前会弹验证码，其他时候一般是不弹得，是否要弹在下个请求检查订单信息时通过返回字段判断
        checkOrderInfo接口返回ifShowPassCode='Y'就要弹验证码，因此这里还是要将验证码图片保存下来，在下一步判断是否弹出
    

    第六步：检查订单信息
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo
    方式：
        POST
    参数：
        cancel_flag                     = 2
        bed_level_order_num             = 000000000000000000000000000000        固定值
        passengerTicketStr              = E6%B0%91%2C1%2C411121199208153010     乘客信息
        oldPassengerStr                 = %E6%AE%B5%E6%A2%A6%E6%B0%91%2C1%2
        tour_flag                       = dc                                    单程
        randCode                        =
        whatsSelect                     = 1                                     
        _json_att                       =
        REPEAT_SUBMIT_TOKEN             = ad895d8d3d6c334ae835724b8f9a4830      Token
    响应：
        status=true     成功
        ifShowPassCode='Y'  需要弹验证码
        
        
    第七步：确认坐席
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount
    方式：
        POST
    参数：
        train_date                          = ""
        train_no                            = 55000K104811
        stationTrainCode                    = K1048
        seatType                            = 1
        fromStationTelecode                 = SHH
        toStationTelecode                   = LON
        leftTicket                          = f%252Bg7jaFkqCgs5Ctl
        purpose_codes                       = 00
        train_location                      = H3
        _json_att                           =
        REPEAT_SUBMIT_TOKEN                 = ad895d8d3d6c334ae835724b8f9a4830
    响应：
        status=true     成功

    
    第八步：确认完整订单信息，提交进入订单队列
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue
    方式：
        POST
    参数：
        passengerTicketStr                  = ""
        oldPassengerStr                     = ""
        randCode                            =
        purpose_codes                       = 00
        key_check_isChange                  = ""
        leftTicketStr                       = ""
        train_location                      = H3
        choose_seats                        =
        seatDetailType                      = 000
        whatsSelect                         = 1
        roomType                            = 0
        dwAll                               = N
        _json_att                           =
        REPEAT_SUBMIT_TOKEN                 = 6398aa8b04876c
    响应：
        submitStatus=true   订单提交成功
        
        
    第九步：查询当前排队剩余时间
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime
    方式：
        GET
    参数：
        random                              = 1539417744419         随机字符串
        tourFlag                            = dc
        _json_att                           =
        REPEAT_SUBMIT_TOKEN                 = 6398aa8b04876
    响应：
        queryOrderWaitTimeStatus=true   查询成功
        waitTime                        剩余等待时间，
                                        -1 表示处理完毕，订单已生成结果
                                        -2 订票取消次数过多，当日无法订票
        orderId                         订单号，用于查询订单结果，waitTime=-1处理完毕才会生成
        
        
    第十步：查询订单最终结果
    ------------------------------------------------------------
    地址：
        https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue
    方式：
        POST
    参数：
        orderSequence_no                    = E212530833           订单号
        _json_att                           =
        REPEAT_SUBMIT_TOKEN                 = 6398aa8b04876c1
    响应：
        submitStatus=true   订单完成，车票预订成功
        
    """
}

{
    '''
    坐席类型：
        硬座      1
        软座      2
        硬卧      3
        软卧      4
        二等座     O
        一等座     M
        商务座     9
    '''
}