import json
import requests
import urllib.parse


# 根据地点查询时间信息data
def get_jd_msg(lon, lat):
    """
    根据地点查询时间信息
    :param lon: 经度
    :param lat: 纬度
    :return: 详细的时间信息表
    """
    request_dict = {
        "serviceTime": "2",  # 服务时长不可为空，固定
        "serviceTimeUnit": 1,  # 服务时间单位不可为空，固定
        "serviceTemplateId": 1,  # 服务模板id不可为空，固定
        "lon": lon,  # 变量
        "lat": lat,  # 变量
        "serviceProjectItemId": 111,
        "newUser": True
    }

    # 字典转化成json字符串
    url_text = json.dumps(request_dict)
    # json字符串转化成url编码
    encoded_url = urllib.parse.quote(url_text)
    # url编码拼接到post请求url 并发送请求
    url = f"https://api.m.jd.com/api?appid=cleaning&functionId=housekeeping_getServiceDateList&body={encoded_url}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://api.m.jd.com/api"  # 替换成你的源的地址
    }

    response = requests.post(url, headers=headers)

    if response.status_code == 200:
        # print("Response Successfully!")
        # print(response.json())
        return response.json()['data']
    else:
        print("Request failed with status code:", response.status_code)
        print(response.json())
        return None


# 根据地址和时间查询京东结果（是否可以下单）  return: True or False or None
def search_res(lon, lat, the_time):
    """
    查询京东当天的结果（当前时间到24点 之间）
    :param lon: 经度
    :param lat: 纬度
    :param the_time: 查询时间
    :return: True or False or None
    """
    res = []
    data = get_jd_msg(lon, lat)

    # 返回全天的空闲时间段
    for dic in data:

        try:
            # 对比到 年-月-日
            if dic['serviceDate'] == the_time[:10]:
                for dic2 in dic['timeStockStatusList']:
                    res.append({'time': dic2['startTime'], 'enabled': dic2['enabled']})
                break
        except Exception as e:
            # TODO dic['serviceDate'] 报错 'NoneType' object is not subscriptable
            # 问题是 the_time是 Nonetype
            break

    return res


if __name__ == '__main__':
    from datetime import datetime
    from utils.convert_time import convert_time

    the_time = convert_time(datetime.now().strftime('%Y-%m-%d %H:%M'))

    res = search_res('116.4133836971231', '39.910924547299565', convert_time('2024-06-29 12:21'))
    print(res)
