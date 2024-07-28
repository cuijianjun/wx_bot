import concurrent.futures
import configparser
import os
import os.path
import queue
import random
import re
import sys
import threading
import time
import uuid
from datetime import datetime
import requests
from urllib.parse import urljoin
import hashlib

import pyautogui
import pygetwindow as gw
from uiautomation import WindowControl

from utils.convert_time import convert_time
from utils.deque import FixedSizeQueue
from utils.fly_book import *
from utils.jd import search_res
from utils.model import call_with_messages, get_res_list
from utils.selenium_get_location import launch_browser, search
from utils.str_to_hash import string_to_short_hash

file_lock = threading.Lock()

api_ver_order = ""


# 无限循环 用线程池监控微信消息列表的每一行，并调用 msg_execute() 将捕捉到的单个消息，加入队列
def get_msg(wx, fix_msg_queue_total, wait_for_exec_queue, psw):
    while True:
        e = threading.Event()
        e.wait(random.randint(100, 300) / 1000)
        # 刷新微信窗口中的群聊列表
        try:
            ListControl_conmunicate = wx.ListControl(Name='会话')
        except:
            continue

        for msg in ListControl_conmunicate.GetChildren():
            p = threading.Thread(target=msg_execute, args=(msg, fix_msg_queue_total, wait_for_exec_queue))
            p.start()


def is_orderable(user_id: str, msg_hash: str) -> bool:
    """检测是否可接单"""
    global api_ver_order
    if api_ver_order == "":
        # 加载配置文件
        config = configparser.ConfigParser()
        config.read('config.ini', encoding='utf-8')
        api_ver_order = config.get('config', 'api_ver_order')

    url = urljoin(api_ver_order, "/api/verOrder")
    req = requests.post(url, params={"user_id": user_id, "message_hash": msg_hash})

    if req.status_code == 200:
        try:
            if req.json().get('code') == 0:
                return True
        except Exception:
            print("verOrder api error.")
    return False


# 将捕捉到的单个消息，加入队列，并更新全局dict_all
def msg_execute(msg, fix_msg_queue_total, wait_for_exec_queue, psw):
    try:
        # 排除"折叠置顶"的按钮
        if len(list(msg.GetFirstChildControl().GetChildren())) == 1:
            return

        # 获取消息
        content = msg.GetFirstChildControl().GetChildren()[1].GetLastChildControl().GetFirstChildControl().Name

        # 如果是置顶的空消息 则不处理
        if not content:
            return

        # 获取纯消息，不包含发送人
        if '条]' in content or '我]' in content:
            the_content = content.split('：', 1)[-1]
        else:
            the_content = content

        # 检测纯消息是否重复
        if string_to_short_hash(the_content) in fix_msg_queue_total.get_queue():
            return

        # 检测是否可接单
        if not is_orderable(psw, hashlib.md5(the_content.encode('utf-8')).hexdigest()):
            return

        fix_msg_queue_total.add(string_to_short_hash(the_content))

        # 获取用户名称
        user = msg.GetFirstChildControl().GetChildren()[1].GetFirstChildControl().GetFirstChildControl().Name

        next_msg = 'time：' + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S") + '---' + 'user：' + user + '---' + 'content：' + content + '---'
        wait_for_exec_queue.put(next_msg)


    except:
        print('事件无法调用任何订户')


# 开启5个线程执行该函数：从wait_for_exec_queue队列中获取 原生消息 交给 大模型切割、提取   然后存 dict_queue 队列
def exec_source_msg(wait_for_exec_queue, dict_queue, keys, refuse_keys, locations, fix_msg_queue):
    while True:
        # 从wait_for_exec_queue队列中获取  原生消息
        source_msg = wait_for_exec_queue.get()
        the_content = re.findall("content：(.+?)---", source_msg)[0]

        # 原始消息处理（去除群里的发信人）
        if '条]' in the_content or '我]' in the_content:
            the_content = the_content.split('：', 1)[-1]

        # 检测白名单关键词
        nokeys = True
        for key in keys:
            if key in the_content:
                nokeys = False
                break
        # 无白名单关键词，跳过
        if nokeys:
            continue

        # 分割换行符  ---  补充说明：﻿﻿（零宽度空格，代表微信消息中的"换行符" ） 代码：\ufeff
        split_lines = re.split('[\ufeff\n]', the_content)
        # 拼接换行符
        if len(split_lines) > 1:
            the_content = '\n'.join(split_lines)

        # 有白名单关键词，继续执行，调用  _______大模型_______  拆分详细信息 获取回答
        answer = call_with_messages(the_content)
        # 获取回答失败，跳过
        if not answer:
            continue

        # 获取大模型回答的字典
        res_list = get_res_list(answer)
        for res in res_list:
            # print(f"{res['work_time']}          {res['work_addr']}          {res['source_text']}")

            # 检测过滤省份
            nolocations = True
            for location in locations:
                if location in res['work_addr']:
                    nolocations = False
                    break
            # 无过滤省份关键词，跳过
            if nolocations:
                print(res['work_addr'], '非法省份')
                continue

            # 检测白名单关键词
            nokeys = True
            for key in keys:
                if key in res['source_text']:
                    nokeys = False
                    break
            # 无白名单关键词，跳过
            if nokeys:
                continue

            # 检测非法关键词
            has_refuse_keys = False
            for refuse_key in refuse_keys:
                if refuse_key in res['source_text']:
                    has_refuse_keys = True
                    break
            # 存在非法关键词，跳过
            if has_refuse_keys:
                continue

            # TODO 补充黑名单特殊关键字
            if '玻璃' in res["source_text"] and '不' not in res["source_text"]:
                continue

            if '玻璃擦' in res["source_text"]:
                continue

            if '窗' in res["source_text"] and '不' not in res["source_text"]:
                continue

            # 如果近200条消息有重复地址 则跳过
            if string_to_short_hash(res['work_addr'] + res['work_time']) in fix_msg_queue.get_queue():
                print(
                    f'重复的地址：{res["work_addr"]}--{res["work_time"]}--{string_to_short_hash(res["work_addr"] + res["work_time"])}')
                continue
            # 将地址存入固定长度的消息队列 fix_msg_queue

            print(
                f'未重复的地址：{res["work_addr"]}--{res["work_time"]}--{string_to_short_hash(res["work_addr"] + res["work_time"])}')
            fix_msg_queue.add(string_to_short_hash(res['work_addr'] + res['work_time']))

            dict_queue.put({'source_msg': source_msg, 'the_content': the_content, 'addr': res['work_addr'],
                            'work_time': res['work_time'],
                            'split_msg': res['source_text']})


# 无限循环从 exec_queue 队列中取字典，获取最终查询结果 last_res 然后把查询到的last_res 并行传入队列 msg_queue
def exec_msg_queue(driver, exec_queue, index_queue):
    """
    无限循环从 exec_queue 队列中取字典，获取最终查询结果 last_res
    然后把查询到的last_res 并行传入队列 msg_queue

    :param driver: 浏览器驱动
    :param exec_queue: 接收队列 字典队列
    :param msg_queue: 发送队列（待发送消息）
    :return:
    """
    while True:
        the_dict = exec_queue.get()
        the_addr = the_dict['addr']
        the_source_msg = the_dict['source_msg']
        split_msg = the_dict['split_msg']
        work_time = the_dict['work_time']
        # the_time 是送往京东查询的时间
        the_time = convert_time(work_time)
        # 获取经纬度
        location = search(driver, the_addr)

        # res：当天可排工期的列表
        res = search_res(location['lng'], location['lat'], the_time)
        res_text = ''
        if res:
            the_result = None
            # 拿到客户要求的当前时间段的查询结果the_result
            for item in res:
                if item['time'] == the_time[-5:]:
                    the_result = item['enabled']
                    break

            if the_result:
                res_text = '【当前时间可预约】'
            else:
                for dic in res:
                    if dic['enabled']:
                        res_text += f"【{dic['time']}】\n"
        else:
            # TODO 京东解析失败
            print(the_addr, '京东解析失败。')
            continue

        # 如果没有时间段是空闲的，则跳过，不处理这条消息
        if res_text == '':
            res_text = '【无可预约时间】'

        # 计算【消息来源】和【原始消息】
        all_msg = re.findall("content：(.+?)---", the_source_msg)[0]
        if '条]' in all_msg or '我]' in all_msg:
            msg_group = re.findall("user：(.+?)---", the_source_msg)[0]
            msg_autor = all_msg.split('：', 1)[0].split(']', 1)[-1].strip()
            msg_source = '【群】' + msg_group + '  ->  ' + msg_autor
        else:
            msg_source = '【个人】' + re.findall("user：(.+?)---", the_source_msg)[0]

        # 计算【消息耗时】
        the_time_receve = re.findall("time：(.+?)---", the_source_msg)[0]
        the_time_receve_datetime = datetime.strptime(the_time_receve, "%Y-%m-%d %H:%M:%S")
        time_delta = datetime.now() - the_time_receve_datetime
        time_delta_text = round(float(str(time_delta).rsplit(":", 1)[1]), 1)

        last_res = f'''
1.详细地址：【{the_addr}】

2.工作时间：{the_time}

3.消息来源：{msg_source}

4.查询结果：\n{res_text}

5.切割消息：【
{split_msg}
】

6.原始消息：【
{the_dict['the_content']}
】

7.本次消耗：【{time_delta_text}】
'''

        index_queue.put(last_res)


def inc_file_record(abs_filename: str):
    with file_lock:
        if os.path.exists(abs_filename):
            with open(abs_filename, mode='r', encoding='utf-8') as file:
                index = int(file.read()) + 1
        else:
            with open(abs_filename, mode='w', encoding='utf-8') as file:
                file.write('1')
                index = 1
        with open(abs_filename, mode='w', encoding='utf-8') as file:
            file.write(str(index))
    return index


# 线程函数：处理待发送消息队列 -> 加上序号
def msg_queue_do(msg_queue, access_token_list, chat_id_1, chat_id_2, chat_id_3):
    while True:
        message = msg_queue.get()
        now_time = datetime.now().strftime('%Y-%m-%d')
        current_dir = os.getcwd()
        if not os.path.isdir(os.path.join(current_dir, 'data')):
            os.mkdir('data')
        # 发送消息
        if '当前时间可预约' in message:
            bookable_file_name = f'可预约_{now_time}.txt'
            abs_bookable_file = os.path.join(
                current_dir, 'data', bookable_file_name)
            index = inc_file_record(abs_bookable_file)

            later_msg = f'今日序号【{str(index)}】\n\n{message}'
            send(access_token_list[0], later_msg, chat_id_1)

        elif '无可预约时间' in message:
            later_msg = f'京东未通过：\n\n{message}'
            send(access_token_list[0], later_msg, chat_id_3)

        else:  # 当前非空闲
            free_file_name = f'非空闲_{now_time}.txt'
            abs_free_file = os.path.join(current_dir, 'data', free_file_name)
            index = inc_file_record(abs_free_file)
            later_msg = f'今日序号【{str(index)}】\n\n{message}'
            send(access_token_list[0], later_msg, chat_id_2)


# 主程序
def go():
    # 全局记录：存储消息队列，用于对比。
    fix_msg_queue_total = FixedSizeQueue(800)
    # ——————————————————————————初始化飞书凭证——————————————————————————————————————
    # 全局存储access_token
    access_token_list = [None]
    # TODO 配置你的应用程序凭证
    app_id = 'cli_a60aa656b939100e'
    app_secret = 'sarxErZ9gpw2Au6xTVJ2tdEAfZ8sx1s4'
    access_token = get_access_token(app_id, app_secret)
    if not access_token:
        print('飞书凭证验证失败。')
        return
    access_token_list[0] = access_token
    # ——————————————————————————初始化飞书凭证——————————————————————————————————————
    # TODO 配置你的文档id

    psw = input('请输入密钥：')
    if psw.strip() not in get_document_content(access_token_list[0], 'TVnmdRnCJoZXgLxNue0ckXZGnjf').split('\n'):
        print('密钥错误或已过期！')
        return

    print('开始程序初始化 >>>')

    # ——————————————————————————持续刷新飞书凭证，创建飞书群——————————————————————————————————————
    print('配置飞书机器人 >>>')
    # 持续刷新飞书凭证
    p = threading.Thread(target=refresh_access_token, args=(app_id, app_secret, access_token_list))
    p.start()

    # 选择飞书群聊回传方式
    while True:
        x = input('请选择飞书群聊回传方式：（1.创建新的群聊 2.载入群聊）：')
        if x.strip() == '1':
            # 创建群
            chat_id_1 = create_group(access_token, '当前空闲')
            if not chat_id_1:
                return
            chat_id_2 = create_group(access_token, '当前非空闲')
            if not chat_id_2:
                return
            chat_id_3 = create_group(access_token, '未通过京东')
            if not chat_id_3:
                return
            break

        elif x.strip() == '2':
            try:
                with open('group_create_log.txt', mode='rt', encoding='utf-8') as file_object:
                    content = file_object.read()
                chat_id_1 = re.findall('当前空闲 chat_id ->(.+?)\n', content)[0]
                chat_id_2 = re.findall('当前非空闲 chat_id ->(.+?)\n', content)[0]
                chat_id_3 = re.findall('未通过京东 chat_id ->(.+?)\n', content)[0]
                break

            except:
                chat_id_1 = input('当前空闲 chat_id ->').strip()
                chat_id_2 = input('当前非空闲 chat_id ->').strip()
                chat_id_3 = input('未通过京东 chat_id ->').strip()
                break

        else:
            print('输入有误！')

    # 获取群分享链接
    share_link_1 = get_group_share_link(access_token, chat_id_1)
    if not share_link_1:
        return
    share_link_2 = get_group_share_link(access_token, chat_id_2)
    if not share_link_2:
        return
    share_link_3 = get_group_share_link(access_token, chat_id_3)
    if not share_link_3:
        return

    print('当前空闲 GROUP_LINK：')
    print(share_link_1)
    print('当前非空闲 GROUP_LINK：')
    print(share_link_2)
    print('未通过京东 GROUP_LINK：')
    print(share_link_3)

    with open('group_create_log.txt', mode='wt', encoding='utf-8') as file_object:
        file_object.write(f'当前空闲 chat_id ->{chat_id_1}\n')
        file_object.write(share_link_1)
        file_object.write('\n')
        file_object.write(f'当前非空闲 chat_id ->{chat_id_2}\n')
        file_object.write(share_link_2)
        file_object.write('\n')
        file_object.write(f'未通过京东 chat_id ->{chat_id_3}\n')
        file_object.write(share_link_3)

    x = input('加入飞书群聊后继续 Enter -> ')

    print('飞书配置完成 >>>')
    # ——————————————————————————持续刷新飞书凭证，创建飞书群——————————————————————————————————————

    savedStdout = sys.stdout
    print_log = open("printlog.log", "w", encoding='utf8')
    sys.stdout = print_log

    # ——————————————————————————配置selenium谷歌浏览器——————————————————————————————————————
    driver = launch_browser()

    if not driver:
        return
    # ——————————————————————————配置selenium谷歌浏览器——————————————————————————————————————

    # 创建一个从微信获取原生消息 存放的队列
    wait_for_exec_queue = queue.Queue()

    # 创建一个筛选后的字典队列
    dict_queue = queue.Queue()

    # 创建一个已经处理完待发送的 消息队列
    msg_queue = queue.Queue()

    # 创建一个固定长度为 200 的队列 用于排除重复消息
    fix_msg_queue = FixedSizeQueue(50)

    # 锁定微信窗口
    print('锁定微信窗口 >>>')
    wx = WindowControl(ClassName='WeChatMainWndForPC')

    # 切换到微信窗口
    print('切换微信窗口 >>>')
    wx.SwitchToThisWindow()

    print('调整微信窗口 >>>')
    # 查找微信窗口
    wechat_window = gw.getWindowsWithTitle('微信')[0]
    # 获取屏幕的宽度
    screen_width, _ = pyautogui.size()
    # 设置新的窗口左上角的 x 坐标，使其位于屏幕最右边，仅露出来50px
    new_left = screen_width - 200
    # 设置窗口新的位置和大小
    wechat_window.moveTo(new_left, 0)  # 将窗口移动到新的位置
    wechat_window.resizeTo(25, 66666666)  # 设置窗口新的大小

    # 关键词设置
    with open('key.txt', mode='rt', encoding='utf-8') as file:
        content = file.read()
    keys = [item.strip() for item in re.findall('keys = \[(.+?)]', content)[0].strip().split(',')]
    refuse_keys = [item.strip() for item in re.findall('refuse_keys = \[(.+?)]', content)[0].strip().split(',')]
    print('关键词设置完毕 >>>')

    # 过滤省级地址
    with open('location.txt', mode='rt', encoding='utf-8') as file:
        content = file.read()
    locations = [item.strip() for item in re.findall('locations = \[(.+?)]', content)[0].strip().split(',')]
    print('过滤地址设置完毕 >>>')

    print('UI初始化已完成,开始监控任务 >>>')

    # 开启线程：从 WX 获取消息 存入 wait_for_exec_queue
    print('开启线程 1/5 >>> ')
    p = threading.Thread(target=get_msg, args=(wx, fix_msg_queue_total, wait_for_exec_queue, psw))
    p.start()

    # 开启线程：从 wait_for_exec_queue 队列中取出消息，并调用  ——————————大模型——————————处理， 结果存入 dict_queue
    print('开启线程 2/5 >>> ')
    for i in range(5):
        p = threading.Thread(target=exec_source_msg,
                             args=(wait_for_exec_queue, dict_queue, keys, refuse_keys, locations, fix_msg_queue))

        p.start()

    # 开启线程：从 dict_queue 队列中取出字典信息，查询京东结果，并将结果存入msg_queue
    print('开启线程 3/5 >>> ')
    for i in range(5):
        p = threading.Thread(target=exec_msg_queue,
                             args=(driver, dict_queue, msg_queue))

        p.start()

    # 开启线程：从待发送消息队列 取消息，然后发送到飞书
    print('开启线程 4/5 >>> ')
    for i in range(1):
        p = threading.Thread(target=msg_queue_do,
                             args=(msg_queue, access_token_list, chat_id_1, chat_id_2, chat_id_3))
        p.start()

    print('线程加载完毕 开始工作 >>> ')


if __name__ == '__main__':
    go()
