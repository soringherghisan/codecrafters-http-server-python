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

RESPONSE_LINE_200 = "HTTP/1.1 200 OK"
RESPONSE_LINE_200_WITH_DELIMITER = "HTTP/1.1 200 OK\r\n\r\n"
RESPONSE_LINE_404 = "HTTP/1.1 404 Not Found\r\n\r\n"
#
CONTENT_TYPE_HEADER = "Content-Type: text/plain"


def parse_request(received_data: bytes) -> tuple[str, str, str, list]:
    decoded = received_data.decode()
    lines = decoded.split("\r\n")
    method, path, version = lines[0].split()
    headers = lines[1:]
    return method, path, version, headers


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


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_addr = server_socket.accept()  # wait for client
    print(f"Connection from {client_addr}")

    with client_socket:
        # read data from connection
        received_data = client_socket.recv(4096)
        print(f"Received data {received_data}\n")

        # parse received data & respond accordingly
        method, path, version, headers = parse_request(received_data)
        if path == "/":
            response = RESPONSE_LINE_200_WITH_DELIMITER
        elif "echo" in path:
            path_string = extract_string_from_path(path)
            response = build_response([RESPONSE_LINE_200, CONTENT_TYPE_HEADER, f"Content-Length: {len(path_string)}"],
                                      path_string)
        elif "user-agent" in path:
            for header in headers:
                if "user-agent" in header.lower():
                    agent = header.split(":")[-1].strip()
                    response = build_response(
                        [RESPONSE_LINE_200, CONTENT_TYPE_HEADER, f"Content-Length: {len(agent)}"],
                        agent)
                    break
        else:
            response = RESPONSE_LINE_404

        client_socket.sendall(response.encode())


if __name__ == "__main__":
    main()
