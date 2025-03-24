import socket

# 设备端
def device_client():
    top_level_domain_server_ip = '127.0.0.1'
    top_level_domain_server_port = 5301
    domain_name = input("请输入要查询的域名: ")

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((top_level_domain_server_ip, top_level_domain_server_port))
    client_socket.sendall(domain_name.encode())
    response = client_socket.recv(1024).decode()
    print(f"查询结果: {response}")
    client_socket.close()

if __name__ == "__main__":
    device_client()    