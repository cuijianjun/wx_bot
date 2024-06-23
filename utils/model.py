import re
from datetime import datetime
import random
from http import HTTPStatus
import dashscope
from dashscope import Generation  # 建议dashscope SDK 的版本 >= 1.14.0

dashscope.api_key = 'sk-251ae7ea282b42018baf65e2571b9b5b'


def get_time(work_time, source_text):
    # 检测字段：现在/随便等
    if work_time == '现在' or '现在' in source_text or '几点都行' in source_text or '马上' in source_text or '立即' in source_text or '立刻' in source_text or '随便' in source_text or '随时' in source_text:
        return datetime.now().strftime('%Y-%m-%d %H:%M')


# 获取大模型回答
def call_with_messages(ques):
    prompt = f"""
请根据我提供的文本，依次完成以下2步：
1、将文本按照"任务"合理分割成多个句子（只有一个任务的不用分割）。
2、从分割后的文本中分别提取出：
（1）工作时间（格式是：年-月-日 时:分。如果提取不到则返回"空"字。今天是{datetime.now().strftime('%Y-%m-%d')}，根据上下文返回时间）
（2）工作地点（自动补充省市区加详细地址，没有详细地址则返回"空"字。）
（3）分割后的原始文本
完成以上两步之后返回给我结果。请严格遵守以下格式（请不要有任何多余的文字）：
###工作时间：...；工作地点：...；原始文本：...；###
###工作时间：...；工作地点：...；原始文本：...；###
###工作时间：...；工作地点：...；原始文本：...；###
注意：
1.工作时间是从早上08:30到晚上20:00点，请自动校准。比如文本中说3点，就一定是15:00，而不是凌晨03:00！
2.工作时间如果是现在、尽快、立即、立马、随便等字眼，则工作时间返回"现在"。
3.分割出来的所有原始文本拼接起来必须等于我提供给你的文本！不能遗漏！

分割出来的原始文本保留换行！
分割出来的原始文本保留换行！
分割出来的原始文本保留换行！

强调格式：
1.每一段分割文本提取的结果以###开头和结尾。
2.每段分割文本中间每一个要点结尾都是中文分号。
3.每一个提取出来的分割文本之间用换行符间隔。

示例：
问：
2. 日常2小时，海淀，罗庄西里11号楼1306，自带工具，70 1 明天3点半 3小时做饭+保洁 房山 燕山 铜锅涮肉东侧  自带工具  100 3.立马去   日常4小时  香山南路89号1号院、 自带工具140
答：
###工作时间：空；工作地点：北京市海淀区罗庄西里11号楼1306；原始文本：2. 10:00   日常2小时，海淀，罗庄西里11号楼1306，自带工具，70；###
###工作时间：x年-x月-x日 15:30；工作地点：北京市房山区燕山铜锅涮肉东侧；原始文本：1 明天3点半 3小时做饭+保洁 房山 燕山 铜锅涮肉东侧  自带工具  100；###
###工作时间：现在；工作地点：空；原始文本：3.立马去   日常4小时  香山南路89号1号院、 自带工具140；###

下面是我提供给你的文本，请按照上面的要求返回结果。
"""

    messages = [{'role': 'system', 'content': prompt},
                {'role': 'user', 'content': ques}]
    response = Generation.call(model="qwen-long",
                               messages=messages,
                               # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
                               seed=random.randint(1, 10000),
                               # 将输出设置为"message"格式
                               result_format='message')

    if response.status_code == HTTPStatus.OK:
        try:
            content = response['output']['choices'][0]['message']['content']
            content = content.replace(r'\n', '\n')
            return content
        except:
            print('大模型结果返回失败！')
            return None
    else:
        print('大模型结果返回失败！')
        return None


# 返回结果列表，列表元素为字典，包括work_time work_addr source_text
def get_res_list(the_answer):
    return_list = []
    res_list = re.findall('###.+?###', the_answer, re.DOTALL)
    # 循环提取到的任务
    for res in res_list:
        work_time_re = re.findall('###工作时间：(.+?)；', res)
        work_addr_re = re.findall('工作地点：(.+?)；', res)
        source_text_re = re.findall('原始文本：(.+?)；###', res, re.DOTALL)

        if work_time_re:
            work_time = work_time_re[0]
        else:
            print('从大模型结果中解析【工作时间】失败：', res)
            continue

        if work_addr_re:
            work_addr = work_addr_re[0]
        else:
            print('从大模型结果中解析【工作地点】失败：', res)
            continue

        if source_text_re:
            source_text = source_text_re[0]
        else:
            source_text_re = re.findall('原始文本：(.+?)###', res, re.DOTALL)
            if source_text_re:
                source_text = source_text_re[0]
            else:
                print('从大模型结果中解析【原始文本】失败：', res)
                continue

        # 处理时间为 文本型数据：'%Y-%m-%d %H:%M'
        if work_time == '现在' or '现在' in source_text or '几点都行' in source_text or '马上' in source_text or '立即' in source_text or '立刻' in source_text or '随便' in source_text or '随时' in source_text:
            work_time = datetime.now().strftime('%Y-%m-%d %H:%M')

        res_dict = {"work_time": work_time, "work_addr": work_addr, "source_text": source_text}
        print(res_dict)
        return_list.append(res_dict)

    return return_list


if __name__ == '__main__':
    ques = '''
明天9:00
2小时日常
70+5好评
东城区 西营房胡同9号院-4号楼

随便什么时候
2小时日常
70+5好评
东城区 西营房胡同9号院-4号楼
'''
    answer = call_with_messages(ques)
    if answer:
        res_list = get_res_list(answer)
        for item in res_list:
            print(item)
