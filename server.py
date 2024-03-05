import socket
import marshaller

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(1.0)  # Set a timeout of 1 second
    server_address = '0.0.0.0'
    server_port = 2222
    server_socket.bind((server_address, server_port))
    print(f"UDP server up and listening on {server_address}:{server_port}")

    try:
        while True:
            try:
                message, client_address = server_socket.recvfrom(1024)
                print(f"Message from {client_address}: {message.decode('utf-8')}")
                server_msg = "This is the server."
                server_socket.sendto(server_msg.encode(), client_address)
            except socket.timeout:
                continue  # Continue the loop if recvfrom times out
    except KeyboardInterrupt:
        print("Keyboard interrupt triggered, exiting server.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    start_server()
