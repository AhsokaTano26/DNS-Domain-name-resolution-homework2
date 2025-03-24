import socket
import json

# 读取 DNS 记录
def read_dns_records(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("错误: 文件未找到!")
        return {}
    except json.JSONDecodeError:
        print("错误: 文件内容不是有效的 JSON 格式!")
        return {}

# 顶级域名服务器
def top_level_domain_server():
    dns_records = read_dns_records('tld_dns_records.txt')
    root_server_ip = '127.0.0.1'
    root_server_port = 5300
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 5301))
    server_socket.listen(1)
    print("顶级域名服务器已启动，等待连接...")

    while True:
        conn, addr = server_socket.accept()
        print(f"连接来自: {addr}")
        data = conn.recv(1024).decode()
        if data in dns_records:
            response = dns_records[data]
        else:
            # 连接根服务器查询
            root_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            root_socket.connect((root_server_ip, root_server_port))
            root_socket.sendall(data.encode())
            response = root_socket.recv(1024).decode()
            root_socket.close()
        conn.sendall(response.encode())
        conn.close()

if __name__ == "__main__":
    top_level_domain_server()    