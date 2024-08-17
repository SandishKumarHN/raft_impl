from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)
# above line does TCP/IPv4 connection, 
# if you want TCP/IPv6 you can change AF_INET->AF_INET6

sock.connect(('www.python.org', 80))
sock.send(b'GET /index.html HTTP/1.0\r\n\r\n')
parts = []

while True:
    part = sock.recv(1000) # send 1000 bytes at a time
    if part == b'':
        break
    parts.append(part)

response = b''.join(parts)
print("Response:", response.decode('ascii'))


