from socket import socket, AF_INET, SOCK_STREAM
from message import recv_message

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('localhost', 12345))
print("current time is: ", recv_message(sock))