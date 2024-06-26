"""
socket.accept()
    Accept a connection. The socket must be bound to an address and listening for connections.
     The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data
      on the connection, and address is the address bound to the socket on the other end of the connection.


Here's what the contents of a HTTP request look like:
    GET /index.html HTTP/1.1
    Host: localhost:4221
    User-Agent: curl/7.64.1

"""

# Uncomment this to pass the first stage
import socket
import threading
import os
import sys

RESPONSE_LINE_200 = "HTTP/1.1 200 OK"
RESPONSE_LINE_201_WITH_DELIMITER = "HTTP/1.1 201 Created\r\n\r\n"
RESPONSE_LINE_200_WITH_DELIMITER = "HTTP/1.1 200 OK\r\n\r\n"
RESPONSE_LINE_404 = "HTTP/1.1 404 Not Found\r\n\r\n"
#
CONTENT_TYPE_TEXT_PLAIN_HEADER = "Content-Type: text/plain"
CONTENT_TYPE_OCTET_STREAM_HEADER = "Content-Type: application/octet-stream"


def parse_request(received_data: bytes) -> tuple[str, str, str, list, str | None]:
    decoded = received_data.decode()
    # Splitting request into headers and body based on the first occurrence of "\r\n\r\n"
    header_part, separator, body_part = decoded.partition("\r\n\r\n")
    lines = header_part.split("\r\n")
    method, path, version = lines[0].split()
    headers = lines[1:]
    # The body will remain None if not found
    body = body_part if separator else None
    return method, path, version, headers, body


def extract_string_from_path(path: str) -> str:
    """
    index 0 == /
    find the next '/' and what's after it is the string we're looking for
    """
    str_index = path.index("/", 1) + 1
    target = path[str_index:]
    return target


def build_response(response_lines: list, body: str = None) -> str:
    """
    :param response_lines: a list containing the strings: response line and headers, in order
    :param body: a string with the body of the response ; optional
    :return: a str with the response, properly formatted , ready to be encoded and sent
    """
    response = "\r\n".join(response_lines)
    if body:
        response += f"\r\n\r\n{body}\r\n\r\n"
    return response


def handle_client_connection(client_socket, client_addr, _dir):
    print(f"Connection from {client_addr}")

    with client_socket:
        # read data from connection
        received_data = client_socket.recv(4096)
        print(f"Received data {received_data}\n")

        # parse received data & respond accordingly
        method, path, version, headers, body = parse_request(received_data)
        if path == "/":
            response = RESPONSE_LINE_200_WITH_DELIMITER
        elif "echo" in path:
            path_string = extract_string_from_path(path)
            response = build_response(
                [RESPONSE_LINE_200, CONTENT_TYPE_TEXT_PLAIN_HEADER, f"Content-Length: {len(path_string)}"],
                path_string)
        elif "user-agent" in path:
            for header in headers:
                if "user-agent" in header.lower():
                    agent = header.split(":")[-1].strip()
                    response = build_response(
                        [RESPONSE_LINE_200, CONTENT_TYPE_TEXT_PLAIN_HEADER, f"Content-Length: {len(agent)}"],
                        agent)
                    break
        elif method == "POST":
            response = RESPONSE_LINE_404
            if _dir and "files" in path:
                file_name = extract_string_from_path(path)
                file_path = os.path.join(_dir, file_name)
                with open(file_path, "w") as f:
                    f.write(body)
                response = RESPONSE_LINE_201_WITH_DELIMITER
        elif _dir and "files" in path:
            file_name = extract_string_from_path(path)
            file_path = os.path.join(_dir, file_name)
            response = RESPONSE_LINE_404
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, "r") as f:
                    contents = f.read()
                    response = build_response(
                        [RESPONSE_LINE_200, CONTENT_TYPE_OCTET_STREAM_HEADER, f"Content-Length: {len(contents)}"],
                        contents)
        else:
            response = RESPONSE_LINE_404

        client_socket.sendall(response.encode())


def main(_dir=None):
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    print("Server has started...")

    try:
        while True:
            client_socket, client_addr = server_socket.accept()  # Wait for client
            client_thread = threading.Thread(target=handle_client_connection, args=(client_socket, client_addr, _dir),
                                             daemon=True)
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
    finally:
        server_socket.close()


if __name__ == "__main__":
    _dir = None
    args = sys.argv
    for idx, arg in enumerate(args):
        if arg == "--directory":
            _dir = args[idx + 1]
            break

    main(_dir)
