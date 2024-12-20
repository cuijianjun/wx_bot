import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
import configparser
import os
import sys
import psutil
import queue
import random
import re
import json
from datetime import datetime, timedelta, date
import requests
from urllib.parse import urljoin
import hashlib
import winreg
import subprocess
import pyautogui
import pygetwindow as gw
from utils.deque import FixedSizeQueue
from uiautomation import WindowControl
from utils.convert_time import convert_time
from utils.fly_book import FeishuAPI
from utils.jd import search_res,get_jd_xy,get_qq_xy
from utils.model import call_with_messages,call_with_query, get_res_list,get_order_list
from utils.selenium_get_location import launch_browser, search
from utils.str_to_hash import string_to_short_hash
import logging
from collections import OrderedDict,deque

from logging.handlers import TimedRotatingFileHandler



class LRUCache:
    def __init__(self, max_size):
        self.cache = OrderedDict()
        self.max_size = max_size
    def get(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
            return True
        return False

    def put(self, key):
        if key in self.cache:
            self.cache.move_to_end(key)
        else:
            self.cache[key] = True
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def __contains__(self, key):
        return key in self.cache

    def __len__(self):
        return len(self.cache)

    def __str__(self):
        return str(self.cache)

    def __repr__(self):
        return repr(self.cache)



class HashQueue:
    def __init__(self, max_size):
        self.hash_set = set()
        self.queue = deque()
        self.max_size = max_size

    def add_hash(self, hash_value):
        if hash_value not in self.hash_set:
            if len(self.queue) >= self.max_size:
                oldest_hash = self.queue.popleft()
                self.hash_set.remove(oldest_hash)
            self.hash_set.add(hash_value)
            self.queue.append(hash_value)

    def __contains__(self, hash_value):
        return hash_value in self.hash_set

    def __len__(self):
        return len(self.queue)

    def __str__(self):
        return str(self.queue)

    def __repr__(self):
        return repr(self.queue)
    
# class ThreadManager:
#     def __init__(self, error_handler=None):
#         self.threads = []
#         self.pause_event = threading.Event()
#         self.pause_event.set() 
#         self.stop_event = threading.Event()
#         self.error_handler = error_handler  # 错误处理函数

#     def create_thread(self, target, args=()):
#         thread = threading.Thread(target=self._wrap_target, args=(target, args))
#         thread.start()
#         self.threads.append(thread)
#         return thread
#     def err_reset(self):
#         self.threads = []
#         self.pause_event = threading.Event()
#         self.pause_event.set()  
#         self.stop_event = threading.Event()
#     def _wrap_target(self, target, args):
#         while not self.stop_event.is_set():
#             self.pause_event.wait()  # 等待暂停事件被设置
#             target(*args)
#             # try:
#             #     target(*args)
#             # except Exception as e:
#             #     if self.error_handler:
#             #         print('错误',e)
#             #         time.sleep(2)
#             # time.sleep(0.1)  
#     def start_threads(self):
#         for thread in self.threads:
#             thread.start()

#     def pause_threads(self):
#         self.pause_event.clear()
#         self.status = 'pause'
#     def resume_threads(self):
#         self.pause_event.set()
#     def stop_threads(self):
#         self.stop_event.set()
#         self.resume_threads()  
#         for thread in self.threads:
#             thread.join() 
def is_time_between(check_time, start_time, end_time):

    check_time_dt = datetime.strptime(check_time, "%H:%M")
    start_time_dt = datetime.strptime(start_time, "%H:%M")
    end_time_dt = datetime.strptime(end_time, "%H:%M")
    
    if end_time_dt < start_time_dt:
        return check_time_dt >= start_time_dt or check_time_dt <= end_time_dt
    else:
        return start_time_dt <= check_time_dt <= end_time_dt
    
    
def parse_time(time_str):
    """将时间字符串解析为小时和分钟"""
    hours, minutes = map(int, time_str.split(':'))
    return (hours, minutes)

def is_within_time_range(start_time_str, check_time_str):
    max_time = (20, 0)  
    hours_to_add = 3

    start_time = parse_time(start_time_str)
    check_time = parse_time(check_time_str)

  
    if start_time[0] > max_time[0] or (start_time[0] == max_time[0] and start_time[1] > max_time[1]):
        return False


    end_time = add_hours(start_time, hours_to_add, max_time)

    
    check_minutes = check_time[0] * 60 + check_time[1]


    start_minutes = start_time[0] * 60 + start_time[1]
    end_minutes = end_time[0] * 60 + end_time[1]

    return start_minutes <= check_minutes <= end_minutes

def add_hours(start_time, hours_to_add, max_time):
  
    start_minutes = start_time[0] * 60 + start_time[1]
    max_minutes = max_time[0] * 60 + max_time[1]
    

    new_minutes = start_minutes + hours_to_add * 60
    
 
    if new_minutes > max_minutes:
        new_minutes = max_minutes
    
    new_hours = new_minutes // 60
    new_minutes = new_minutes % 60
    
    return (new_hours, new_minutes)
def contains_urgent_word(text):
    urgent_words = {"现在", "尽快", "立即", "立马", "马上", "立刻","随时"}
    return any(word in text for word in urgent_words)


def is_within_hour_range(time_point1, time_point2):
    """
    判断 time_point2 是否在 time_point1 的前一个小时或后一个小时的范围内。

    参数:
    time_point1 (str): 格式为 '%H:%M' 的时间字符串
    time_point2 (str): 格式为 '%H:%M' 的时间字符串

    返回:
    bool: 如果在范围内返回 True，否则返回 False
    """
    # 将时间字符串转换为 datetime 对象
    time_point1_dt = datetime.strptime(time_point1, '%H:%M')
    time_point2_dt = datetime.strptime(time_point2, '%H:%M')

    # 计算 time_point1 的前一个小时和后一个小时
    time_point1_before = time_point1_dt - timedelta(hours=1)
    time_point1_after = time_point1_dt + timedelta(hours=1)

    # 判断 time_point2 是否在 time_point1 的前一个小时或后一个小时的范围内
    return time_point1_before <= time_point2_dt <= time_point1_after

def extract_content(source_msg):
    return re.findall("content：(.+?)---", source_msg)[0]

def should_skip_content(the_content, keys):

    if '条]' in the_content or '我]' in the_content:
        
        the_content = the_content.split('：', 1)[-1]
    return all(key not in the_content for key in keys)

def should_skip_location(res, locations):
    return all(location not in res['work_addr'] for location in locations)

def should_skip_keys(res, keys):
    return all(key not in res['source_text'] for key in keys)

def has_refuse_keys(res, refuse_keys):
    return any(refuse_key in res['source_text'] for refuse_key in refuse_keys)

def log_refuse_keys(current_time, res, refuse_keys):
    with open("模型后进入黑名单.txt", "a", encoding='utf-8') as file:
        for refuse_key in refuse_keys:
            if refuse_key in res['source_text']:
                file.write(f"{current_time} 包含key:{refuse_key} 内容：{res['source_text']} \n")

def is_time_over(res):
    try:
        given_time = datetime.strptime(res['work_time'], "%Y-%m-%d %H:%M")
        one_week_later = datetime.now() + timedelta(weeks=1)
        return given_time > one_week_later
    except Exception:
        print('时间相关报错')
        return True
def is_app(res):
    return '【APP接单】' in res['work_notes'] or '【不可做】' in res['work_notes'] 
# or '【不可做】' in res['work_notes'] 
def is_glass_cleaning(res):
    bo_list = ['擦玻璃', '擦室内玻璃', '双面擦玻璃','擦窗户','擦窗']
    negative_words = ['不需', '不需要', '不用', '无需']
    negative_combinations = [neg + bo for neg in negative_words for bo in bo_list]
    if any(comb in res['work_notes'] for comb in negative_combinations):
        return False
    return (any(keyword in res['work_notes'] for keyword in ['【双面擦窗】', '含擦玻璃', '【含双面玻璃】', '【擦玻璃】', '【擦窗户】', '【擦窗】']) or
            any(bo in res['work_notes'] for bo in bo_list)) and any(char in res['source_text'] for char in '玻璃')
           

def is_work_uniform(res):
    return '【工服签到】' in res['work_notes'] 

class TaskManager:
    def __init__(self, log_file_path,error_file_path, app_id, app_secret,threadCount=20, runfn=None, errorfn=None):
        self.file_lock = threading.Lock()
        self.api_ver_order = ""
        # self.thread_manager = ThreadManager(error_handler=self.handle_error)
        
        self.pause_event = threading.Event()
        self.pause_event.set() 
        self.stop_event = threading.Event()
        
        self.ensure_file_exists(log_file_path)
        self.ensure_file_exists(error_file_path)
        self.logger = self.setup_logger(log_file_path,error_file_path)
        self.app_id = app_id
        self.app_secret = app_secret
        self.runfn = runfn
        self.errorfn = errorfn
        self.keys = []
        self.refuse_keys = [] 
        self.locations = []
        self.user = dict()
        self.user_id = None
        self.chat_id_1 = None
        self.status = 'init'
        self.feishuAPI = None
        self.threadCount = threadCount
        self.lock = threading.Lock()
        # 微信消息过滤重复消息的队列
        # self.wx_tasks = LRUCache(max_size=1000) 
        # 模型处理过已发送飞书的订单队列
        # 微信获取到的消息队列
        # self.wait_for_exec_queue = queue.LifoQueue()
        self.wait_for_exec_queue = queue.Queue()
        # 模型处理后丢给京东的队列
        self.dict_queue = queue.Queue()
        # 京东处理后丢给飞书发消息的队列
        self.msg_queue = queue.Queue()
        # 查询订单的队列
        self.query_queue = queue.Queue()
        # 订单结果的队列
        self.result_queue = queue.Queue()
        _keys = self.load_keywords("key.json")
        self.keys = _keys['keys']
        self.refuse_keys = _keys['refuse_keys']
        self.hash_queue = HashQueue(max_size=1000)
        self.fs_tasks = HashQueue(max_size=500)
        self.driver_path = None
        self.chrome_path = None
        self.driver = None
        self.fs_tasks_lock = threading.Lock()
    def setChat_id(self,id_1,id_2,id_3):
        self.chat_id_1 = id_1
        self.chat_id_2 = id_2
        self.chat_id_3 = id_3
    def setup_logger(self, log_file_path,error_file_path):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        run_log_handler = TimedRotatingFileHandler(log_file_path, when='D', interval=1, backupCount=7, encoding='utf-8')
        run_log_handler.setLevel(logging.INFO)
        run_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        error_log_handler = logging.FileHandler(error_file_path, encoding='utf-8')
        error_log_handler.setLevel(logging.ERROR)
        error_log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(run_log_handler)
        logger.addHandler(error_log_handler)
        return logger
    
    
    def load_keywords(self,file_path):
        """
        从 JSON 文件中加载 keywords 数据。
        :param file_path: JSON 文件的路径
        :return: 包含 keys 和 refuse_keys 的字典
        """
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            return data
        else:
            return {"keys": [], "refuse_keys": []}
    def clear_group(self,chat_id):
        if self.feishuAPI:
            self.feishuAPI.close_group( chat_id)
    def ensure_file_exists(self,file_path):

        dir_name = os.path.dirname(file_path)
        
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
        
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')
    def log(self, message):
        self.logger.info(message)
        if self.runfn and 'run_info' in message:
            self.runfn(message)

    def error_log(self, message, exc_info=None):
        self.logger.error(message, exc_info=exc_info)
        # self.pause()  # 发生错误时暂停任务
        time.sleep(1)
        # self.resume()
        # self.pause()

    def handle_error(self, message, exc_info=None):
        self.error_log(message, exc_info)
        if self.errorfn:
            self.status = 'error'
            self.errorfn(f'{message}{exc_info}')
    def empty_groups(self):
        return self.feishuAPI.empty_groups()
    def order_push(self,message):
        self.query_queue.put(message)
    def order_inquiries(self):
        while True:
            e = threading.Event()
            e.wait(random.randint(100, 300) / 1000)
            source_msg = self.query_queue.get()
            
            try:
                self.log(f"进入模型 {source_msg}")
                answer = call_with_query(source_msg)
                self.log(f"进模型完成解析 {answer}")
                if not answer:
                    self.result_queue.put({"res":'【模型处理失败，稍后重试】','answer':''})
                    continue
                res_list = get_order_list(answer)
                res = None  
                for res in res_list:
                    if not any(location in res['work_addr'] for location in self.locations):
                        self.log(f"{res['work_addr']} 非法省份")
                        continue
                if res is None: 
                    self.result_queue.put({"res":'【暂无匹配项】','answer':answer})
                    continue
                the_addr = res['work_addr']
                work_life = res['work_life']
                the_time = convert_time(res['work_time'])
                the_city = res['work_city']
                answer = re.sub(r'预约时间：\d{4}-\d{2}-\d{2} \d{2}:\d{2}', f'预约时间：{the_time}', answer)
                # location = get_qq_xy(the_addr,the_city)
                # self.log(f"获取位置 {location}")
                # # print('location',location)
                # if location is None:
                #     self.result_queue.put({"res":'【暂无匹配项】','answer':answer})
                #     continue
                # res = search_res(location['lng'], location['lat'], the_time)
                # print('res',res)
                # self.log(f"获取时间列表 {res}")
                res_text = False
                # enableds = []
                # if res:
                #     the_result = False
                #     for item in res:

                #         t = item['time']
                #         tt = the_time[-5:]
                #         if t == tt:
                #             the_result = item['enabled']
                #             if item['enabled']:
                #                 enableds.append(f'【{t}】*')
                #         if item['enabled']:
                #             enableds.append(f'【{t}】')
                #     if the_result:
                #         res_text = '【当前时间可预约】'
                #         enableds.insert(0, '【当前时间可预约】')
                        
                #     if res_text == '':
                #         res_text = '【无可预约时间】'
                #     else:
                #         res_text  =  '\n'.join(enableds)
                    # the_result = next((item['enabled'] for item in res if item['time'] == the_time[-5:]), None)
                    # if the_result:
                    #     res_text = '【当前时间可预约】'
                    # else:
                    #     res_text = ''.join(f"【{dic['time']}】\n" for dic in res if dic['enabled'])
                # else:
                #     self.log(f"{the_addr} 京东解析失败。")

                # if not res_text:
                #     res_text = '【无可预约时间】'
                    
                    
                
                self.result_queue.put({"res":res_text,'answer':answer})
                continue
            except Exception as e:
                self.error_log(f"处理大模型回答失败: {e}", exc_info=traceback.format_exc())
                self.result_queue.put({"res":'【模型处理失败，稍后重试】','answer':''})
                continue
    def run_order_inquiries(self, message):
        result_queue = queue.Queue()
        thread = threading.Thread(target=self.order_inquiries, args=(message, result_queue))
        thread.start()
        result = result_queue.get()
        if result is None:
            result = '【无可预约时间】'
        return result
 
    # 获取微信的安装路径
    def get_wechat_install_path(self):
        paths = [
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\WeChat",  # 64位系统上的32位应用程序
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\WeChat",  # 32位系统上的32位应用程序
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\WeChat"  # 64位系统上的64位应用程序
        ]

        for path in paths:
            try:
                # 打开注册表项
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                # 读取安装路径
                install_path = winreg.QueryValueEx(key, "InstallLocation")[0]
                winreg.CloseKey(key)
                return install_path
            except FileNotFoundError:
                continue
            except PermissionError:
                print(f"权限不足，无法访问注册表路径: {path}")
                continue
        return None
    def open_wechat(self):
        try:
            wechat_path = self.get_wechat_install_path()
            wechat_path = os.path.join(wechat_path, 'WeChat.exe')
            subprocess.Popen(wechat_path)
        except FileNotFoundError:
            print("未找到微信的可执行文件")
        except Exception as e:
            print(f"打开微信时发生错误: {e}")
    def test_key(self,key):

        try:
            if not self.feishuAPI:
                self.feishuAPI = FeishuAPI(self.app_id, self.app_secret,self.logger)
        except Exception as e:
            self.handle_error(f"初始化飞书凭证失败: {e}", exc_info=traceback.format_exc())
            return False
        users = self.feishuAPI.get_users()

        for user in users:
            name = user["name"]
            mobile = user["mobile"]
            open_id = user["open_id"]
            union_id = user["union_id"]
            user_id = user["user_id"]
            if mobile.endswith(key) and len(key)>3:
                self.user_id = user_id
                self.user = dict(name=name,mobile=mobile,open_id=open_id,union_id=union_id,user_id=user_id)
                self.psw = key
                return True
        else:
            return False
    def create_fs_group_link(self):

        try:
            # 获取当前时间
            now = datetime.now()

            # 获取当前时间的月和日
            month = now.month
            day = now.day
            _name = self.user['name']
            name1 = f'杭州群-{_name} {month}-{day}'
            
            name2 = f'非杭州（当天）群-{_name} {month}-{day}'
            
            name3 = f'非杭州（以后）群-{_name} {month}-{day}'
            self.chat_id_1 = self.feishuAPI.create_group(self.user_id,name1)
            
            self.chat_id_2 = self.feishuAPI.create_group(self.user_id,name2)
    
            self.chat_id_3 = self.feishuAPI.create_group(self.user_id,name3)
            # share_link_1 = get_group_share_link(self.access_token, self.chat_id_1)
       
            # share_link_2 = get_group_share_link(self.access_token, self.chat_id_2)
      
            # share_link_3 = get_group_share_link(self.access_token, self.chat_id_3)

            return [
                dict(id = self.chat_id_1,name=name1,user_id = self.user_id),
                dict(id = self.chat_id_2,name=name2,user_id = self.user_id),
                dict(id = self.chat_id_3,name=name3,user_id = self.user_id)
            ]
        except Exception as e:
            self.handle_error(f"创建飞书群聊失败: {e}", exc_info=traceback.format_exc())
            return []

    # def get_msg(self, wx, psw):
    #     while not self.thread_manager.stop_event.is_set():
    #         self.thread_manager.pause_event.wait()  # 等待暂停事件被设置
    #         # e = threading.Event()
    #         # e.wait(random.randint(100, 300) / 1000)
    #         try:
    #             ListControl_conmunicate = wx.ListControl(Name='会话')
    #         except Exception as e:
    #             self.handle_error(f"刷新微信窗口中的群聊列表失败: {e}", exc_info=traceback.format_exc())
    #             continue
    #         for msg in ListControl_conmunicate.GetChildren():
    #             # self.msg_execute(msg, psw)
    #             self.thread_manager.create_thread(target=self.msg_execute, args=(msg, psw))
    def get_msg(self,wx, psw):
        while not self.stop_event.is_set():
            self.pause_event.wait()
            e = threading.Event()
            e.wait(random.randint(100, 300) / 1000)
            # 刷新微信窗口中的群聊列表
            msg_list = []
            try:
                ListControl_conmunicate = wx.ListControl(Name='会话')
                msg_list = ListControl_conmunicate.GetChildren()
            except:
                continue
            for msg in msg_list:
                p = threading.Thread(target=self.msg_execute, args=(msg,psw))
                p.start()
    # def on_join_group(self,open_id,chat_id):
    #     try:
    #         self.feishuAPI.set_chat_members(chat_id,open_id)
    #         return True
    #     except Exception as e:
    #         self.error_log(f"加入群聊失败: {e}", exc_info=traceback.format_exc())
    #         return False

    def kill_process_by_path(self,exe_path):
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                # 检查进程的路径是否匹配
                if proc.info['exe'] == exe_path:
                    proc.terminate()  # 发送终止信号
                    proc.wait()  # 等待进程终止
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                # 处理可能发生的异常
                pass
    
    def is_orderable(self, user_id: str, msg_hash: str) -> bool:
        if self.api_ver_order == "":
            config = configparser.ConfigParser()
            config.read('config.ini', encoding='utf-8')
            self.api_ver_order = config.get('config', 'api_ver_order')

        url = urljoin(self.api_ver_order, "/api/verOrder")
        try:
            req = requests.post(url, params={"user_id": user_id, "message_hash": msg_hash})
            if req.status_code == 200:
                if req.json().get('code') == 0:
                    return True
        except Exception as e:
            self.handle_error(f"请求 verOrder api 失败: {e}", exc_info=traceback.format_exc())
        return False

    def msg_execute(self, msg, psw):
        try:
            if not self.stop_event.is_set():
                self.pause_event.wait()  # 等待暂停事件被设置

                if len(list(msg.GetFirstChildControl().GetChildren())) == 1:
                    return
                content = msg.GetFirstChildControl().GetChildren()[1].GetLastChildControl().GetFirstChildControl().Name
        
                if not content:
                    return
                if '条]' in content or '我]' in content:
                    the_content = content.split('：', 1)[-1]
                else:
                    the_content = content
                    return
                task_hash = string_to_short_hash(the_content)
    
                if task_hash in self.hash_queue:
                    return 
                self.hash_queue.add_hash(task_hash)

                user = msg.GetFirstChildControl().GetChildren()[1].GetFirstChildControl().GetFirstChildControl().Name
                
                next_msg = 'time：' + datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S") + '---' + 'user：' + user + '---' + 'content：' + content + '---'
        #    if '条]' in all_msg or '我]' in all_msg:
        #             msg_group = re.findall("user：(.+?)---", the_source_msg)[0]
        #             msg_autor = all_msg.split('：', 1)[0].split(']', 1)[-1].strip()
        #             msg_source = '【群】' + msg_group + '  ->  ' + msg_autor
                with open("总消息.txt", "a", encoding='utf-8') as file:
                    file.write(f"时间 ：{datetime.now()}  {next_msg}\n")
                # if "杭州" in user:
                self.wait_for_exec_queue.put(next_msg)

        except Exception as e:
            self.handle_error(f"微信状态异常: {e}", exc_info=traceback.format_exc())

    def exec_source_msg(self, keys, refuse_keys, locations):
        while not self.stop_event.is_set():
            self.pause_event.wait()  # 等待暂停事件被设置
            source_msg = self.wait_for_exec_queue.get()
            the_content = re.findall("content：(.+?)---", source_msg)[0]
            try:
                if should_skip_content(the_content, keys):
                    continue
    
                split_lines = re.split('[\ufeff\n]', the_content)
                if len(split_lines) > 1:
                    the_content = '\n'.join(split_lines)
        
                answer = call_with_messages(the_content)
                if not answer:
                    continue

                res_list = get_res_list(answer)
                for res in res_list:
                    self.log(f"{res['work_time']} {res['work_notes']} {res['work_addr']} {res['source_text']}")
                    # 地址
                    # if should_skip_location(res, locations):
                    #     self.log(f"不符合 {res['source_text']}")
                    #     print('不符合',res)
                    #     continue

                    if should_skip_keys(res, keys):
                        print('不在白名单',res)
                        self.log(f"不在白名单 {res['source_text']}")
                        continue

                    if has_refuse_keys(res, refuse_keys):
                        self.log(f"黑名单 {res['source_text']}")           
                        continue
                    if is_app(res):
                        print('是APP',res)
                        self.log(f"是APP {res['source_text']}")
                        continue                
                    if is_time_over(res):
                        print('超时')
                        self.log(f"超时 {res['source_text']}")
                        continue
                    if is_glass_cleaning(res):
                        self.log(f"擦玻璃 {res['source_text']}")
                        print('擦玻璃', res)
                        continue

                    if is_work_uniform(res):
                        self.log(f"工服 {res['source_text']}")
                        print('工服', res)
                        continue

                    task_hash = string_to_short_hash(res['work_addr'].strip() + res['work_time'].strip())
        
                    if task_hash in self.fs_tasks:
                            print('存在', res)
                            self.log(f"存在 {res['source_text']}")
                            continue

                    self.fs_tasks.add_hash(task_hash)

                    self.log(f"进入京东处理队列的 {res['source_text']}")
                    self.dict_queue.put({
                                'source_msg': source_msg,
                                'the_content': the_content,
                                'addr': res['work_addr'],
                                'work_timem': res['work_timem'],
                                'work_city': res['work_city'],
                                'work_time': res['work_time'],
                                'work_notes': res['work_notes'],
                                'split_msg': res['source_text']
                            })
            except Exception as e: 
                self.error_log(f"处理大模型回答失败: {e}", exc_info=traceback.format_exc())
    def exec_msg_queue(self):
        while not self.stop_event.is_set():
            self.log("exec_msg_queue: 进入京东处理队列。")
            self.pause_event.wait()  # 等待暂停事件被设置
            the_dict = self.dict_queue.get()
            self.log("exec_msg_queue: 获取到the_dict的值")
            the_addr = the_dict['addr']
            the_source_msg = the_dict['source_msg']
            split_msg = the_dict['split_msg']
            work_time = the_dict['work_time']

            the_time = convert_time(work_time)

            try:
                all_msg = re.findall("content：(.+?)---", the_source_msg)[0]
                if '条]' in all_msg or '我]' in all_msg:
                    msg_group = re.findall("user：(.+?)---", the_source_msg)[0]
                    msg_autor = all_msg.split('：', 1)[0].split(']', 1)[-1].strip()
                    msg_source = '【群】' + msg_group + '  ->  ' + msg_autor
                else:
                    msg_source = '【个人】' + re.findall("user：(.+?)---", the_source_msg)[0]

                the_time_receve = re.findall("time：(.+?)---", the_source_msg)[0]
                the_time_receve_datetime = datetime.strptime(the_time_receve, "%Y-%m-%d %H:%M:%S")
                time_delta = datetime.now() - the_time_receve_datetime
                time_delta_text = round(float(str(time_delta).rsplit(":", 1)[1]), 1)
     
                last_res = f'''
1.详细地址：【{the_addr}】

2.工作时间：{the_time}

3.消息来源：{msg_source}

4.切割消息：【
{split_msg}
】

5.原始消息：【
{the_dict['the_content']}
】

7.本次消耗：【{time_delta_text}】
'''
                self.log(f"进入飞书消息队列  {split_msg}")
                input_datetime = datetime.strptime(the_time, "%Y-%m-%d %H:%M")
                today_date = date.today()
                first_8_chars = the_addr[:8]
                if "杭州" in first_8_chars:
                    last_res += '【****杭州****】'
                elif input_datetime.date() == today_date:
                    last_res += '【****非杭州(当天)****】'
                else:
                    last_res += '【****非杭州(以后)****】'
                self.msg_queue.put(last_res)
            except Exception as e:
                self.error_log(f"处理京东查询结果失败: {e}", exc_info=traceback.format_exc())
                time.sleep(2)

    # def inc_file_record(self, abs_filename: str):
    #     print(111,abs_filename)
    #     with self.file_lock:
    #         if os.path.exists(abs_filename):
    #             with open(abs_filename, mode='r', encoding='utf-8') as file:
    #                 index = int(file.read()) + 1
    #         else:
    #             with open(abs_filename, mode='w', encoding='utf-8') as file:
    #                 file.write('1')
    #                 index = 1
    #         with open(abs_filename, mode='w', encoding='utf-8') as file:
    #             file.write(str(index))
    #     return index
    def inc_file_record(self, abs_filename: str):
        with self.file_lock:
            if os.path.exists(abs_filename):
                with open(abs_filename, mode='r+', encoding='utf-8') as file:
                    file_content = file.read()
                    if file_content:
                        index = int(file_content) + 1
                    else:
                        index = 1
                    file.seek(0)
                    file.write(str(index))
                    file.truncate()
            else:
                with open(abs_filename, mode='w', encoding='utf-8') as file:
                    index = 1
                    file.write(str(index))
        return index
    def msg_queue_do(self, chat_id_1,chat_id_2,chat_id_3):
        while not self.stop_event.is_set():
            self.pause_event.wait()  # 等待暂停事件被设置
            message = self.msg_queue.get()
            now_time = datetime.now().strftime('%Y-%m-%d')
            
            current_dir = os.getcwd()
            if not os.path.isdir(os.path.join(current_dir, 'data')):
                os.mkdir('data')
            try:
                if '【****杭州****】' in message:
                    message = message.replace('【****杭州****】', '')
                    bookable_file_name = f'杭州_{now_time}.txt'
                    abs_bookable_file = os.path.join(
                        current_dir, 'data', bookable_file_name)
                    index = self.inc_file_record(abs_bookable_file)

                    later_msg = f'今日序号【{str(index)}】\n\n{message}'
                    self.log(f'run_info: 杭州 {later_msg}')
                    time.sleep(0.2)
                    self.feishuAPI.send(later_msg, chat_id_1)
                elif '【****非杭州(当天)****】' in message:
                    message = message.replace('【****非杭州(当天)****】', '')
                    bookable_file_name = f'非杭州(当天)_{now_time}.txt'
                    abs_bookable_file = os.path.join(
                        current_dir, 'data', bookable_file_name)
                    index = self.inc_file_record(abs_bookable_file)

                    later_msg = f'今日序号【{str(index)}】\n\n{message}'
                    self.log(f'run_info: 非杭州(当天) {later_msg}')
                    time.sleep(0.2)
                    self.feishuAPI.send(later_msg, chat_id_2)  
                elif '【****非杭州(以后)****】' in message:
                    message = message.replace('【****非杭州(以后)****】', '')
                    bookable_file_name = f'非杭州(以后)_{now_time}.txt'
                    abs_bookable_file = os.path.join(
                        current_dir, 'data', bookable_file_name)
                    index = self.inc_file_record(abs_bookable_file)

                    later_msg = f'今日序号【{str(index)}】\n\n{message}'
                    self.log(f'run_info: 非杭州(以后) {later_msg}')
                    time.sleep(0.2)
                    self.feishuAPI.send(later_msg, chat_id_3)                   
            except Exception as e:
                self.error_log(f"发送消息失败: {e}", exc_info=traceback.format_exc())
    def process_messages(self):
        with ThreadPoolExecutor(max_workers=self.threadCount) as executor:
            while not self.stop_event.is_set():
                self.pause_event.wait()
                if not self.wait_for_exec_queue.empty():
                    source_msg = self.wait_for_exec_queue.get()
                    executor.submit(self.exec_source_msg, source_msg)
    def run(self):
            # self.err_reset()
            self.log('run_info:配置飞书机器人 >>>')
            # try:
            #     driver, err,driver_path,chrome_path = launch_browser()
            #     self.driver = driver
            #     self.driver_path = driver_path
            #     self.chrome_path = chrome_path
            #     if err:
            #         self.handle_error(f"配置selenium谷歌浏览器失败", exc_info=err)
            #         return
            # except Exception as e:
            #     self.handle_error(f"配置selenium谷歌浏览器失败: {e}", exc_info=traceback.format_exc())
            #     return

            # wait_for_exec_queue = queue.Queue()
     
            # fix_msg_queue = FixedSizeQueue(50)
            self.open_wechat()
            time.sleep(1)
            self.log('run_info:锁定微信窗口 >>>')
            try:
                wx = WindowControl(ClassName='WeChatMainWndForPC')
            except Exception as e:
                self.handle_error(f"锁定微信窗口失败: {e}", exc_info=traceback.format_exc())
                return

            self.log('run_info:切换微信窗口 >>>')
            try:
                wx.SwitchToThisWindow()
            except Exception as e:
                self.handle_error(f"切换微信窗口失败: {e}", exc_info=traceback.format_exc())
                return

            self.log('run_info:调整微信窗口 >>>')
            try:
                wechat_window = gw.getWindowsWithTitle('微信')[0]
                screen_width, _ = pyautogui.size()
                new_left = screen_width - 200
                wechat_window.moveTo(new_left, 0)
                wechat_window.resizeTo(25, 66666666)
            except Exception as e:
                self.handle_error(f"调整微信窗口失败: {e}", exc_info=traceback.format_exc())
                return

            # try:
            #     with open('key.txt', mode='rt', encoding='utf-8') as file:
            #         content = file.read()
            #     self.keys = [item.strip() for item in re.findall(r'keys = \[(.+?)]', content)[0].strip().split(',')]
            #     self.refuse_keys = [item.strip() for item in re.findall(r'refuse_keys = \[(.+?)]', content)[0].strip().split(',')]
            #     self.log('run_info:关键词设置完毕 >>>')
            # except Exception as e:
            #     self.handle_error(f"关键词设置失败: {e}", exc_info=traceback.format_exc())
            #     return

            try:
                with open('location.txt', mode='rt', encoding='utf-8') as file:
                    content = file.read()
                self.locations = [item.strip() for item in re.findall(r'locations = \[(.+?)]', content)[0].strip().split(',')]
                self.log('run_info:过滤地址设置完毕 >>>')
            except Exception as e:
                self.handle_error(f"过滤省级地址设置失败: {e}", exc_info=traceback.format_exc())
                return

            self.log('run_info:UI初始化已完成,开始监控任务 >>>')

            
            p = threading.Thread(target=self.order_inquiries, args=())
            p.start()
            self.log('run_info:开启线程 1/5 >>> ')
            p = threading.Thread(target=self.get_msg, args=(wx, self.psw))
            p.start()
            self.log('run_info:开启线程 2/5 >>> ')
            for i in range(self.threadCount):
                p = threading.Thread(target=self.exec_source_msg, args=(self.keys, self.refuse_keys, self.locations))
                p.start()
            # with ThreadPoolExecutor(max_workers=self.threadCount) as executor:
            #     while not self.stop_event.is_set():
            #         source_msg = self.wait_for_exec_queue.get()
            #         executor.submit(self.exec_source_msg, self.keys, self.refuse_keys, self.locations)
            # task_thread = threading.Thread(target=self.process_messages)
            # task_thread.start()

            self.log('run_info:开启线程 3/5 >>> ')
            for i in range(5):
                p = threading.Thread(target=self.exec_msg_queue, args=())
                p.start()
            self.log('run_info:开启线程 4/5 >>> ')
            for i in range(1):
                p = threading.Thread(target=self.msg_queue_do, args=(self.chat_id_1,self.chat_id_2,self.chat_id_3))
                p.start()
            # self.thread_manager.start_threads() 
            self.status = 'start'
            self.log('run_info:线程加载完毕 开始工作 >>> ') 
    def go(self):

        if self.pause_event.is_set() and self.status != 'start':

            self.run()
        else:

            self.resume()

    def pause(self):
        
        self.pause_event.clear()
        self.status = 'pause'

    def resume(self):
        self.pause_event.set()

    def stop(self):
        self.stop_event.set()
    def destroy(self):
        if self.driver:
            self.driver.quit()
            if self.driver_path:
                self.kill_process_by_path(self.driver_path)
            if self.chrome_path:
                self.kill_process_by_path(self.chrome_path)
        os._exit(0)   
# 示例使用
if __name__ == "__main__":
    pass
