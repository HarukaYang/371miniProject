import socket
from datetime import datetime, timedelta
import requests

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8000)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(server_address)
request = 'GET /test.html HTTP/1.0\r\n'


headers = 'Host: 0.0.0.0\r\n'

# add more headers
timestamp = datetime.utcnow() + timedelta(seconds=60)
strTimestamp = timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')
headers += 'if-modified-since: ' + strTimestamp + '\r\n'

request += headers + '\r\n'

s.sendall(request.encode())
response = s.recv(4096)

print("response:", response.decode())

s.close()
