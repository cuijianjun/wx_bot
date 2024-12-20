import json
import requests
import urllib.parse


def get_qq_xy(addr, city =None):
    # 腾讯地图API的URL
    url = "https://apis.map.qq.com/ws/geocoder/v1/"


    api_key = "JANBZ-KVQCQ-53G5G-4ZF5Z-UT3Q6-BZF3U"

    params = {
        "address": addr,
        "key": api_key
    }

    # 发送GET请求
    response = requests.get(url, params=params, verify=False)

    # 检查响应状态码
    if response.status_code == 200:
        # 解析JSON响应
        data = response.json()
        if data["status"] == 0:
            # 获取经纬度信息
            location = data["result"]["location"]
            latitude = location["lat"]
            longitude = location["lng"]
            return {
                'lng':longitude,
                'lat':latitude
            }
            print(f"经度: {longitude}, 纬度: {latitude}")
        else:
            print(f"请求失败: {data['message']}")
            return None
    else:
        print(f"HTTP请求失败: {response.status_code}") 
        return None
    
# 根据地点查询时间信息data
def get_jd_xy(addr, city =None):
    """
    根据地点查询时间信息
    :param lon: 经度
    :param lat: 纬度
    :return: 详细的时间信息表
    """
    request_dict = {
        "keyword": addr
    }
    if city:
        request_dict['region'] = city
    url_text = json.dumps(request_dict)

    encoded_url = urllib.parse.quote(url_text)


    url = f"https://api.m.jd.com/api?appid=cleaning&functionId=housekeeping_addressSuggestion&body={encoded_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0 Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://api.m.jd.com/api"  # 替换成你的源的地址
    }

    response = requests.post(url, headers=headers, verify=False)

    if response.status_code == 200:
        return response.json()['data'][0]
    else:
        print("Request failed with status code:", response.status_code)
        print(response.json())
        return None

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
        "serviceProjectItemId": 702,
        # "serviceAddressFull":addr,
        "newUser": True
    }
    
    # print('request_dict',request_dict)
    # {"serviceTime":"2","serviceTimeUnit":1,"serviceTemplateId":1,
    #  "serviceCityId":1601,"serviceCityName":"广州市",
    #  "serviceAddressId":6113903239,
    #  "serviceAddressFull":"广东广州市黄埔区长岭街道揽镜花园1栋2504",
    #  "serviceProvinceId":19,"serviceProvinceName":"广东",
    #  "serviceCountyId":50283,"serviceCountyName":"黄埔区",
    #  "serviceTownId":129162,"serviceTownName":"长岭街道",
    #  "lon":113.521141,"lat":23.212813,"serviceProjectItemId":702,"newUser":true}
    # 'lon': '116.39536180215137', 'lat': '40.08926890609032'
# appid: cleaning
# functionId: housekeeping_getServiceDateList
# body: {"serviceTime":"2","serviceTimeUnit":1,"serviceTemplateId":1,"serviceCityId":2800,"serviceCityName":"海淀区","serviceAddressId":8646624893,"serviceAddressFull":"北京海淀区学院路街道海淀区学院路街道逸成东苑14号楼1103","serviceProvinceId":1,"serviceProvinceName":"北京","serviceCountyId":55833,"serviceCountyName":"学院路街道","serviceTownId":0,"serviceTownName":null,"lon":116.347779,"lat":40.012682,"serviceProjectItemId":702,"newUser":true}
   
   
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

    response = requests.post(url, headers=headers, verify=False)
    print(response.json())
    if response.status_code == 200:
        return response.json()['data']
    else:
        print("Request failed with status code:", response.status_code)
        print(response.json())
        return None


# 根据地址和时间查询京东结果（是否可以下单）  return: True or False or None
def search_res(lon, lat, the_time=None):
    """
    查询京东当天的结果（当前时间到24点 之间）
    :param lon: 经度
    :param lat: 纬度
    :param the_time: 查询时间
    :return: True or False or None
    """
    res = []
    data = get_jd_msg(lon, lat)
    print(data)
    # 返回全天的空闲时间段
    if the_time:
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
    else:
        res = data
    return res


if __name__ == '__main__':
    # from datetime import datetime
    # from utils.convert_time import convert_time

    # the_time = convert_time(datetime.now().strftime('%Y-%m-%d %H:%M'))

    res = search_res('116.4133836971231', '39.910924547299565')
    print(res)
    # headers = {
    #     "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    #     "Content-Type": "application/json",
    #     "Origin": "https://api.m.jd.com/api"  # 替换成你的源的地址
    # }
    # url ='https://api.m.jd.com/api?appid=cleaning&functionId=housekeeping_getServiceDateList&body=%7B%22serviceTime%22%3A%222%22%2C%22serviceTimeUnit%22%3A1%2C%22serviceTemplateId%22%3A1%2C%22serviceCityId%22%3A2901%2C%22serviceCityName%22%3A%22%E6%98%8C%E5%B9%B3%E5%8C%BA%22%2C%22serviceAddressId%22%3A13316803117%2C%22serviceAddressFull%22%3A%22%E5%8C%97%E4%BA%AC%E6%98%8C%E5%B9%B3%E5%8C%BA%E5%9B%9E%E9%BE%99%E8%A7%82%E8%A1%97%E9%81%93%E6%96%B0%E9%BE%99%E5%9F%8E3%E6%9C%9F36D%E5%8F%B7%E6%A5%BC1402%22%2C%22serviceProvinceId%22%3A1%2C%22serviceProvinceName%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22serviceCountyId%22%3A55554%2C%22serviceCountyName%22%3A%22%E5%9B%9E%E9%BE%99%E8%A7%82%E8%A1%97%E9%81%93%22%2C%22serviceTownId%22%3A0%2C%22serviceTownName%22%3Anull%2C%22lon%22%3A116.332861%2C%22lat%22%3A40.066418%2C%22serviceProjectItemId%22%3A702%2C%22newUser%22%3Atrue%2C%22voucherBindType%22%3Anull%2C%22bindGiftFlag%22%3Anull%7D'
    # # 给定的 Cookie 字符串
    # cookie_str = """pt_key=AAJnEkggADD2KSBd_EFWScq7XyjRqiiQXhYSbu3laufSdzjZjxOkC_-IEZ3KriTPlFYkV-J430g; pt_pin=18838970230_p"""

    # # 指定要提取的 Cookie 字段
    # desired_fields = ['whwswswws']

    # # 将 Cookie 字符串转换为字典
    # cookies_dict = {}
    # for cookie in cookie_str.split(';'):
    #     key, value = cookie.strip().split('=', 1)
    #     cookies_dict[key] = value
   
    # print(cookies_dict)
    # response = requests.post(url, headers=headers, verify=False,cookies=cookies_dict)
    # # print(res)
    # # res = get_jd_xy("北京昌平区城北街道京科苑1号楼")
    # # lon":116.560078,"lat":39.907406,"  "lon":116.24839626220214,"lat":40.21110660237786 {'lng': 116.245746, 'lat': 40.208077}
    # # print(res['lat'],)
    # print(response.json())
