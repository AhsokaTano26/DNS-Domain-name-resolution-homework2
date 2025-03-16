import socket
import struct

# 服务器监听地址和端口
SERVER_ADDR = ('0.0.0.0', 53)

# 根 DNS 服务器维护的顶级域和顶级 DNS 服务器 IP 映射
ROOT_MAPPING = {
    "com": "127.0.0.1",
    "org": "127.0.0.1",
    "net": "127.0.0.1",
    "yuanshen":"192.168.52.179"
}

# 顶级 DNS 服务器维护的二级域和权威 DNS 服务器 IP 映射
TLD_MAPPING = {
    "example.com": "127.0.0.1",
    "test.org": "127.0.0.1",
    "edu.yuanshen":"192.168.52.179"
}

# 权威 DNS 服务器维护的域名和记录映射，包含 A、MX、NS 记录
AUTH_MAPPING = {
    "cqu.edu.yuanshen": [
        (1, "192.168.52.179")  # A 记录
    ],
    "mail.edu.yuanshen": [
        (15, 10, "smtp.edu.yuanshen")  # MX 记录，优先级 10
    ],
    "edu.yuanshen": [
        (2, "ns1.edu.yuanshen"),  # NS 记录
        (2, "ns2.edu.yuanshen")
    ]
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

def parse_query_type(query):
    """解析查询类型"""
    offset = 12
    while True:
        length = query[offset]
        if length == 0:
            break
        offset += length + 1
    return struct.unpack('!H', query[offset + 1:offset + 3])[0]

def build_response(query, records=None):
    response = query[:2]  # 复制事务 ID
    response += struct.pack('!H', 0x8180)  # 响应标志
    response += query[4:6]  # 复制查询数量
    if records:
        ancount = len(records)
    else:
        ancount = 0
    response += struct.pack('!HH', ancount, 0)  # 回答数量和权威名称服务器数量
    response += struct.pack('!H', 0)  # 附加记录数量

    # 复制查询问题部分
    response += query[12:]

    if records:
        for record_type, data in records:
            if record_type == 1:  # A 记录
                response += struct.pack('!H', 0xC00C)  # 指向查询问题中的域名
                response += struct.pack('!HHIH', 1, 1, 3600, 4)  # A 记录，TTL 为 3600 秒，数据长度为 4
                response += socket.inet_aton(data)
            elif record_type == 2:  # NS 记录
                response += struct.pack('!H', 0xC00C)  # 指向查询问题中的域名
                response += struct.pack('!HHIH', 2, 1, 3600, len(data) + 2)  # NS 记录，TTL 为 3600 秒
                parts = data.split('.')
                for part in parts:
                    response += struct.pack('!B', len(part))
                    response += part.encode()
                response += b'\x00'
            elif record_type == 15:  # MX 记录
                preference, exchange = data
                response += struct.pack('!H', 0xC00C)  # 指向查询问题中的域名
                response += struct.pack('!HHIH', 15, 1, 3600, len(exchange) + 4)  # MX 记录，TTL 为 3600 秒
                response += struct.pack('!H', preference)
                parts = exchange.split('.')
                for part in parts:
                    response += struct.pack('!B', len(part))
                    response += part.encode()
                response += b'\x00'

    return response

def handle_query(query):
    domain = parse_domain(query)
    query_type = parse_query_type(query)

    # 先尝试作为权威 DNS 服务器处理
    records = AUTH_MAPPING.get(domain)
    if records:
        filtered_records = [record for record in records if record[0] == query_type]
        if filtered_records:
            return build_response(query, filtered_records)

    # 再尝试作为顶级 DNS 服务器处理
    for tld_domain, auth_ip in TLD_MAPPING.items():
        if domain.endswith(tld_domain):
            if query_type == 2:  # NS 查询
                records = [(2, auth_ip)]
                return build_response(query, records)

    # 最后作为根 DNS 服务器处理
    tld = domain.split('.')[-1]
    tld_ip = ROOT_MAPPING.get(tld)
    if tld_ip:
        if query_type == 2:  # NS 查询
            records = [(2, tld_ip)]
            return build_response(query, records)

    # 未找到匹配信息，返回空响应
    return build_response(query)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SERVER_ADDR)

    print(f"DNS server listening on {SERVER_ADDR}")

    while True:
        query, addr = sock.recvfrom(1024)
        response = handle_query(query)
        sock.sendto(response, addr)

if __name__ == "__main__":
    main()