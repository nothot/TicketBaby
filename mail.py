#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Author  : Dream

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import info

# 第三方 SMTP 服务
mail_host = info.mail_host  # 设置服务器
mail_user = info.mail_account  # 用户名
mail_pass = info.mail_password  # 口令

sender = info.mail_account
receivers = info.mail_receivers  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱


def send_email(text):
    # 构造邮件对象MIMEMultipart对象
    # 下面的主题，发件人，收件人，日期是显示在邮件页面上的。
    msg = MIMEMultipart('mixed')
    msg['Subject'] = 'TicketBaby 抢票成功通知'
    msg['From'] = '{} <{}>'.format(info.mail_account, info.mail_account)

    # 收件人为多个收件人,通过join将列表转换为以;为间隔的字符串
    msg['To'] = ";".join(receivers)

    # 构造文字内容
    text_plain = MIMEText(text,'plain', 'utf-8')
    msg.attach(text_plain)

    try:
        smtpObj = smtplib.SMTP()
        print('连接邮件服务器...')
        smtpObj.connect(mail_host, 25)  # 25 为 SMTP 端口号
        print("登录邮箱账户...")
        smtpObj.login(mail_user, mail_pass)
        print("邮件发送中...")
        smtpObj.sendmail(sender, receivers, msg.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")
