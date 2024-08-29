import requests

# 接口地址
url = "https://api.map.baidu.com/geocoding/v3"

# 此处填写你在控制台-应用管理-创建应用后获取的AK
ak = "gQsCAgCrWsuN99ggSIjGn5nO"

params = {
    "address":    "浙江杭州市下城区朝晖街道稻香园(南区)7幢3单元501室",
    "city":"杭州市",
    "output":    "json",
    "ak":       ak,
    "ret_coordtype":"GCJ02"

}
headers = {
    "Referer": "https://maplocation.sjfkai.com"  # Replace with your actual domain
}
response = requests.get(url=url, params=params, headers=headers)
if response:
    print(response.json())