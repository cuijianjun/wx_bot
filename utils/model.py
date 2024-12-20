import re
import calendar
from datetime import datetime,timedelta
import random
from http import HTTPStatus
import requests
import json
DASHSCOPE_API_KEY = 'sk-251ae7ea282b42018baf65e2571b9b5b'
# 设置请求 URL
url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

# 设置请求头
headers = {
    "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
    "Content-Type": "application/json"
}
# import dashscope
# from dashscope import Generation  # 建议dashscope SDK 的版本 >= 1.14.0

# dashscope.api_key = 'sk-251ae7ea282b42018baf65e2571b9b5b'

# from openai import OpenAI

# client = OpenAI(api_key="sk-251ae7ea282b42018baf65e2571b9b5b", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")

def parse_time(time_str):
    # 定义正则表达式模式
    pattern_full = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'
    pattern_short = r'^\d{2}:\d{2}$'

    # 使用正则表达式判断时间字符串的格式
    if re.match(pattern_full, time_str):
        datetime_obj = datetime.strptime(time_str, '%Y-%m-%d %H:%M')
        return datetime_obj
    elif re.match(pattern_short, time_str):
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        current_date = datetime.now().date()
        datetime_obj = datetime.combine(current_date, time_obj)
        return datetime_obj
    else:
        raise ValueError("时间字符串格式不正确")
def extract_weekdays(text):
    # 定义一个正则表达式来匹配表示周几的词汇
    weekday_pattern = r'(周[一二三四五六日]|星期[一二三四五六日])'
    
    # 使用findall方法查找所有匹配的周几词汇
    weekdays = re.findall(weekday_pattern, text)
    
    return weekdays




def get_weekday_number(weekday_str):
    # 将周几的字符串转换为对应的数字，其中周一为1，周日为7
    weekday_map = {
        '周一': 1, '星期一': 1,
        '周二': 2, '星期二': 2,
        '周三': 3, '星期三': 3,
        '周四': 4, '星期四': 4,
        '周五': 5, '星期五': 5,
        '周六': 6, '星期六': 6,
        '周日': 7, '星期日': 7,
    }
    return weekday_map.get(weekday_str)

def get_date_for_weekday(weekday_str):
    # 获取今天的日期
    today = datetime.now()

    # 获取今天的星期数（0表示周一，6表示周日）
    today_weekday = today.weekday()

    # 根据传入的周几字符串获取对应的数字
    target_weekday = get_weekday_number(weekday_str)

    # 如果没有找到对应的周几，则抛出异常
    if target_weekday is None:
        raise ValueError(f"无法识别的周几描述: {weekday_str}")

    # 计算目标日期与今天之间的天数差
    days_until_target = (target_weekday - today_weekday - 1) % 7

    # 返回目标日期
    return today + timedelta(days=days_until_target)


def get_time(work_time, source_text):
    # 检测字段：现在/随便等
    if work_time == '现在' or '现在' in source_text or '都行' in source_text or '马上' in source_text or '立即' in source_text or '立刻' in source_text or '随便' in source_text or '随时' in source_text:
        return datetime.now().strftime('%Y-%m-%d %H:%M')
def get_week():
    # import datetime

    # 获取当前日期
    today = datetime.now()

    # 获取今天是星期几（0是星期一，6是星期日）
    weekday = today.weekday()

    # 将星期几转换为字符串
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    weekday_str = weekdays[weekday]
    month = today.month
    year = today.year
    # 使用 calendar.monthrange 获取本月有多少天
    _, num_days = calendar.monthrange(year, month)
    return weekday_str,num_days
weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
weekday_str,num_days = get_week()

today = datetime.now()

tomorrow = today + timedelta(days=1)
tomorrow_str = tomorrow.strftime("%Y-%m-%d")
tomorrowweekday = tomorrow.weekday()
tomorrowweekday = weekdays[tomorrowweekday]
day_after_tomorrow = today + timedelta(days=2)
day_after_tomorrow_str = day_after_tomorrow.strftime("%Y-%m-%d")
# qlen = 0
# finlem = 0
# error = 0
def timeStr():
    now = datetime.now()
    weekdays_zh = ["周一，星期一", "周二，星期二", "周三，星期三", "周四，星期四", "周五，星期五", "周六，星期六", "周日，星期日"]
    nowstr = datetime.now().strftime('%Y-%m-%d %H:%M')
    tinfo = [f'现在时间是：{nowstr}']

    for i in range(7): 
        day = now + timedelta(days=i)
        date_str = day.strftime("%Y-%m-%d")
        weekday_index = day.weekday()  
        weekday_zh = weekdays_zh[weekday_index]

        t  =  f'{date_str}:({weekday_zh})'
        if i == 0:
            t  =  f'{date_str}:(今天，{weekday_zh})'
        elif i == 1:
            t  =  f'{date_str}:(明天，{weekday_zh})'
        elif i == 2:
            t  =  f'{date_str}:(后天，{weekday_zh})'
        tinfo.append(t)
    return '\n'.join(tinfo)
#     工作时间：
# 提取并格式化为“年-月-日 时:分”；
# 对于模糊时间（如“今天”、“明天”），根据当前日期解析并格式化时间为08:30；
# 将具体时间（如“08:00”或“10:00”）基于当前日期进行转换，并格式化；
# 将“八点”或“8点”转换为08:00，“八点半”或“8点半”转换为08:30；
# 检查错别字或干扰项，确保时间准确；
# 如无法直接提取时间，返回“空”；
# 获取大模型回答  - 长期工任务 【不可做】
def call_with_messages(ques):
    # global qlen,finlem,error
    prompt = f"""
你是一个优秀的数据分析师，负责高效精确地执行接下来的信息抽取任务：

1.**信息提取**：
   - **工作时间**：当前时间是：{datetime.now().strftime('%Y-%m-%d %H:%M')}，明天时间是：{tomorrow_str}， 后天是：{day_after_tomorrow_str}。
                  1.基于每个任务的信息，精确识别任务发生的具体时间。
                  2.根据以下规则结合当前时间提取工作时间：
                    模糊时间（如“今天”）默认为当天07:00,“下午”默认为当天13:30；
                    时间表述简化为标准格式（例：“八点”→08:00“ ， 八点半”→08:30 ，九点半”→09:30，九点”→09:00等）。
                    处理含糊时间指示（如“上午”）默认为当前日期；
                    “现在”表示立即执行的任务，工作时间应返回当前的时间。
                    排除时间描述中的干扰成分（如：“1. 13:00”，“天 下午 1：30”），确保时间的准确性。
                  3.最终以“年-月-日 时:分”的格式输出。
   - **工作地点**：提取并自动补全为详细地址，包括省、市、区等。如果无法提取详细地址，返回“空”字。
   - **所在城市**：工作地点所在的城市，根据**工作地点**提取出所在的城市，如果无法提取返回“空”字。
   - **备注信息**: 从原始文本中提取备注信息，包括额外的要求或注意事项。注意：需要擦玻璃和工服签到,或需要穿工作服的明确说明“【擦玻璃】”，“【工服签到】”，如何没有说明或者说不用擦玻璃和不用穿工作服的情况去掉关于玻璃和工作服的字眼或使用“【】”代替。仅限于日常保洁任务，以下任务标记为【不可做】：
                 - 需要擦玻璃的任务 【不可做】 
                 - 需要穿工作服的任务 【不可做】
                 - 需用特定软件（如“58阿姨端”、“58app”）打卡的任务 【不可做】
                
                
   - **时间描述**：分割过后的一个单独的任务的完整时间描述。
   - **原始文本**：保留原始文本中的换行符和所有内容。

**结果输出格式**：
完整的分割每个任务，提取结果单独展示，并严格按照以下格式返回：
###工作时间：...；时间描述：...；工作地点：...；所在城市：...；备注信息：...；原始文本：...；###
**注意事项**：
- 准确分析每个任务是否需要擦玻璃或穿工服，是否需要特定APP软件('app',"58",'58APP','58阿姨端'等)接单。并将结果按照要求写入备注信息中。
- 先分割任务在进行时间提取，确保每个任务的日期不会相互影响。
- 保证每一段分割文本提取的结果以###开头和结尾
- 保证分割后文本的顺序与原始文本一致，文本拼接后等同于原始文本。
- 所有任务要素的提取结果以中文分号“；”结尾。
**检验纠正**：
- 认真比对每个任务【工作时间】中提取的日期，跟【时间描述】中的日期是否一致。如果不一致及时修改正确。
把用户提供给你的文本，请按照上面的要求返回结果。
"""
    prompt = f"""
你是一个优秀的数据分析师，你能根据用户给定的信息精准的完成以下信息提取任务：
1、将文本按照"任务"合理分割成多个句子（只有一个任务的不用分割）。
2、从分割后的文任务中分别提取出：
（1）工作时间（格式是：年-月-日 时:分。如果提取不到则返回"空"字。今天是{datetime.now().strftime('%Y-%m-%d %H:%M')}，注意根据上下文补全成年-月-日 时:分的格式。认真分析时间描述精准的提取时间（例：“八点”→08:00“ ， 八点半”→08:30 ，九点半”→09:30，九点”→09:00等））。
（2）工作地点（提取并自动补全为详细地址，包括省、市、区等。如果无法提取详细地址，返回“空”字。）
（3）备注信息（从原始文本中提取备注信息，包括额外的要求或注意事项。注意：需要擦玻璃和工服签到,或需要穿工作服的明确说明“【擦玻璃】”，“【工服签到】”，如何没有说明或者说不用擦玻璃和不用穿工作服的情况去掉关于玻璃和工作服的字眼或使用“【】”代替。）
（4）时间描述（结合上下文和当前任务提取出完整的开始工作时间的描述。）
（5）所在城市（工作地点所在的城市，根据工作地点提取出所在的城市，如果无法提取返回“空”字。）
（6）每个任务分割后完整的原始文本
（7）严谨校验【工作时间】与【时间描述】的日期一致性，必要时作出调整，严格按照【当前时间】合理准确的推测时间。
完成以上两步之后返回给我结果。请严格遵守以下格式（请不要有任何多余的文字）：
###工作时间：...；时间描述：...；工作地点：...；所在城市：...；备注信息：...；原始文本：...；###
注意：
1.请根据任务描述准确的提取时间。并根据上下文补全成（年-月-日 时:分）的格式。
2.如果没有指定具体的时间从早上08:00到晚上20:00点，自动校准。
3.注意中文时间描述和具体时间的转换。如：八点半，8点半指的是8:00,九点指的是9:00。
4.工作时间如果是现在、尽快、立即、立马、随便等字眼，则工作时间返回当前的时间。
5.分割出来的所有原始文本拼接起来必须等于我提供给你的文本！不能遗漏！
6.（保姆，每月发工资，要求会做饭，月嫂，护理，双休，单休，带孩子）的任务直接在备注标注【不可做】
认真阅读任务，务必准确的提取出准确的时间！
7.一条任务的原始文本务必是完整的不要遗漏。
分割出来的原始文本保留换行！

强调格式：
1.每一段分割文本提取的结果以###开头和结尾。
2.每段分割文本中间每一个要点结尾都是中文分号。
3.每一个提取出来的分割文本之间用换行符间隔。

请根据要求精准的完成用户的任务。"""
    pattern = r'隔天.*?结账'
    ques = re.sub(pattern, '', ques)
    pattern = re.compile(r'(\[(\d+)条\]\s*(.+?)\s*：|\[有人@我\]\s*(.+?)\s*：)')
    match = pattern.search(ques)

    if match:
        start, end = match.span()
        if start == 0:
            ques = pattern.sub('', ques)
    messages = [
        {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': ques}]
    # response = Generation.call(model="qwen-long",
    #                            messages=messages,
    #                            temperature=0.0,
    #                            # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
    #                            seed=random.randint(1, 10000),
    #                            # 将输出设置为"message"格式
    #                            result_format='message')
    
    data = {
        "model": "qwen-long",
        "temperature":0.0,
        "messages": messages
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == HTTPStatus.OK:
        try:

            # content = response['output']['choices'][0]['message']['content']
            content = response.json()['choices'][0]['message']['content']
            # print(prompt,'\n',ques,'\n',content)
            content = content.replace(r'\n', '\n')
            # print(prompt,'\n',content)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # finlem = finlem+1
            # with open("outlen.txt", "w",encoding='utf-8') as file:
            #     file.write(f'''
            #             进入模型数量：{qlen}，
            #             已完成数量：{finlem}，
            #             执行中数量：{qlen-finlem-error},
            #             执行失败数量：{error}
            #             ''')
            with open("outques.txt", "a",encoding='utf-8') as file:
                file.write(f"{current_time} 【问题】：\n{ques} ,【答案】：\n{content}\n")
            return content
        except:
            print('大模型结果返回失败！')
            # error = error+1
            # with open("outlen.txt", "w",encoding='utf-8') as file:
            #     file.write(f'''
            #             进入模型数量：{qlen}，
            #             已完成数量：{finlem}，
            #             执行中数量：{qlen-finlem-error},
            #             执行失败数量：{error}
            #        ''')
            return None
    else:
        print('大模型结果返回失败！')
        # error = error+1
        # with open("outlen.txt", "w",encoding='utf-8') as file:
        #     file.write(f'''
        #             进入模型数量：{qlen}，
        #             已完成数量：{finlem}，
        #             执行中数量：{qlen-finlem-error},
        #             执行失败数量：{error}
        #             ''')
        return None


# 获取大模型回答  {datetime.now().strftime('%Y-%m-%d')}
def call_with_query(ques):
    prompt = f'''
你是一个优秀的数据分析师，你能根据用户给定的信息精准的完成以下信息提取任务：
1、将文本按照"任务"合理分割成多个句子（只有一个任务的不用分割）。
2、从分割后的文任务中分别提取出：
（1）预约时间（格式是：年-月-日 时:分。如果提取不到则返回"空"字。今天是{datetime.now().strftime('%Y-%m-%d %H:%M')}，认真分析时间描述精准的提取时间（例：“八点”→08:00“ ， 八点半”→08:30 ，九点半”→09:30，九点”→09:00等））。）并按照（年-月-日 时:分）格式输出。
（2）预约地址（提取并自动补全为详细地址，包括省、市、区等。如果无法提取详细地址，返回“空”字。）
（3）客户姓名（任务的联系人名称一般是汉字,如果没提取到有效信息，则默认是“老板”）
（4）客户电话（客户的联系方式，一般手机号是11位的数字。确保提取准确。）
（5）时间描述（结合上下文和当前任务提取出完整的开始工作时间的描述。）
（6）所在城市（工作地点所在的城市，根据工作地点提取出所在的城市，如果无法提取返回“空”字。）
（7）持续时间（工作的持续时间和工作类型，如果是日常2小时，就提取为“日常2小时”，如深度4小时，就提取成“深度4小时”，默认类型是“日常”）
**结果输出格式**：
完整的分割每个任务，提取结果单独展示，并严格按照以下格式返回：
###客户姓名：...；客户电话：...；预约时间：...；时间描述：...；持续时间：...；预约地址：...；所在城市：...；###
**注意事项**：
- 注意根据时间描述把时间补充完整，并按照（年-月-日 时:分）格式输出。
- 先分割任务在进行时间提取，确保每个任务的日期不会相互影响。
- 保证每一段分割文本提取的结果以###开头和结尾
- 保证分割后文本的顺序与原始文本一致，文本拼接后等同于原始文本。
- 所有任务要素的提取结果以中文分号“；”结尾。
''' 
    pattern = r'隔天.*?结账'
    ques = re.sub(pattern, '', ques)
    pattern = re.compile(r'(\[(\d+)条\]\s*(.+?)\s*：|\[有人@我\]\s*(.+?)\s*：)')
    match = pattern.search(ques)

    if match:
        start, end = match.span()
        if start == 0:
            ques = pattern.sub('', ques)
    messages = [
        {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': ques}]
    data = {
        "model": "qwen-long",
        "temperature":0.0,
        "messages": messages
    }

    # 发送 POST 请求
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    if response.status_code == HTTPStatus.OK:
        try:
            # content = response['output']['choices'][0]['message']['content']
            content = response.json()['choices'][0]['message']['content']
            content = content.replace(r'\n', '\n')
            # print(1111,prompt,'\n',content)
            return content
        except:
            print('大模型结果返回失败！')
            return None
    else:
        print('大模型结果返回失败！')
        return None
# 返回结果列表，列表元素为字典，包括work_time work_addr source_text

def get_order_list(the_answer):
    return_list = []
    res_list = re.findall('###.+?###', the_answer, re.DOTALL)
    # 循环提取到的任务
    for res in res_list:
        work_time_re = re.findall('预约时间：(.+?)；', res)
        work_addr_re = re.findall('预约地址：(.+?)；', res)
        work_city_re = re.findall('所在城市：(.+?)；', res)
        work_timem_re = re.findall('时间描述：(.+?)；', res)
        work_life_re = re.findall('持续时间：(.+?)；', res)
        # print(work_timem_re)
        if work_timem_re:
            work_timem = work_timem_re[0]
            # print(work_timem)
        if work_life_re:
            work_life = work_life_re[0]
        if work_time_re:
            work_time = work_time_re[0]
            # TODO BUG修复
   
            if work_time == '空':
   
                # print('从大模型结果中解析【工作时间】失败：', res)
                continue
            elif work_time:
                                # 获取今天的日期
                print(work_time)
                
                full_datetime_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$'
                time_only_pattern = r'^\d{2}:\d{2}$'
                
                if re.match(full_datetime_pattern, work_time):
                    datetime_obj = datetime.strptime(work_time, '%Y-%m-%d %H:%M')
                    hm = datetime_obj.time().strftime('%H:%M')
                # 检查字符串是否匹配时间格式
                elif re.match(time_only_pattern, work_time):
                    hm = datetime.strptime(work_time, '%H:%M').time()
                
                today = datetime.now().date()

                tomorrow = today + timedelta(days=1)

                day_after_tomorrow = today + timedelta(days=2)
                pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}')
                match = pattern.search(work_timem)
                weekdays = extract_weekdays(work_timem)
           
                if match:
                    work_timem = match.group()
             
                elif '今天' in work_timem or '今日' in work_timem:
                    
                    work_time = f'{today} {hm}'
           
                elif '明天' in work_timem or '明日' in work_timem:
                    work_time = f'{tomorrow} {hm}'
         
                elif '后天' in work_timem:
                    work_time = f'{day_after_tomorrow} {hm}'

                elif weekdays:
                    
                    weekday = weekdays[0]
  
                    date = get_date_for_weekday(weekday)

                    dateStr = date.strftime('%Y-%m-%d')
                    
                    original_datetime = datetime.strptime(work_time, "%Y-%m-%d %H:%M")

                    original_time = original_datetime.time()
  
                    if original_time != dateStr:
                        
                        new_date = datetime.strptime(dateStr, "%Y-%m-%d").date()

                        new_datetime = datetime.combine(new_date, original_time)
                        
                        work_time = new_datetime.strftime("%Y-%m-%d %H:%M")
                              
        else:
            # print('从大模型结果中解析【工作时间】失败：', res)
            continue

        if work_addr_re:
            work_addr = work_addr_re[0]
        else:
            # print('从大模型结果中解析【工作地点】失败：', res)
            continue
        if work_city_re:
            work_city = work_city_re[0]
            if work_city == '空':
                work_city = '北京市'
        res_dict = {"work_life":work_life,"work_time": work_time, "work_addr": work_addr,"work_city":work_city}
 
        return_list.append(res_dict)

    return return_list

def get_res_list(the_answer):
    return_list = []
    res_list = re.findall('###.+?###', the_answer, re.DOTALL)
 
    for res in res_list:
        try:
            work_time_re = re.findall('###工作时间：(.+?)；', res)
            
            work_timem_re = re.findall('时间描述：(.+?)；', res)
            
            work_addr_re = re.findall('工作地点：(.+?)；', res)
            
            work_notes_re = re.findall(r"备注信息：(.*?)\；原始文本：", res)
            
            work_city_re = re.findall('所在城市：(.+?)；', res)
    
            source_text_re = re.findall('原始文本：(.+?)；###', res, re.DOTALL)
        
            if work_timem_re:
                work_timem = work_timem_re[0]

            if work_time_re:
                work_time = work_time_re[0]
                # TODO BUG修复
    
                if work_time == '空':
    
                    # print('从大模型结果中解析【工作时间】失败：', res)
                    continue
                elif work_time:
                    # 获取今天的日期            
                    datetime_obj = parse_time(work_time)

                    today = datetime.now().date()

                    tomorrow = today + timedelta(days=1)

                    day_after_tomorrow = today + timedelta(days=2)
                    pattern = re.compile(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}')
                    match = pattern.search(work_timem)
                    weekdays = extract_weekdays(work_timem)

                    if match:
                        work_time = match.group()
                    elif '今天' in work_timem or '今日' in work_timem:
                        _timeStr = datetime_obj.time().strftime('%H:%M')
                        work_time = f'{today} {_timeStr}'
            
                    elif '明天' in work_timem or '明日' in work_timem:
                        _timeStr = datetime_obj.time().strftime('%H:%M')
                        work_time = f'{tomorrow} {_timeStr}'
            
                    elif '后天' in work_timem:
                        _timeStr = datetime_obj.time().strftime('%H:%M')
                        work_time = f'{day_after_tomorrow} {_timeStr}'
                    elif weekdays:
                        weekday = weekdays[0]
    
                        date = get_date_for_weekday(weekday)
    
                        dateStr = date.strftime('%Y-%m-%d')
                        
                        original_datetime = datetime.strptime(work_time, "%Y-%m-%d %H:%M")

                        original_time = original_datetime.time()

                        if original_time != dateStr:
                
                            new_date = datetime.strptime(dateStr, "%Y-%m-%d").date()

                            new_datetime = datetime.combine(new_date, original_time)
        
                            work_time = new_datetime.strftime("%Y-%m-%d %H:%M")            
            else:
                # print('从大模型结果中解析【工作时间】失败：', res)
                continue
            if work_addr_re:
                work_addr = work_addr_re[0]
            else:
                # print('从大模型结果中解析【工作地点】失败：', res)
                continue
            if work_notes_re:
                work_notes = work_notes_re[0]
            if source_text_re:
                source_text = source_text_re[0]
            if work_city_re:
                work_city = work_city_re[0]
                if work_city == '空':
                    work_city = '北京市'
            if source_text_re:
                source_text = source_text_re[0]
            else:
                source_text_re = re.findall('原始文本：(.+?)###', res, re.DOTALL)
                if source_text_re:
                    source_text = source_text_re[0]
                else:
                    # print('从大模型结果中解析【原始文本】失败：', res)
                    continue

            res_dict = {"work_time": work_time, "work_addr": work_addr, "source_text": source_text,"work_notes":work_notes,"work_city":work_city,"work_timem":work_timem}

            return_list.append(res_dict)
        except Exception as e:
            
            print(f"解析时间错误: {e}")   
            continue     
    return return_list


if __name__ == '__main__':
    pass
    # weekdays = extract_weekdays('下午3点到')
    # print(f"提取到的表示周的值: {weekdays}")
    # date = get_date_for_weekday(weekdays[0])
    # print(f"{weekdays[0]} 对应的日期是: {date.strftime('%Y-%m-%d')}")