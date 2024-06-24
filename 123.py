dic = {'bookStatus': 0, 'serviceDate': '2024-06-23', 'serviceDateDes': '周日',
       'timeStockStatusList': [{'enabled': False, 'isChecked': None, 'startTime': '08:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '08:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '09:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '09:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '10:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '10:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '11:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '11:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '12:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '12:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '13:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '13:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '14:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '14:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '15:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '15:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '16:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '16:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '17:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '17:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '18:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '18:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '19:00'},
                               {'enabled': False, 'isChecked': None, 'startTime': '19:30'},
                               {'enabled': False, 'isChecked': None, 'startTime': '20:00'}]}
res = []
try:
    # 对比到 年-月-日
    if dic['serviceDate'] == '2024-06-23':
        for dic2 in dic['timeStockStatusList']:
            res.append({'time': dic2['startTime'], 'enabled': dic2['enabled']})

except Exception as e:
    # TODO dic['serviceDate'] 报错 'NoneType' object is not subscriptable
    print('京东解析出错，dic返回值：', dic)
    print('京东解析出错原因：', e)

print(res)