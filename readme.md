1、环境配置：

    python 3.8环境下安装下列模块：
        jionlp selenium pyautogui uiautomation pygetwindow nuitka

2、py说明：

    baidu_get_location：用于从百度地图接口获取经纬度坐标。应用于selenium_get_location.py
    convert_time：将时间转换为半点或整点
    deque：自定义了一个固定长度队列
    fly_book：飞书api功能复现
    jd：用于到京东查询结果
    model：大语言模型的集成实现
    qianyi：千亿通问的接口调用指南
    random_str：用于生成随机的字符串。应用于selenium_get_location.py
    selenium_get_location：通过selenium调用百度api查询经纬度的实现
    str_to_hash：用于将字符串转换成哈希值
    admin_control：用于后台控制密钥
    main：主流程函数


3、打包
    先执行清空缓存
    py -m comtypes.clear_cache
    打包命令
    nuitka --onefile  --include-data-dir=JS=JS --include-data-dir=data=data --include-data-file=key.json=key.json --include-data-file=location.txt=location.txt  --enable-plugin=tk-inter --include-package=uiautomation  --include-package=comtypes --windows-disable-console --nofollow-imports --clang main.py
