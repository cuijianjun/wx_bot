import requests

# 接口地址
url = "https://api.map.baidu.com/geocoding/v3"

# 此处填写你在控制台-应用管理-创建应用后获取的AK
ak = "VRfGHhpMKqJZnzPsGKO2SNti7wELtPVS"

params = {
    "address":    "北京市海淀区上地十街10号",
    "output":    "json",
    "ak":       ak,

}

response = requests.get(url=url, params=params)
if response:
    print(response.json())