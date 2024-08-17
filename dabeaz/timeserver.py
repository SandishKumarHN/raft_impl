from socket import socket, AF_INET, SOCK_STREAM
import time
from message import send_message
    
    
sock = socket(AF_INET, SOCK_STREAM)
sock.bind(('', 12345))
sock.listen()

while True:
    client, addr = sock.accept()
    print('Connection from, ', addr)
    msg = time.ctime()
    send_message(client, msg.encode('utf-8'))
    client.close()
    


    