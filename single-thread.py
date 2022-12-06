from socket import *
from datetime import datetime, timedelta
import time
import socket as soc
import ast

# http://192.168.56.1:12000/test.html
serverPort = 8000
timestamp = datetime.utcnow() + timedelta(seconds=60)
strTimestamp = timestamp.strftime('%a, %d %b %Y %H:%M:%S GMT')

TIMEOUT_IN_SEC = 5

# This is a dict storing all last-modified-date of resources
modified_dates = {
    'test.html': strTimestamp
}


def parse_method(all_fields):
    """
    Get the request method fields
    """

    request_method = all_fields[0]
    request_method_list = request_method.split(' ')

    print("Request methods:")
    print(request_method_list)

    return request_method_list


def parse_header_fields(all_fields):
    """
    Get only the header fields, not GET, filenames and HTTP version... etc
    """
    header_fields = all_fields[1:]
    header_fields_dict = {}

    for field in header_fields:
        # check for invalid field
        if not field:
            continue
        key, value = field.split(': ', 1)
        header_fields_dict[key] = value

    print("Request headers:")
    print(header_fields_dict)

    return header_fields_dict


def parse_request(request):
    """
    Parse HTTP request

    :param request:
    :return: request method list and header fields

    """
    # Split http request into list of fields
    all_fields = request.split("\r\n")
    request_method_list = parse_method(all_fields)
    header_fields_dict = parse_header_fields(all_fields)

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
        deadline = time.time() + TIMEOUT_IN_SEC
        # Get the client request
        is_time_out = False

        while True:
            if time.time() > deadline:
                response = 'HTTP/1.0 408 REQUEST TIMEOUT\n\n'
                connectionSocket.sendall(response.encode())
                time.sleep(5)
                connectionSocket.close()
                print("connection closed")
                print("---------------------------------------------")
                is_time_out = True
                break
            if not is_time_out:
                request = connectionSocket.recv(1024).decode()
                if request:
                    break

        if is_time_out:
            continue
        response = ''
        request_method_list, header_fields_dict = parse_request(request)

        # 400 response code
        # Check if the request method is valid
        valid_request_methods = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTION', 'TRACE', 'PATCH']
        current_method = request_method_list[0]
        # Check for invalid headers, if header is invalid, respond with 400 BAD REQUEST and close connection
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
            resourceName = request_method_list[1]
            if resourceName == '/test.html':
                resourceName = 'test.html'

                # 304 response code
                flag = 'If-Modified-Since'
                if flag in header_fields_dict.keys():
                    client_mod_date = header_fields_dict[flag]
                    server_mod_date = modified_dates[resourceName]
                    print("last_modified:", server_mod_date)
                    is_latest = datetime.strptime(client_mod_date, '%a, %d %b %Y %H:%M:%S GMT') > datetime.strptime(
                        server_mod_date, '%a, %d %b %Y %H:%M:%S GMT')
                    if is_latest:
                        response = 'HTTP/1.1 304 Not Modified\n\n'
                        connectionSocket.sendall(response.encode())
                        connectionSocket.close()
                        continue
            # Read resource and add it to the response
            fin = open(resourceName)
            content = fin.read()
            fin.close()
            response = 'HTTP/1.1 200 OK\n\n'
            response += content

            if 'modified_date' in header_fields_dict.keys():
                response = modified_dates[resourceName]


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
