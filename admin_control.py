from utils.fly_book import *


# 添加数据
def insert_data(access_token, document_id, data):
    # 输出文档原文本内容（纯文本）
    last_content = get_document_content(access_token, document_id)
    new_content = last_content + '\n' + data
    new_content = new_content.strip()

    if update_piece(access_token, document_id, document_id, new_content):
        print('数据添加成功')
        return True
    else:
        print('数据添加失败')
        return False


# 删除数据
def delete_data(access_token, document_id, data):
    # 输出文档原文本内容（纯文本）
    last_content = get_document_content(access_token, document_id)
    if data not in last_content.split('\n'):
        print('数据不存在')
        return False

    new_content = last_content.replace(data, '')
    new_content = new_content.strip()

    if update_piece(access_token, document_id, document_id, new_content):
        print('数据删除成功')
        return True
    else:
        print('数据删除失败')
        return False


# 查看当前文档内容
def print_current_document(access_token, document_id):
    print('当前文档内容：')
    print(get_document_content(access_token, document_id))


# 编辑内容
def edit(access_token, document_id):
    while True:
        command = input('输入命令（0返回） -> ')
        if command.strip() == '0':
            break
        elif 'insert ' in command.lower():
            data = command.split(' ', 1)[-1].strip()
            insert_data(access_token, document_id, data)
        elif 'delete ' in command.lower():
            data = command.split(' ', 1)[-1].strip()
            delete_data(access_token, document_id, data)
        else:
            print("命令有误")
            continue
        print_current_document(access_token, document_id)


# 测试密钥
def test(access_token, document_id):
    while True:
        psw = input('请输入密钥（0返回） -> ')
        if psw.strip() == '0':
            break
        if psw.strip() not in get_document_content(access_token, document_id).split('\n'):
            print('密钥错误或已过期！')
            continue
        print('密钥正确')


if __name__ == '__main__':
    # 配置你的应用程序凭证
    app_id = 'cli_a6cb07f2a6f4d013'
    app_secret = 'Vi2dPXRLCRfrj0hppj40hfiZIGLRmdbh'
    access_token = get_access_token(app_id, app_secret)

    # 配置你的文档id
    while True:
        chose = input('请选择document_id操作模式 （1自动，2创建，3填写）-> ')
        if chose.strip() == '1':
            with open('document_id.txt', mode='rt', encoding='utf-8') as file_object:
                document_id = file_object.read().strip()
            if document_id:
                break
            else:
                print('获取失败')

        elif chose.strip() == '2':
            # 创建文档
            document_id = creaate_document(access_token)
            if document_id:
                break
            else:
                print('创建失败')

        elif chose.strip() == '3':
            document_id = input('请输入document_id -> ').strip()
            if get_document_content(access_token, document_id) != None:
                break
            print('该document_id不存在')

        else:
            print('输入有误')

    print('绑定成功！document_id：', document_id)

    # 将 document_id在文件中刷新
    with open('document_id.txt', mode='wt', encoding='utf-8') as file_object:
        file_object.write(document_id)

    print('初始化完成 >>> ')
    # 开始操作
    print('【编辑】操作指令：')
    print('【插入】：insert 数据内容')
    print('【删除】：delete 数据内容')

    while True:
        chose = input('请输入功能（0结束，1编辑，2测试，3查看当前数据） -> ')
        if chose.strip() == '0':
            break
        elif chose.strip() == '1':
            edit(access_token, document_id)
        elif chose.strip() == '2':
            test(access_token, document_id)
        elif chose.strip() == '3':
            print_current_document(access_token, document_id)
