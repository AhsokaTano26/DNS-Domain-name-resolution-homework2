import socket
import struct

# 根 DNS 服务器监听地址和端口
ROOT_SERVER_ADDR = ('0.0.0.0', 54)

# 维护域名与顶级 DNS 服务器 IP 的映射关系
TLD_SERVER_MAPPING = {
    "com": "192.168.1.2",
    "org": "192.168.1.3",
    "net": "192.168.1.4",
    "yuanshen": "192.168.1.5"
}

def parse_domain(query):
    """解析查询请求中的域名"""
    offset = 12
    domain_parts = []
    while True:
        length = query[offset]
        if length == 0:
            break
        offset += 1
        domain_parts.append(query[offset:offset + length].decode())
        offset += length
    return ".".join(domain_parts)

def handle_query(query):
    # 解析查询请求中的域名
    domain = parse_domain(query)
    # 获取顶级域名
    tld = domain.split('.')[-1]

    # 根据顶级域名查找对应的顶级 DNS 服务器 IP 地址
    tld_server_ip = TLD_SERVER_MAPPING.get(tld)
    if not tld_server_ip:
        # 如果未找到对应的顶级 DNS 服务器 IP 地址，可以返回错误信息或默认值
        tld_server_ip = "0.0.0.0"

    response = query[:2]  # 复制事务 ID
    response += struct.pack('!H', 0x8180)  # 响应标志
    response += query[4:6]  # 复制查询数量
    response += struct.pack('!HH', 0, 0)  # 回答数量和权威名称服务器数量为 0
    response += struct.pack('!H', 1)  # 附加记录数量为 1

    # 复制查询问题部分
    response += query[12:]

    # 附加记录：顶级 DNS 服务器的 IP 地址
    response += struct.pack('!H', 0xC00C)  # 指向查询问题中的域名
    response += struct.pack('!HHIH', 2, 1, 0, 4)  # NS 记录，TTL 为 0，数据长度为 4
    response += socket.inet_aton(tld_server_ip)

    return response

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(ROOT_SERVER_ADDR)

    print(f"Root DNS server listening on {ROOT_SERVER_ADDR}")

    while True:
        query, addr = sock.recvfrom(1024)
        response = handle_query(query)
        sock.sendto(response, addr)

if __name__ == "__main__":
    main()