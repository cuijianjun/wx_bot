from datetime import datetime, timedelta


# 自动转换成整点日期
def convert_time(input_time):
    dt = datetime.now()
    try:
        if len(input_time) == 10:
            input_time1 = input_time + f' {dt.hour + 1}:00'     # tmp
            print(f"{input_time}输入异常，已转换为：{input_time1}")
            input_time = input_time1
        elif len(input_time) == 5:
            input_time1 = f'{dt.date()} {input_time}'     # tmp
            print(f"{input_time}输入异常，已转换为：{input_time1}")
            input_time = input_time1
        elif len(input_time) != 16:
            print("输入时间格式不正确，请使用YYYY-MM-DD HH:MM格式, 实际输入：", input_time)
            # 返回第二天的这时候的时间
            new_dt = dt + timedelta(days=1)
            input_time = new_dt.strftime("%Y-%m-%d %H:%M")
        # 将输入时间字符串转换为datetime对象
        input_datetime = datetime.strptime(input_time, "%Y-%m-%d %H:%M")

        # 将小时和分钟调整到最近的半小时或整点
        if input_datetime.minute == 0:
            pass
        elif 0 < input_datetime.minute <= 30:
            input_datetime = input_datetime.replace(minute=30)
        else:
            if input_datetime.hour == 23 and input_datetime.minute > 30:
                # 如果是23:30以后，直接设置为00:00第二天
                input_datetime = input_datetime.replace(hour=0, minute=0) + timedelta(days=1)
            else:
                input_datetime = input_datetime.replace(hour=input_datetime.hour + 1, minute=0)

        # 返回格式化后的时间字符串
        return input_datetime.strftime("%Y-%m-%d %H:%M")
    except Exception as e:
        print("输入时间格式不正确，请使用YYYY-MM-DD HH:MM格式")
        print('输入时间格式不正确，原因：', e)
        return None


if __name__ == '__main__':
    the_time = convert_time('2024-05-14 00:01')
    print(the_time)
