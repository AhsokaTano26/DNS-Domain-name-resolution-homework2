import socket
import struct

# 权威服务器监听地址和端口
AUTH_SERVER_ADDR = ('0.0.0.0', 53)
# 域名对应的 IP 地址
DOMAIN_IP = '192.168.1.100'

def handle_query(query):
    response = query[:2]  # 复制事务 ID
    response += struct.pack('!H', 0x8180)  # 响应标志
    response += query[4:6]  # 复制查询数量
    response += struct.pack('!HH', 1, 0)  # 回答数量为 1，权威名称服务器数量为 0
    response += struct.pack('!H', 0)  # 附加记录数量为 0

    # 复制查询问题部分
    response += query[12:]

    # 回答记录：域名对应的 IP 地址
    response += struct.pack('!H', 0xC00C)  # 指向查询问题中的域名
    response += struct.pack('!HHIH', 1, 1, 3600, 4)  # A 记录，TTL 为 3600 秒，数据长度为 4
    response += socket.inet_aton(DOMAIN_IP)

    return response

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(AUTH_SERVER_ADDR)

    print(f"Authoritative DNS server listening on {AUTH_SERVER_ADDR}")

    while True:
        query, addr = sock.recvfrom(1024)
        response = handle_query(query)
        sock.sendto(response, addr)

if __name__ == "__main__":
    main()