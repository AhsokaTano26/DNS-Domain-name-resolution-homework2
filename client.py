import socket
import struct

# DNS 服务器地址
DNS_SERVER = ('192.168.52.215', 54)

# 要查询的域名和查询类型
DOMAIN = 'cqu.edu.yuanshen'
# 1 表示 A 记录，2 表示 NS 记录，15 表示 MX 记录
QUERY_TYPE = 1

def build_query(domain, query_type):
    # 事务 ID，可随机生成
    transaction_id = 12345
    # 标志位，设置为标准查询
    flags = 0x0100
    # 查询问题数量
    qdcount = 1
    # 回答记录数量
    ancount = 0
    # 权威名称服务器记录数量
    nscount = 0
    # 附加记录数量
    arcount = 0

    # 构建 DNS 头部
    header = struct.pack('!HHHHHH', transaction_id, flags, qdcount, ancount, nscount, arcount)

    # 构建查询问题部分
    parts = domain.split('.')
    question = b''
    for part in parts:
        length = len(part)
        question += struct.pack('!B', length)
        question += part.encode()
    question += b'\x00'

    # 查询类型和查询类别
    qtype = query_type
    qclass = 1
    question += struct.pack('!HH', qtype, qclass)

    return header + question

def parse_response(response):
    # 解析 DNS 头部
    header = response[:12]
    transaction_id, flags, qdcount, ancount, nscount, arcount = struct.unpack('!HHHHHH', header)

    offset = 12
    # 跳过查询问题部分
    for _ in range(qdcount):
        while True:
            length = response[offset]
            if length == 0:
                offset += 1
                break
            offset += length + 1
        offset += 4

    results = []
    # 解析回答记录
    for _ in range(ancount):
        offset += 2
        qtype, qclass, ttl, rdlength = struct.unpack('!HHIH', response[offset:offset + 10])
        offset += 10
        if qtype == 1:  # A 记录
            ip = socket.inet_ntoa(response[offset:offset + rdlength])
            results.append(('A', ip))
        elif qtype == 2:  # NS 记录
            ns_domain = []
            while True:
                length = response[offset]
                if length == 0:
                    offset += 1
                    break
                offset += 1
                ns_domain.append(response[offset:offset + length].decode())
                offset += length
            results.append(('NS', '.'.join(ns_domain)))
        elif qtype == 15:  # MX 记录
            preference = struct.unpack('!H', response[offset:offset + 2])[0]
            offset += 2
            mx_domain = []
            while True:
                length = response[offset]
                if length == 0:
                    offset += 1
                    break
                offset += 1
                mx_domain.append(response[offset:offset + length].decode())
                offset += length
            results.append(('MX', preference, '.'.join(mx_domain)))
        offset += rdlength

    return results

def main():
    # 创建 UDP 套接字
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # 构建 DNS 查询请求
    query = build_query(DOMAIN, QUERY_TYPE)
    # 发送查询请求
    sock.sendto(query, DNS_SERVER)
    # 接收 DNS 响应
    response, _ = sock.recvfrom(1024)
    # 解析响应
    results = parse_response(response)

    print(f"查询 {DOMAIN} 的 {QUERY_TYPE} 记录结果:")
    for result in results:
        if result[0] == 'A':
            print(f"A 记录: {result[1]}")
        elif result[0] == 'NS':
            print(f"NS 记录: {result[1]}")
        elif result[0] == 'MX':
            print(f"MX 记录: 优先级 {result[1]}, 邮件服务器 {result[2]}")

    sock.close()

if __name__ == "__main__":
    main()