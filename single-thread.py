from socket import *
import ast

# http://192.168.56.1:12000/test.html


serverPort = 8000
timeout = 10

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.settimeout(timeout)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)
print('The server is ready to receive')

while True:
    # Waiting for client connections
    connectionSocket, addr = serverSocket.accept()
    print("connection starts")
    # Get the client request
    request = connectionSocket.recv(1024).decode()

    # Parse HTTP request
    # Split http request into list of fields
    fields = request.split("\r\n")
    # Get only the header fields, not GET, filenames and HTTP version... etc
    request_method = fields[0]
    request_method_list = request_method.split(' ')
    print("Request methods:")
    print(request_method_list)
    header_fields = fields[1:]
    header_fields_dict = {}
    for field in header_fields:
        # check for invalid field
        if not field:
            continue
        key, value = field.split(': ', 1)
        header_fields_dict[key] = value

    print("Request headers:")
    print(header_fields_dict)

    # 400 response code
    # Check if the request method is valid
    valid_request_methods = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTION', 'TRACE', 'PATCH']
    current_method = request_method_list[0]

    # Check for invalid headers, if header is invalid, responde with 400 BAD REQUEST and close connection
    if 'Host' not in header_fields_dict.keys() \
            or len(header_fields_dict) < 1 \
            or current_method not in valid_request_methods:
        response = 'HTTP/1.0 400 BAD REQUEST\n\n'
        response += 'Error code: 400\nREQUEST IS BAD'
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        continue

    # Get the content of the file
    try:
        filename = request_method_list[1]

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
    print("connection closed")
    print("---------------------------------------------")
