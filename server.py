import socket
import marshaller
import servertools

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(1.0)  # Set a timeout of 1 second
    server_address = '0.0.0.0'
    server_port = 2222
    server_socket.bind((server_address, server_port))
    print(f"UDP server up and listening on {server_address}:{server_port}")

    monitor_dictionary = {} # key: filename, val: list of tuples [(client_address, end_time), ... ]

    # {
    #     'a.txt': [(client_address, 8pm), (client_address, 7.30pm), (client_address, 7pm)], 
    #     'b.txt': []
    # }

    try:
        while True:
            try:
                byte_string, client_address = server_socket.recvfrom(65535)
                message_object = marshaller.unmarshal(byte_string)
                print(f"Message from {client_address}: {message_object}")
                message_type = message_object['type']

                if message_type == 'read':
                    filename, offset, num_bytes = message_object['filename'], int(message_object['offset']), int(message_object['num_bytes'])
                    read_data = servertools.read(filename, offset, num_bytes)
                    server_socket.sendto(read_data, client_address)
                    
                elif message_type == 'insert':
                    # insert(filename, offset, content)
                    pass
                elif message_type == 'monitor':
                    # monitor(filename, interval, client_address):
                    
                    pass
                elif message_type == 'delete':
                    # delete(filename, offset, num_bytes)
                    pass
                elif message_type == 'create':
                    # create(filename)
                    pass
                elif message_type == 'get_tmserver':
                    filename = message_object['filename']
                    tm_server_result = servertools.get_tmserver(filename)
                    server_socket.sendto(tm_server_result, client_address)      
                
            except socket.timeout:
                continue  # Continue the loop if recvfrom times out
    except KeyboardInterrupt:
        print("Keyboard interrupt triggered, exiting server.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    start_server()
