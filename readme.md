1、环境配置：

    python 3.8环境下安装下列模块：
        jionlp selenium pyautogui uiautomation pygetwindow

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

3、配置文件说明：

    html_.html：用于启动selnium
    index：用于计数
    document_id：配置飞书
    key：配置关键词
    location：配置城市

4、 程序实现流程

    捕获微信消息 -> 解析地址、时间 -> 百度查询经纬度坐标 -> 京东查询结果 -> 返回到飞书（均基于队列实现）

5、打包

    通过pyinstaller打包之后将dist文件夹中的内容放至指定文件夹即可