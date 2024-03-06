import socket
import marshaller

def udp_client(server_ip, server_port=2222):
    # Create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)  # Set timeout for recvfrom
    client_socket.connect((server_ip, server_port))
    client_ip, client_port = client_socket.getsockname()
    
    # Define the server address and port
    server_address = (server_ip, server_port)
    request_count = 0
    
    def generate_request_id():
        nonlocal request_count
        request_count += 1  # Increment the global request count

        # Combine the request count with the client's IP and port to form the requestId
        request_id = f"{client_ip}:{client_port}:{request_count}"
        return request_id
    
    try:
        while True:
            print("\nSelect an option:")
            print("1: Read File")
            print("2: Insert content into file")
            print("3: Register for updates")
            print("4: Delete bytes from file")
            print("5: Create empty file")
            print("0: Exit")

            choice = input("Enter your choice: ")

            if choice == '0':
                print("Exiting client.")
                break

            elif choice in ['1', '2', '3', '4', '5']:
                
                message = {}

                if choice == '1':
                    message['type'] = 'read'
                    message['filename'] = input("Enter the filename to read: ")
                    message['offset'] = int(input("Enter the offset: "))
                    message['num_bytes'] = int(input("Enter the number of bytes to read: "))

                elif choice == '2':
                    message['type'] = 'insert'
                    message['filename'] = input("Enter the filename to insert content into: ")
                    message['offset'] = int(input("Enter the offset: "))
                    message['content'] = input("Enter the content to insert: ")

                elif choice == '3':
                    message['type'] = 'monitor'
                    message['filename'] = input("Enter the filename to monitor: ")

                elif choice == '4':
                    message['type'] = 'delete'
                    message['filename'] = input("Enter the filename to delete bytes from: ")
                    message['offset'] = int(input("Enter the offset: "))
                    message['num_bytes'] = int(input("Enter the number of bytes to delete: "))

                elif choice == '5':
                    message['type'] = 'create'
                    message['filename'] = input("Enter the name of the file to create: ")

                message['id'] = generate_request_id()
                byte_string = marshaller.marshal(message)
                print(f"Sending message to server: {byte_string}")
                client_socket.send(byte_string)

                # Waiting for response from the server
                print("Waiting for response...")
                try:
                    data, server = client_socket.recvfrom(4096)
                    print(f"Received message from server: {data.decode('utf-8')}")
                except socket.timeout:
                    print("No response received, server might be busy or offline. Try again.")

            else:
                print("Invalid choice. Please enter a valid option.")

    except KeyboardInterrupt:
        print("Keyboard interrupt triggered, exiting client.")

    finally:
        # Close the socket only once when exiting the loop
        client_socket.close()
        print("Socket closed.")

if __name__ == "__main__":
    SERVER_IP = "192.168.137.205"  # Replace with your server's IP address
    # SERVER_IP = "10.91.182.34"
    SERVER_IP = "192.168.137.205"  # Replace with your server's IP address
    # SERVER_IP = "10.91.182.34"
    udp_client(SERVER_IP)



