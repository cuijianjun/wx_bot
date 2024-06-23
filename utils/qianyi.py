import random
import json
from http import HTTPStatus
import dashscope
from dashscope import Generation  # 建议dashscope SDK 的版本 >= 1.14.0

dashscope.api_key = 'sk-251ae7ea282b42018baf65e2571b9b5b'


def call_with_messages(ques):
    prompt = """
请根据我提供的文本，依次完成以下2步：
1、将文本按照"任务"合理分割成多个句子（只有一个任务的不用分割）。
2、从分割后的文本中分别提取出：工作时间（格式是：XX:XX。如果提取不到则返回"空"字。）、工作地点（自动精准到省市区加详细地址，没有区级或者没有详细地址则返回"空"字。）、原始文本。
然后返回给我结果。返回的结果必须严格遵守以下格式（请不要有任何多余的话）：
###工作时间：...；工作地点：...；原始文本：...；###
###工作时间：...；工作地点：...；原始文本：...；###
###工作时间：...；工作地点：...；原始文本：...；###
注意：
1.工作时间是从早上08:30到晚上20:00点，请自动校准。比如文本中说3点，就一定是15:00，而不是凌晨03:00！
2.工作时间如果是现在、尽快或者立即、立马、立刻等字眼，返回"现在"就可以。
3.分割出来的所有原始文本拼接起来必须等于我提供给你的文本！不能遗漏！

强调格式：每一段分割文本提取的结果以###开头和结尾，并且用换行符分隔。中间每一个要素用中文分号间隔。

下面是一个示例：
问：
2. 日常2小时，海淀，罗庄西里11号楼1306，自带工具，70 1 明天3点半 3小时做饭+保洁 房山 燕山 铜锅涮肉东侧  自带工具  100 3.立马去   日常4小时  香山南路89号1号院、 自带工具140
答：
###工作时间：空；工作地点：北京市海淀区罗庄西里11号楼1306；原始文本：2. 10:00   日常2小时，海淀，罗庄西里11号楼1306，自带工具，70；###
###工作时间：15:30；工作地点：北京房山区燕山铜锅涮肉东侧；原始文本：1 明天3点半 3小时做饭+保洁 房山 燕山 铜锅涮肉东侧  自带工具  100；###
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
            return None
    else:
        return False


if __name__ == '__main__':
    ques = '''
明早8点
上城区彭埠街道中海御道一区
2小时日常  到手70

明天早上9点
上城区四季青街道钱塘府
2小时日常  到手70

明早9点
钱塘区白杨街道金隅观澜时代瀚庭
深度3小时起  35一小时  1位保洁  带擦玻璃器

明天下午4点
萧山区新塘街道融望之城西区
2小时日常  到手70
'''
    answer = call_with_messages(ques)
    print(answer)
