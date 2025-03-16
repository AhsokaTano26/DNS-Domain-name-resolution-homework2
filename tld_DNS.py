import socket
import struct

# 顶级 DNS 服务器监听地址和端口
TLD_SERVER_ADDR = ('0.0.0.0', 54)
# 权威服务器的 IP 地址
AUTH_SERVER_IP = '192.168.1.3'

def handle_query(query):
    # 简单处理，直接返回权威服务器的 IP 地址
    response = query[:2]  # 复制事务 ID
    response += struct.pack('!H', 0x8180)  # 响应标志
    response += query[4:6]  # 复制查询数量
    response += struct.pack('!HH', 0, 0)  # 回答数量和权威名称服务器数量为 0
    response += struct.pack('!H', 1)  # 附加记录数量为 1

    # 复制查询问题部分
    response += query[12:]

    # 附加记录：权威服务器的 IP 地址
    response += struct.pack('!H', 0xC00C)  # 指向查询问题中的域名
    response += struct.pack('!HHIH', 2, 1, 0, 4)  # NS 记录，TTL 为 0，数据长度为 4
    response += socket.inet_aton(AUTH_SERVER_IP)

    return response

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(TLD_SERVER_ADDR)

    print(f"TLD DNS server listening on {TLD_SERVER_ADDR}")

    while True:
        query, addr = sock.recvfrom(1024)
        response = handle_query(query)
        sock.sendto(response, addr)

if __name__ == "__main__":
    main()