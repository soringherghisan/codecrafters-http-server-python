"""
socket.accept()
    Accept a connection. The socket must be bound to an address and listening for connections.
     The return value is a pair (conn, address) where conn is a new socket object usable to send and receive data
      on the connection, and address is the address bound to the socket on the other end of the connection.

"""

# Uncomment this to pass the first stage
import socket


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_addr = server_socket.accept()  # wait for client

    # read data from connection
    received_data = client_socket.recv(4096)

    # respond
    response = b"HTTP/1.1 200 OK\r\n\r\n"
    client_socket.send(response)


if __name__ == "__main__":
    main()
