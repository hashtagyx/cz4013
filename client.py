# client.py
import argparse
import re
from clienttools import ClientTools

def main(ttl, response_lost):
    # Initialize server IP and port configurations.
    SERVER_IP = "192.168.0.105"  # Primary server IP. Replace with the actual IP address.
    SERVER_PORT = 2222  # Server port. Change if using a different port.
    
    # Initialize client tools with server configurations and arguments.
    client_tools = ClientTools(server_ip=SERVER_IP, ttl=ttl, server_port=SERVER_PORT, response_lost=response_lost)

    try:
        while True:
            # Display menu options for the client.
            print("\nSelect an option:")
            print("1: Read File")
            print("2: Insert content into file")
            print("3: Register for updates")
            print("4: Delete bytes from file")
            print("5: Check last modified time of a file")
            print("0: Exit")
            choice = input("Enter your choice: ")

            # Exit loop if choice is 0.
            if choice == '0':
                print("Exiting client.")
                break

            # Process user choice.
            if choice == '1':
                # Handle file read operation.
                filename = get_valid_string("Enter the filename to read: ")
                offset = get_positive_int("Enter the offset: ", allow_zero=True)
                num_bytes = get_positive_int("Enter the number of bytes to read: ")
                client_tools.read(filename, offset, num_bytes)

            elif choice == '2':
                # Handle content insertion into file.
                filename = get_valid_string("Enter the filename to insert content into: ")
                offset = get_positive_int("Enter the offset: ", allow_zero=True)
                content = get_valid_string("Enter the content to insert: ")
                client_tools.insert(filename, offset, content)

            elif choice == '3':
                # Handle update registration.
                filename = get_valid_string("Enter the filename to monitor: ")
                interval = get_positive_int("Enter the monitor interval: ")
                client_tools.monitor(filename, interval)

            elif choice == '4':
                # Handle byte deletion from file.
                filename = get_valid_string("Enter the filename to delete bytes from: ")
                offset = get_positive_int("Enter the offset: ", allow_zero=True)
                num_bytes = get_positive_int("Enter the number of bytes to delete: ")
                client_tools.delete(filename, offset, num_bytes)

            elif choice == '5':
                # Handle checking the last modified time of a file.
                filename = get_valid_string("Enter the filename to check the last modified time at the server: ")
                client_tools.get_tmserver(filename)

    except KeyboardInterrupt:
        # Handle keyboard interrupt to gracefully exit.
        print("Keyboard interrupt triggered, exiting client.")

    finally:
        # Ensure the client socket is closed before exiting.
        client_tools.client_socket.close()
        print("Socket closed.")

def get_valid_string(prompt):
    # Validate string input to contain only alphanumeric characters and '.'.
    pattern = re.compile(r'^[\w.]+$')
    while True:
        user_input = input(prompt)
        if pattern.match(user_input):
            return user_input
        else:
            print("Invalid input. Please use only alphanumeric characters and '.'.")

def get_positive_int(prompt, allow_zero=False):
    # Validate input to ensure it's a positive integer. Optionally allow zero.
    while True:
        try:
            value = int(input(prompt))
            if value > 0 or (allow_zero and value == 0):
                return value
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

if __name__ == "__main__":
    # Parse command-line arguments for ttl and response_lost options.
    parser = argparse.ArgumentParser(description="Client for interacting with a file server.")
    parser.add_argument('--ttl', type=int, default=100, help='Time-to-live for cache entries in seconds (default: 100 seconds)')
    parser.add_argument("--response_lost", action="store_true", help="Handle scenarios where a response from the server might be lost")
    args = parser.parse_args()
    
    # Execute the main function with parsed arguments.
    main(ttl=args.ttl, response_lost=args.response_lost)
