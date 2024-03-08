# clienttools.py
import time
import socket
import marshaller
from collections import OrderedDict
class ClientTools:
    def __init__(self, server_ip, ttl=100, server_port=2222, response_lost=False):
        # Initialize ClientTools with server IP, port, cache TTL, and response handling
        self.cache = {}  # Dictionary to store cached data
        self.ttl = ttl  # Time in seconds for how long cache entries are considered fresh
        self.server_address = (server_ip, server_port)  # Tuple for server address
        self.client_socket = self.initialize_socket()  # Initialize and configure the socket
        self.client_ip, self.client_port = self.client_socket.getsockname()  # Extract client IP and port
        self.unique_req_count = 0  # Counter for generating unique request IDs
        self.response_lost = response_lost  # Flag to simulate response loss scenario
        self.request_count = 0  # Counter for tracking the number of requests sent

    def initialize_socket(self):
        # Create and configure a UDP socket with a timeout
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(2.0)  # Set timeout for recvfrom to 2 seconds
        client_socket.connect(self.server_address)  # Connect the socket to the server
        return client_socket
    
    def generate_request_id(self):
        # Generate a unique request ID based on the client's IP, port, and a sequence number
        self.unique_req_count += 1  # Increment the sequence number
        request_id = f"{self.client_ip}:{self.client_port}:{self.unique_req_count}"
        return request_id

    def read(self, filename, offset, num_bytes):
        # Request to read a range of bytes from a file, utilizing cache and checking for freshness
        print(f"Start cache: {self.cache}")
        time_now = time.time() # Current time for freshness checks
        tm_server = None # Server's last modification time for the file
        if filename not in self.cache:
            self.cache[filename] = {} # Initialize cache for the file if not present
        byte_dict = self.cache[filename] # Reference to the cache for the specific file
        first, last = None, None # Markers for the first and last byte positions needing update from server

        # Iterate through the requested byte range
        for i in range(offset, offset + num_bytes):
            if i not in byte_dict: # If byte i is not cached
                if first == None:
                    first = i
                last = i

            else:
                # Check if cached byte is fresh
                data, tc, tm_client = byte_dict[i]
                time_diff = time_now - tc
                if time_diff >= self.ttl: # If cached byte is stale
                    if not tm_server: # Retrieve server's last modification time if not already done
                        response = self.get_tmserver(filename)
                        if not response or response['type'] == 'error':
                            print('No such filename exists on the server.')
                            return
                        tm_server = float(response['content'])
                    if tm_server == tm_client: # Refresh tc in cache since the file hasn't been modified
                        tc = time_now
                        byte_dict[i] = (data, tc, tm_client)
                    else: # Server's version is newer than cache's version
                        if first == None:
                            first = i
                        last = i

        # Request data from the server for uncached or stale bytes
        if first != None:
            message = {
                'id': self.generate_request_id(),
                'type': 'read',
                'filename': filename,
                'offset': first,
                'num_bytes': last - first + 1
            }

            server_object = self.send_and_receive(message)
            if server_object['type'] == 'error': # No such file or offset invalid
                return

            # Retrieve server's last modification time if not already done
            if not tm_server:
                response = self.get_tmserver(filename)
                if not response or response['type'] == 'error':
                    print('No such filename exists on the server.')
                    return
                tm_server = float(response['content'])

            # Update cache for fetched bytes
            for i in range(last - first + 1):
                byte_dict[i + first] = (server_object['content'][i], time_now, tm_server)
        
        # Generate client requested string for output
        output = ''.join([byte_dict[i][0] for i in range(offset, offset + num_bytes)])
        print(f'Content of file {filename} at offset = {offset} for num_bytes = {num_bytes}: {output}')
        print(f"End cache: {self.cache}")
        
    def get_tmserver(self, filename):
        # Implementation to get the last modification time from the server
        message = {
            'id': self.generate_request_id(),
            'type': 'get_tmserver',
            'filename': filename
        }

        server_object = self.send_and_receive(message)
        if server_object['type'] == 'error': # No such file or offset invalid
            print(server_object['content']) 
        elif server_object['type'] == 'response': # Print last modified time
            print(f"File {filename} was last modified at server time: {server_object['content']}")
        
        return server_object

    def monitor(self, filename, interval):
        # Send a request to monitor a file for updates within a specified interval.
        print(f"Start cache: {self.cache}")
        message = {
                'id': self.generate_request_id(),
                'type': 'monitor',
                'filename': filename,
                'interval': interval
            }
        end_time = time.time() + interval
        self.client_socket.send(marshaller.marshal(message))
        
        try:
            print(f"Client is monitoring file {filename} for the next {interval} seconds.")
            while time.time() < end_time:
                try:
                    byte_string, server_address = self.client_socket.recvfrom(65535)
                    message_object = marshaller.unmarshal(byte_string)
                    if message_object['type'] == 'error': # No file by the filename found on server
                        print(f"Error: {message_object['content']}")
                        return
                    # Update cache with the latest file content from the server.
                    tm_server = float(message_object['tm_server'])
                    content = message_object['content']
                    tc = time.time()
                    self.cache[filename] = {}  # Reset cache for the file.
                    for i in range(len(content)): # Populate with new cache entries
                        self.cache[filename][i] = (content[i], tc, tm_server)
                    
                    # Generate string for output on command line
                    output = ''.join([self.cache[filename][i][0] for i in range(len(content))])
                    print(f"Callback for file {filename} triggered. New file content: {output}")

                except socket.timeout:
                    continue  # Continue the loop if recvfrom times out
        except KeyboardInterrupt:   
            print("Keyboard interrupt triggered, exiting client.")
            self.client_socket.close()
            print("Client socket closed.")

    def insert(self, filename, offset, content): # non-idempotent
        # Prepare and send insert request to the server.
        message = {
            'id': self.generate_request_id(),
            'type': 'insert',
            'filename': filename,
            'offset': offset,
            'content': content
        }
        print(f"Old cache before insert: {self.cache}")
        server_object = self.send_and_receive(message)
        if server_object['type'] == 'error': # No such file or offset invalid
            return

        # server_object['type'] == 'response'
        time_now = time.time() # Current time for cache update
        tm_server = float(server_object['tm_server']) # Last modification time from server

        # Initialize file cache if not present
        if filename not in self.cache:
            self.cache[filename] = {}
            
        file_cache = self.cache[filename]
        # Sort the items of file_cache in descending/reverse order by keys (byte positions)
        sorted_items = sorted(file_cache.items(), key=lambda x: x[0], reverse=True)
        # Create a new OrderedDict with the sorted items
        file_cache = OrderedDict(sorted_items)

        # Calculate the length of the content to be inserted
        LENGTH = len(content)
        new_file_cache = {}

        # Update cache: shift existing bytes to the right to make space for new content (iterating through bytes in descending/reverse order)
        for byte_num in file_cache:
            if byte_num >= offset:
                new_file_cache[byte_num + LENGTH] = file_cache[byte_num]
            elif byte_num < offset:
                new_file_cache[byte_num] = file_cache[byte_num]

        # Insert new content into the cache at the specified offset
        for byte_num in range(offset, offset + LENGTH):
            idx = byte_num - offset
            new_file_cache[byte_num] = (content[idx], time_now, tm_server)
        
        # Update the file cache with the new changes
        self.cache[filename] = new_file_cache
        print(f"New cache after insert: {self.cache}")
        print(f"Inserted {LENGTH} bytes at position {offset} of {filename}.")

    def delete(self, filename, offset, num_bytes): # non-idempotent
        # Construct and send a delete request to the server.
        message = {
            'id': self.generate_request_id(),
            'type': 'delete',
            'filename': filename,
            'offset': offset,
            'num_bytes': num_bytes
        }
        print(f"Old cache before delete: {self.cache}")
        server_object = self.send_and_receive(message)
        if server_object['type'] == 'error': # No such file or offset invalid
            return
        
        # Ensure cache exists for the file; if not, initialize it
        if filename not in self.cache:
            self.cache[filename] = {}
            
        file_cache = self.cache[filename]
        # Sort the items of file_cache in ascending order by keys (byte positions)
        sorted_items = sorted(file_cache.items(), key=lambda x: x[0])
        # Create a new OrderedDict with the sorted items
        file_cache = OrderedDict(sorted_items)

        
        LENGTH = num_bytes # Length of content to be deleted
        new_file_cache = {} # Temporary cache to hold updated values

        for byte_num in file_cache: 
            # Keep bytes before deletion offset unchanged
            if byte_num < offset: 
                new_file_cache[byte_num] = file_cache[byte_num]
            # Shift bytes after the deleted section to the left
            elif byte_num >= offset + LENGTH:
                new_file_cache[byte_num - LENGTH] = file_cache[byte_num]
        
        # Replace the old cache with the updated cache reflecting deletions
        self.cache[filename] = new_file_cache
        print(f"New cache after delete: {self.cache}")
        print(f"Deleted {LENGTH} bytes at position {offset} of {filename}.")
    
    def send_and_receive(self, message):
        # Send a request to the server and handle the response, including simulating response loss if enabled
        print(message)
        self.client_socket.send(marshaller.marshal(message))  # Send the marshalled message to the server
        self.request_count += 1  # Increment the request counter
        if self.response_lost:  # Simulate a lost response scenario
            response, _ = self.client_socket.recvfrom(65535)  # Dummy receive to simulate waiting for a lost response
            print(f"r1:r{response}")
            self.client_socket.send(marshaller.marshal(message))  # Resend the message
            print(message)
            self.request_count += 1  # Increment the request counter again for the resent message

        print(f"Request Count: {self.request_count}")
        try:
            server_data, server = self.client_socket.recvfrom(65535)  # Wait for the server's response
            print(f"r2:r{server_data}")
            server_object = marshaller.unmarshal(server_data)  # Unmarshal the response data into a Python object
            if server_object['type'] == 'error':  # Handle any errors reported by the server
                print(server_object['content'])
            return server_object
        except socket.timeout:
            print("No response received, server might be busy or offline. Try again.")
            return {
                'type': 'error',
                'content': 'No response received, server might be busy or offline. Try again.'
            }