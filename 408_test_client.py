import socket
import time
from datetime import datetime, timedelta

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', 8000)

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(server_address)
request = 'GET /test.html HTTP/1.0\r\n'

# Create header
headers = 'Host: 0.0.0.0\r\n'

# Add more headers

request += headers

print("Test request:")
print(request)

time.sleep(6)
s.sendall(request.encode())
response = s.recv(4096)

print("response:", response.decode())

s.close()
