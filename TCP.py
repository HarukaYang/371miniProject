from socket import *

# http://192.168.56.1:12000/test.html


serverPort = 8000

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

while True:
    # Waiting for client connections
    connectionSocket, addr = serverSocket.accept()

    # Get the client request
    request = connectionSocket.recv(1024).decode()

    # Parse HTTP headers
    request_list = request.split('\n')
    headers = request_list[1:]
    print("headers:")
    print(headers)

    # 400 response code
    # Check for invalid headers, if header is invalid, responde with 400 BAD REQUEST and close connection
    if 'Host: ' not in str(headers) or len(headers) < 1:
        response = 'HTTP/1.0 40 BAD REQUEST\n\n'
        response += 'Error code: 400\nREQUEST IS BAD'
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        continue

    # Get the content of the file
    try:
        filename = request_list[0].split()[1]
        print("filename:")
        print(filename)
        if filename == '/test.html':
            filename = 'test.html'
        fin = open(filename)
        content = fin.read()
        fin.close()
        response = 'HTTP/1.0 200 OK\n\n'
        response += content

    # Handle file not found error
    except FileNotFoundError:
        response = 'HTTP/1.0 404 NOT FOUND\n\n'
        response += 'Error code: 404\nThe file you are looking for is not found.'

    # Handle invalid file address error
    except PermissionError:
        response = 'HTTP/1.0 404 NOT FOUND\n\n'
        response += 'Error code: 404\nThe file you are looking for is not found.'

    # Send HTTP response
    connectionSocket.sendall(response.encode())

    # Close HTTP connection
    connectionSocket.close()
