import json

import requests

class FeishuAPI:
    def __init__(self, app_id, app_secret,logger):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.open_id = None
        self.owner_id = '7f1638gc'
        self.logger = logger
    def get_access_token(self):
        url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data = {
            'app_id': self.app_id,
            'app_secret': self.app_secret
        }
        response = requests.post(url, json=data, headers=headers, verify=False)
        access_token = response.json().get('tenant_access_token')
        try:
            return access_token
        except:
            print('获取应用访问令牌失败 >>>')
            self.logger.info('获取应用访问令牌失败 >>>')
            return None

    # def refresh_access_token(self):
    #     while True:
    #         time.sleep(60)
    #         self.access_token_list[0] = self.get_access_token()

    def _request_with_retry(self, method, url, headers=None, params=None, data=None):
        access_token = self.access_token
        if not access_token:
            access_token = self.get_access_token()
            self.access_token = access_token

        headers = headers or {}
        headers['Authorization'] = f'Bearer {access_token}'

        response = requests.request(method, url, headers=headers, params=params, data=data, verify=False)
        content = response.content.decode('utf-8')
        response_json = json.loads(content)
        
        if response_json.get('code') in [99991663,99991661,99991665,99991671,99991677]:  
            new_access_token = self.get_access_token()
            self.access_token = new_access_token
            headers['Authorization'] = f'Bearer {new_access_token}'
            response = requests.request(method, url, headers=headers, params=params, data=data, verify=False)
            content = response.content.decode('utf-8')
            response_json = json.loads(content)

        return response_json
    def create_group(self,user_id,name='无主题'):
        # url = 'https://open.feishu.cn/open-apis/im/v1/chats'
        url = 'https://open.feishu.cn/open-apis/im/v1/chats?set_bot_manager=false&user_id_type=user_id'
        user_id_list = [self.owner_id,user_id]
        # user_id_list = [user_id]
        payload = json.dumps({
            "chat_type": "public",
            "name": name,
            "user_id_list":user_id_list
        })
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response_json = self._request_with_retry("POST", url, headers=headers, data=payload)
        try:
            return response_json['data']['chat_id']
        except:
            print('创建群失败 >>>')
            self.logger.info('创建群失败 >>>')
            return None

    def get_group_share_link(self, chat_id):
        url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/link"
        payload = json.dumps({
            "validity_period": "permanently"
        })
        headers = {'Content-Type': 'application/json'}
        response_json = self._request_with_retry("POST", url, headers=headers, data=payload)
        try:
            return response_json['data']['share_link']
        except:
            print('获取群链接失败 >>>')
            self.logger.info('获取群链接失败 >>>')
            return None

    def get_group_list(self):
        url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=100"
        headers = {}
        response_json = self._request_with_retry("GET", url, headers=headers)
        if response_json.get('code') == 0:
            return [{'chat_id': dict['chat_id'], 'name': dict['name']} for dict in response_json['data']['items']]
        else:
            self.logger.info('获取群列表失败 >>>')
            return None

    def close_group(self, chat_id):
        url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}"
        headers = {}
        response_json = self._request_with_retry("DELETE", url, headers=headers)
        # print('response_json',response_json)
        if response_json.get('msg') == 'success':
            return True
        else:
            return False

    def empty_groups(self):
        res = self.get_group_list()
        print('群聊列表', res)
        delList = []
        for item in res:
            data = self.close_group(item['chat_id'])
            # print('data',data)
            delList.append(data)
            print('delete：', item['chat_id'])
        return delList

    def send(self, msg, chat_id):
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        params = {"receive_id_type": "chat_id"}
        msgContent = {
            "text": msg,
        }
        req = {
            "receive_id": f"{chat_id}",
            "msg_type": "text",
            "content": json.dumps(msgContent)
        }
        payload = json.dumps(req)
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        response_json = self._request_with_retry("POST", url, headers=headers, params=params, data=payload)
        if response_json.get('msg') == 'success':
            return True
        else:
            self.logger.info(f'消息发送失败 >>> ，{response_json}')
            return False

    def creaate_document(self):
        url = "https://open.feishu.cn/open-apis/docx/v1/documents"
        headers = {'Content-Type': 'application/json'}
        response_json = self._request_with_retry("POST", url, headers=headers)
        try:
            return response_json['data']['document']['document_id']
        except:
            return None

    def update_piece(self, document_id, block_id, new_content):
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{block_id}"
        payload = json.dumps({
            "update_text_elements": {
                "elements": [
                    {
                        "text_run": {
                            "content": f"{new_content}"
                        }
                    }
                ]
            }
        })
        headers = {'Content-Type': 'application/json'}
        response_json = self._request_with_retry("PATCH", url, headers=headers, data=payload)
        try:
            if response_json['code'] == 0:
                return True
        except:
            return False

    def get_users(self):
        url = f"https://open.feishu.cn/open-apis/contact/v3/users/find_by_department?department_id=01&department_id_type=department_id&page_size=50"
        headers = {}
        response_json = self._request_with_retry("GET", url, headers=headers)
        try:
            return response_json['data']['items']
        except:
            return None
    # def get_bot(self):
    #     url = f"https://open.feishu.cn/open-apis/bot/v3/info"
    #     headers = {}
    #     response_json = self._request_with_retry("GET", url, headers=headers)
    #     try:
    #         self.open_id = response_json['bot']['open_id']
    #         return response_json['bot']
    #     except:
    #         return None
    # def set_chat_members(self, chat_id, open_id):
    #     url = f"https://open.feishu.cn/open-apis/im/v1/chats/{chat_id}/members?member_id_type=user_id"
        
    #     id_list = [open_id]
    #     if not self.open_id:
    #         self.get_bot()
    #     if self.open_id and open_id != self.open_id:
    #         id_list.append(self.open_id)
    #     print(111,chat_id,id_list)
    #     payload = json.dumps({
    #         "id_list": id_list
    #     })
    #     headers = {'Content-Type': 'application/json; charset=utf-8'}
    #     response_json = self._request_with_retry("POST", url, headers=headers, data=payload)
    #     print(response_json)
    #     try: 
    #         if response_json['code'] == 0:
    #             return True
    #     except:
    #         return False

    def get_document_content(self, document_id):
        url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content"
        headers = {}
        response_json = self._request_with_retry("GET", url, headers=headers)
        try:
            return response_json['data']['content'].strip()
        except:
            return None


if __name__ == '__main__':
    app_id = 'cli_a60aa656b939100e'
    app_secret = 'sarxErZ9gpw2Au6xTVJ2tdEAfZ8sx1s4'
    feishu_api = FeishuAPI(app_id, app_secret)
    
    # print(feishu_api.get_bot())
    # pass
    # # 示例调用
    # chat_id = feishu_api.create_group('测试群')
    # print('创建的群ID:', chat_id)
    # share_link = feishu_api.get_group_share_link(chat_id)
    # print('群分享链接:', share_link)
    # feishu_api.send('Hello, Feishu!', chat_id)
    # feishu_api.empty_groups()