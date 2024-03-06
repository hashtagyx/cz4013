import socket

def udp_client(server_ip, server_port=2222):
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)  # Set timeout for recvfrom

    # Define the server address and port
    server_address = (server_ip, server_port)

    try:
        while True:
            # Message to be sent to the server
            message = input("Enter text input to send to the server: ")
            message_bytes = message.encode('utf-8')
            print(f"Sending message to server: {message}")
            client_socket.sendto(message_bytes, server_address)

            # Waiting for response from the server
            print("Waiting for response...")
            try:
                data, server = client_socket.recvfrom(4096)
                print(f"Received message from server: {data.decode('utf-8')}")
            except socket.timeout:
                print("No response received, server might be busy or offline. Try again.")
                continue  # Continue waiting for user input

    except KeyboardInterrupt:
        print("Keyboard interrupt triggered, exiting client.")

    finally:
        # Close the socket only once when exiting the loop
        client_socket.close()
        print("Socket closed.")

if __name__ == "__main__":
    # SERVER_IP = "192.168.0.104"  # Replace with your server's IP address
    SERVER_IP = "192.168.137.205"
    udp_client(SERVER_IP)
