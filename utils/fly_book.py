import json
import time
import requests


# 获取应用访问令牌，失败返回None
def get_access_token(app_id, app_secret):
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = {
        'app_id': app_id,
        'app_secret': app_secret
    }
    response = requests.post(url, json=data, headers=headers)
    access_token = response.json().get('tenant_access_token')
    try:
        return access_token
    except:
        print('获取应用访问令牌失败 >>>')
        return None


# 刷新飞书凭证
def refresh_access_token(app_id, app_secret, access_token_list):
    while True:
        time.sleep(60)
        access_token_list[0] = get_access_token(app_id, app_secret)


# 创建群，成功返回chat_id，失败返回None
def create_group(access_token, name='无主题'):
    url = 'https://open.feishu.cn/open-apis/im/v1/chats'
    headers = {
        'Authorization': f'Bearer {access_token}',  # your access token
        'Content-Type': 'application/json; charset=utf-8'
    }
    payload = json.dumps({
        "chat_type": "public",
        "name": name
    })

    response = requests.post(url, headers=headers, data=payload)
    content = response.content.decode('utf-8')
    try:
        return json.loads(content)['data']['chat_id']
    except:
        print('创建群失败 >>>')
        return None


# 获取群分享链接，成功返回链接，失败返回None
def get_group_share_link(access_token, chat_id):
    url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/link"
    payload = json.dumps({
        "validity_period": "permanently"
    })

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    content = response.content.decode('utf-8')
    try:
        return json.loads(content)['data']['share_link']
    except:
        print('获取群链接失败 >>>')
        return None


# 获取群列表 item为字典 {'chat_id': dict['chat_id'], 'name': dict['name']}
def get_group_list(access_token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=100"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        return [{'chat_id': dict['chat_id'], 'name': dict['name']} for dict in
                json.loads(response.content.decode('utf-8'))['data']['items']]
    else:
        return None


# 解散群，成功返回True，失败返回False
def close_group(access_token, chat_id):
    url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("DELETE", url, headers=headers)
    if response.status_code == 200:
        try:
            res = json.loads(response.content.decode('utf-8'))['msg']
        except:
            return False
        if res == 'success':
            return True
        return False
    else:
        return False


# 解散所有群聊
def empty_groups(access_token):
    res = get_group_list(access_token)
    print('群聊列表', res)
    for item in res:
        close_group(access_token, item['chat_id'])
        print('delete：', item['chat_id'])


# 发送消息，成功返回True，失败返回False
def send(access_token, msg, chat_id):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    msgContent = {
        "text": msg,
    }
    req = {
        "receive_id": f"{chat_id}",  # chat id
        "msg_type": "text",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': f'Bearer {access_token}',  # your access token
        'Content-Type': 'application/json; charset=utf-8'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    content = response.content.decode('utf-8')  # Print Response
    msg = json.loads(content)['msg']
    if msg == 'success':
        return True
    else:
        return False


# 创建文档，成功返回文档document_id，失败返回None            ---用于验证权限
def creaate_document(access_token):
    url = "https://open.feishu.cn/open-apis/docx/v1/documents"

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers)
    try:
        return json.loads(response.content)['data']['document']['document_id']
    except:
        return None


# 更新块的内容，成功返回True，失败返回False            ---用于验证权限
def update_piece(access_token, document_id, block_id, new_content):
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}"
    payload = json.dumps({
        "update_text_elements": {
            "elements": [
                {  # text_run代表更新文本
                    "text_run": {
                        "content": f"{new_content}"
                    }
                }
            ]
        }
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.request("PATCH", url, headers=headers, data=payload)
    try:
        if json.loads(response.content)['code'] == 0:
            return True
    except:
        return False


# 获取文档纯文本内容            ---用于验证权限
def get_document_content(access_token, document_id):
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)

    try:
        return json.loads(response.content)['data']['content'].strip()
    except:
        return None


if __name__ == '__main__':
    # 配置你的应用程序凭证
    app_id = 'cli_a6cb07f2a6f4d013'
    app_secret = 'Vi2dPXRLCRfrj0hppj40hfiZIGLRmdbh'
    access_token = get_access_token(app_id, app_secret)
    empty_groups(access_token)
