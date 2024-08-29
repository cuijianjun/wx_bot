import hashlib


# def string_to_short_hash(input_string, length=27):
#     # 创建一个新的sha1 hash对象
#     hash_object = hashlib.sha1()
#     # 将输入的字符串编码为字节，然后更新hash对象
#     hash_object.update(input_string.encode('utf-8'))
#     # 获取16位的哈希值
#     hash_value = hash_object.hexdigest()[:16]
#     return hash_value
def string_to_short_hash(input_string, length=20):
    # 创建一个新的 SHA-256 hash 对象
    hash_object = hashlib.sha256()
    # 将输入的字符串编码为字节，然后更新 hash 对象
    hash_object.update(input_string.encode('utf-8'))
    # 获取20位的哈希值
    hash_value = hash_object.hexdigest()[:length]
    return hash_value

if __name__ == '__main__':
    original_string = "Hello,  World!"
    short_hash = string_to_short_hash(original_string)  # 截取前8位
    print(short_hash)
