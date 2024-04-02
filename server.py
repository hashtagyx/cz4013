import socket
import marshaller
import servertools
import argparse

def start_server(at_most_once=False):
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.settimeout(1.0)  # Set a timeout of 1 second
    server_address = '0.0.0.0' # Define server address
    server_port = 2222  # Define server port
    server_socket.bind((server_address, server_port)) # Bind the socket to the server address and port
    print(f"UDP server up and listening on {server_address}:{server_port}")
    history = {} # Dictionary to store client message history 
    reply_count = 0 # Counter to keep track of replies sent to clients

    try:
        while True:
            try:
                # Receive data and address from client
                byte_string, client_address = server_socket.recvfrom(65535)
                message_object = marshaller.unmarshal(byte_string) # Unmarshal the byte string to get the message object
                print(f"Message from {client_address}: {message_object}")
                # Extract message type and ID
                message_type = message_object['type'] 
                message_id = message_object['id']
                # Check if the message_id exists in history
                if message_id in history:
                    # message_id exists in history, send the stored response to the client
                    print(history[message_id], client_address, type(history[message_id]), type(client_address))
                    server_socket.sendto(history[message_id], client_address) 
                    print(f"Reply Count: {reply_count}")

                elif message_type == 'read':
                    filename, offset, num_bytes = message_object['filename'], int(message_object['offset']), int(message_object['num_bytes'])
                     # Performing read operation
                    read_data = servertools.read(filename, offset, num_bytes) # Read data from the file
                    if at_most_once: # at most once invocation handling 
                        history[message_id] = read_data # store marshalled read bytestring into server history for filtering
                    server_socket.sendto(read_data, client_address) # Send the read data to the client
                    reply_count += 1 # Update counter for the number of replies from the server
                    print(f"Reply Count: {reply_count}")
                    
                elif message_type == 'insert':
                    filename, offset, content = message_object['filename'], int(message_object['offset']), message_object['content']
                     # Performing insert operation
                    insert_resp_data = servertools.insert(filename, offset, content) # Insert content into the file
                    if at_most_once: # at most once invocation handling 
                        history[message_id] = marshaller.marshal(insert_resp_data) # store marshalled read bytestring into server history for filtering
                    # if insertion is successful, callback registered clients
                    if insert_resp_data['type'] == 'response':
                        callback_obj, callback_client_list = servertools.callback(filename) # invoke client callback function to notify subscibed clients of the update
                        if callback_obj['type'] == 'response':
                            callback_data = marshaller.marshal(callback_obj) # marshall the object into bytestring
                            # Sending callback data to each registered client
                            for callback_client in callback_client_list: 
                                server_socket.sendto(callback_data, callback_client) # Sending callback response data to the client
                    
                    server_socket.sendto(marshaller.marshal(insert_resp_data), client_address) # Sending insert response data to the client
                    reply_count += 1 # Update counter for the number of replies from the server
                    print(f"Reply Count: {reply_count}")
                    
                elif message_type == 'monitor':
                    # Handling monitor operation
                    filename, interval = message_object['filename'], int(message_object['interval'])
                    error = servertools.monitor(filename, interval, client_address) # Monitoring the file and sending error if any
                    if error != None:
                        server_socket.sendto(error, client_address) # Send error message to client 
                
                elif message_type == 'delete':
                    filename, offset, num_bytes = message_object['filename'], int(message_object['offset']), int(message_object['num_bytes'])
                    # Performing delete operation
                    delete_resp_data = servertools.delete(filename, offset, num_bytes) 
                    if at_most_once: # at most once invocation handling 
                        history[message_id] = marshaller.marshal(delete_resp_data) # store marshalled read bytestring into server history for filtering
                    # if deletion is successful, callback registered clients
                    if delete_resp_data['type'] == 'response':
                        callback_obj, callback_client_list = servertools.callback(filename) # invoke client callback function to notify subscibed clients of the update
                        if callback_obj['type'] == 'response':
                            callback_data = marshaller.marshal(callback_obj) # marshall the object into bytestring
                            # Sending callback data to each registered client
                            for callback_client in callback_client_list:
                                server_socket.sendto(callback_data, callback_client)
                    
                    server_socket.sendto(marshaller.marshal(delete_resp_data), client_address) # Sending delete response data to the client
                    reply_count += 1
                    print(f"Reply Count: {reply_count}")
                   
                elif message_type == 'get_tmserver':
                    filename = message_object['filename']
                    tm_server_result = servertools.get_tmserver(filename)
                    if at_most_once: # at most once invocation handling 
                        history[message_id] = tm_server_result # store marshalled read bytestring into server history for filtering
                    server_socket.sendto(tm_server_result, client_address)      
                    reply_count += 1  # Update counter for the number of replies from the server
                    print(f"Reply Count: {reply_count}")
                
            except socket.timeout:
                continue  # Continue the loop if recvfrom times out
    except KeyboardInterrupt:
        print("Keyboard interrupt triggered, exiting server.")
    finally:
        server_socket.close()
        print("Server socket closed.")

if __name__ == "__main__":
    # Creating an argument parser object with description
    parser = argparse.ArgumentParser(description="Server Configuration")
    # Adding a command-line argument to enable at most once operation
    parser.add_argument("--at_most_once", action="store_true", help="Ensure operations are performed at most once")
    # Parsing the command-line arguments
    args = parser.parse_args()

    # Starting the server with the at_most_once flag specified
    start_server(at_most_once=args.at_most_once)