from socket import *
from datetime import datetime, timedelta
import socket as soc
import ast

# http://192.168.56.1:12000/test.html
serverPort = 8000
timestamp = datetime.utcnow() + timedelta(seconds=60)
strTimestamp = timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')

# This is a dict storing all last-modified-date of resources
modified_dates = {
    'test.html': strTimestamp
}

def parse_request(request):
    """
    Parse HTTP request

    :param request:
    :return: request method list and header fields
    """
    # Split http request into list of fields
    fields = request.split("\r\n")

    # Get the request method fields
    request_method = fields[0]
    request_method_list = request_method.split(' ')
    print("Request methods:")
    print(request_method_list)

    # Get only the header fields, not GET, filenames and HTTP version... etc
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
    return request_method_list, header_fields_dict


def start_socket(port):
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', port))
    serverSocket.listen(1)
    print('The server is ready to receive')

    while True:
        # Waiting for client connections
        connectionSocket, addr = serverSocket.accept()

        print("connection starts")
        # Get the client request
        request = connectionSocket.recv(1024).decode()

        response = ''
        request_method_list, header_fields_dict = parse_request(request)

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
            target_path = request_method_list[1]
            if target_path == '/test.html':
                resourceName = 'test.html'
                fin = open(resourceName)
                content = fin.read()
                fin.close()
                # 304 response code
                flag = 'If-Modified-Since'
                if flag in header_fields_dict.keys():
                    client_mod_date = header_fields_dict[flag]
                    server_mod_date = modified_dates[resourceName]
                    print(client_mod_date, server_mod_date)
                    is_latest = datetime.strptime(client_mod_date, '%a, %d %b %Y %H:%M:%S GMT') > datetime.strptime(server_mod_date, '%a, %d %b %Y %H:%M:%S GMT')
                    print(is_latest)
                    if is_latest:
                        response = 'HTTP/1.1 304 OK\n\n'
                        connectionSocket.sendall(response.encode())
                        connectionSocket.close()
                        continue
                response = 'HTTP/1.1 200 OK\n\n'
                response += content

        # Handle file not found error
        except FileNotFoundError:
            response = 'HTTP/1.0 404 NOT FOUND\n\n'
            response += 'Error code: 404\nThe file you are looking for is not found.'
        # Handle invalid file address error
        except PermissionError:
            response = 'HTTP/1.0 404 NOT FOUND\n\n'
            response += 'Error code: 404\nThe file you are looking for is not found.'

        # Send HTTP response and close HTTP connection
        connectionSocket.sendall(response.encode())
        connectionSocket.close()
        print("connection closed")
        print("---------------------------------------------")


if __name__ == '__main__':

    start_socket(serverPort)
