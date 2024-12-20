import socket
import select

class SocketClient:
    def __init__(self, server_address, server_port):
        self.server_address = server_address
        self.server_port = server_port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.server_address, self.server_port))

    def send_message(self, message):
        self.client_socket.sendall(message.encode())

    def receive_message(self, timeout=1.0):
        ready_to_read, _, _ = select.select([self.client_socket], [], [], timeout)
        if self.client_socket in ready_to_read:
            data = self.client_socket.recv(1024)
            if not data:
                print('服务器关闭连接')
                return None
            return data.decode()
        else:
            print('没有数据可读')
            return None

    def close(self):
        self.client_socket.close()


# 调整了一下字段驼峰格式

# socket连接
# xxx.xxx.xxx.xxx:xx/phone_num=12312341234&mac=xx_xx_xx_xx

# 服务器推送
	
# 	------------------------------------------------
# 	设备连接成功消息
# 	message name:
# 		device_reg
# 	message body:
# 		{
# 			"code":0,
# 			"msg":"操作成功"
# 		}
# 	解释：
# 		code 为 0 表示成功，其他表示失败
		
# 	------------------------------------------------
# 	服务器订单推送
# 	message name:
# 		order_push
# 	message body:
# 		{
# 			"orderId":12345678,
# 			"name": "这里是雇主的姓名",
# 			"address"："这里是雇主的地址",
# 			"phone":"这里是雇主的电话",
# 			"serviceDate":"2024-09-11",
# 			"serviceTime":18,
# 			"serviceDuration":2,
# 			"remark":"备注信息"
# 		}

# 	------------------------------------------------
# 	服务器订单取消
# 	message name:
# 		order_cancel
# 	message body:
# 		{
# 			"orderId":12345678,
# 			"jdAccount":"baojie123456"
# 		}


# 客户端推送, 客户端推送失败需要有重试机制

# 	------------------------------------------------
# 	订单取消上报
# 	message name:
# 		order_cancel_res
# 	message body:
# 		{
# 			"orderId":12345678,
# 			"result": false,
# 			"message":"取消不了"
# 		}

# 	------------------------------------------------
# 	订单约单结果上报
# 	message name:
# 		order_exec_res
# 	message body:
# 		{
# 			"orderId":12345678,
# 			"result": false,
# 			"message":"下失败了了",
# 			"extra: {
# 				"jdOrder":"JD1233211112",
# 				"jdAccount":"baojie123456",
# 				"orderAmount": 55
# 			}
# 		}

# 	------------------------------------------------
# 	设备添加京东账号
# 	message name:
# 		jd_account_add
# 	message body:
# 		{
# 			"jdAccount":"baojie123456",
# 			"jdPwd":"aabbccdd"
# 		}

# 	------------------------------------------------
# 	设备移除京东账号
# 	message name:
# 		jd_account_remove
# 	message body:
# 		{
# 			"jdAccount":"baojie123456",
# 		}

# 00-91-9E-42-B0-AE
if __name__ == "__main__":
    client = SocketClient('192.168.191.100/phone_num=18838970230&mac=00-91-9E-42-B0-AE', 16001)
    try:
        client.send_message('Hello, server!')
        while True:
            message = client.receive_message()
            if message is not None:
                print(f'收到响应: {message}')
            else:
                break
    except ConnectionResetError as e:
        print(f'连接被重置: {e}')
    finally:
        client.close()