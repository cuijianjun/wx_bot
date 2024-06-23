import time
import requests
import os
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.random_str import generate_random_string


# 打开谷歌无头浏览器
def launch_browser():
    print('正在模拟浏览器环境 >>> ')

    try:
        # 创建一个 Chrome 浏览器实例
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--incognito")  # 启用无痕模式

        # 本地 HTML 文件的绝对路径
        if getattr(sys, 'frozen', False):
            # 如果是打包成exe文件
            FIRST_PATH = os.path.dirname(sys.executable)
            service_path = os.path.join(os.path.dirname(FIRST_PATH), 'jingdong', 'chromedriver.exe')
            service = Service(service_path)
            driver = webdriver.Chrome(options=options, service=service)
            html_file_path = os.path.join(os.path.dirname(FIRST_PATH), 'jingdong', 'JS', 'html_.html')
        else:
            # 如果是直接运行Python脚本
            driver = webdriver.Chrome(options=options)
            FIRST_PATH = os.path.dirname(os.path.abspath(__file__))
            html_file_path = os.path.join(os.path.dirname(FIRST_PATH), 'JS', 'html_.html')

        # 使用 file:// 协议加载本地 HTML 文件
        driver.get("file://" + html_file_path)


    except Exception as e:
        print('模拟浏览器环境失败 >>> ')
        print(e)
        return None

    print('浏览器环境搭建完毕 >>> ')

    return driver


# 搜索地址的经纬度
def search(driver, addr):
    id = generate_random_string()

    driver.execute_script(f"search('{addr}', '{id}');")

    while True:
        try:
            driver.find_element(By.CSS_SELECTOR, f'#{id}')
            break
        except:
            time.sleep(0.5)

    lng = driver.execute_script(f'return document.querySelector("#{id}").getAttribute("lng");')
    lat = driver.execute_script(f'return document.querySelector("#{id}").getAttribute("lat");')
    driver.execute_script(f'document.querySelector("#{id}").remove();')
    # print(addr, {'lng': lng, 'lat': lat})
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
