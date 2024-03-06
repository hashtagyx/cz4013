# client.py
from clienttools import ClientTools

def main():
    SERVER_IP = "192.168.137.205"  # Replace with your server's IP address
    # SERVER_IP = "10.91.182.34"  # Replace with your server's IP address
    SERVER_PORT = 2222
    client_tools = ClientTools(SERVER_IP, server_port=SERVER_PORT)

    try:
        while True:
            print("\nSelect an option:")
            # List the options as before
            print("1: Read File")
            print("2: Insert content into file")
            print("3: Register for updates")
            print("4: Delete bytes from file")
            print("5: Check last modified time of a file")
            print("0: Exit")
            choice = input("Enter your choice: ")

            if choice == '0':
                print("Exiting client.")
                break

            elif choice in ['1', '2', '3', '4', '5']:
                # Handle each choice, e.g., for reading a file:
                if choice == '1':
                    # read
                    filename = input("Enter the filename to read: ")
                    offset = int(input("Enter the offset: "))
                    num_bytes = int(input("Enter the number of bytes to read: "))
                    client_tools.read(filename, offset, num_bytes)
                # Handle other choices similarly
                elif choice == '2':
                    pass
                    # 'insert'
                    # message['filename'] = input("Enter the filename to insert content into: ")
                    # message['offset'] = int(input("Enter the offset: "))
                    # message['content'] = input("Enter the content to insert: ")

                elif choice == '3':
                    # 'monitor'
                    filename = input("Enter the filename to read: ")
                    interval = int(input("Enter the monitor interval: "))
                    client_tools.monitor(filename, interval)

                elif choice == '4':
                    pass
                    # message['type'] = 'delete'
                    # message['filename'] = input("Enter the filename to delete bytes from: ")
                    # message['offset'] = int(input("Enter the offset: "))
                    # message['num_bytes'] = int(input("Enter the number of bytes to delete: "))

                elif choice == '5':
                    pass
                    # filename = input("Enter the filename to check last modified time: ")
                    # client_tools.get_tmserver(filename)
                    # message['type'] = 'create'
                    # message['filename'] = input("Enter the name of the file to create: ")

    except KeyboardInterrupt:
        print("Keyboard interrupt triggered, exiting client.")

    finally:
        # Close the socket only once when exiting the loop
        client_tools.client_socket.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()