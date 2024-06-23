import random
import string

def generate_random_string():
    # 生成随机字母和数字组成的序列
    random_chars = random.choices(string.ascii_letters + string.digits, k=4)
    # 随机选择一个字母作为字符串的开头
    start_char = random.choice(string.ascii_letters)
    # 将开头字母和随机字符序列连接起来
    random_string = start_char + ''.join(random_chars)
    return random_string


