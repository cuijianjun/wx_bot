import time
import requests
import os
import sys
# import psutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.random_str import generate_random_string

import tempfile

temp_dir = tempfile.gettempdir()


# 打开谷歌无头浏览器
def launch_browser():
    print('正在模拟浏览器环境 >>> ')

    try:
        # 创建一个 Chrome 浏览器实例
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")  # 启用无痕模式
        # 本地 HTML 文件的绝对路径
        cwd_path = os.getcwd()
        driver_path = os.path.join(cwd_path, 'Chrome-bin', '127.0.6533.88','chromedriver.exe')
        chrome_path = os.path.join(cwd_path, 'Chrome-bin', 'chrome.exe')

        options.binary_location = chrome_path
            
        service = Service(driver_path)
        driver = webdriver.Chrome(options=options, service=service)
        FIRST_PATH = os.path.dirname(os.path.abspath(__file__))
        # print(2222,FIRST_PATH)
        html_file_path = os.path.join(os.path.dirname(FIRST_PATH), 'JS', 'html_.html')
        driver.get("file://" + html_file_path)
    except Exception as e:
        print('模拟浏览器环境失败 >>> ')
        print(e)
        return None,e,None,None

    print('浏览器环境搭建完毕 >>> ')

    return driver,None,driver_path,chrome_path
# 用来加入飞书的群
def fs_browser():
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")  # 启用无痕模式
        feishu_folder = os.path.join(temp_dir, 'feishu')
        options.add_argument(f"--user-data-dir={feishu_folder}") 
        chrome_path = os.path.join(os.getcwd(), 'Chrome', 'Application', 'chrome.exe')
        service = Service(chrome_path)
        driver = webdriver.Chrome(options=options, service=service)
    except Exception as e:
        print(e)
        return None
    return driver


# 搜索地址的经纬度
def search(driver, addr,city):
    id = generate_random_string()
    driver.execute_script(f"search('{addr}', '{id}','{city}');")

    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, f'#{id}')
            break
        except:
            time.sleep(0.5)

    lng = driver.execute_script(f'return document.querySelector("#{id}").getAttribute("lng");')
    lat = driver.execute_script(f'return document.querySelector("#{id}").getAttribute("lat");')
    driver.execute_script(f'document.querySelector("#{id}").remove();')
    return {'lng': lng, 'lat': lat}


if __name__ == '__main__':
    driver = launch_browser()

    list_of_addr = ['贵州省贵阳市云岩区书香门第B栋3单元', '蔡甸区江汉大学', '北京天安门', '北海市银滩']

    # 利用线程池加快查找速度
    import concurrent.futures

    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        # 提交任务给线程池，每个任务对应一个 msg
        futures = [executor.submit(search, driver, addr) for addr in list_of_addr]
        # 等待所有任务执行完毕
        concurrent.futures.wait(futures)
