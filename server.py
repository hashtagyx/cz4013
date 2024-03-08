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
                    filename, offset, content = message_object['filename'], int(message_object['offset']), message_object['content']
                    insert_resp_data = servertools.insert(filename, offset, content)
                    
                    # if insertion is successful, callback registered clients
                    if insert_resp_data['type'] == 'response':
                        callback_obj, callback_client_list = servertools.callback(filename)
                        if callback_obj['type'] == 'response':
                            callback_data = marshaller.marshal(callback_obj)
                            for callback_client in callback_client_list:
                                server_socket.sendto(callback_data, callback_client)
                    
                    server_socket.sendto(marshaller.marshal(insert_resp_data), client_address)
                    
                elif message_type == 'monitor':
                    filename, interval = message_object['filename'], int(message_object['interval'])
                    error = servertools.monitor(filename, interval, client_address)
                    if error != None:
                        server_socket.sendto(error, client_address)
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
