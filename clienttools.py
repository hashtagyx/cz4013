# clienttools.py
import time
import socket
import marshaller

class ClientTools:
    def __init__(self, server_ip, ttl=100, server_port=2222):
        self.cache = {}
        self.ttl = ttl  # Time-to-live for cache entries in seconds
        self.server_address = (server_ip, server_port)
        self.client_socket = self.initialize_socket()
        self.client_ip, self.client_port = self.client_socket.getsockname()
        self.request_count = 0

    def initialize_socket(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.settimeout(1.0)  # Set timeout for recvfrom
        client_socket.connect(self.server_address)
        return client_socket

    def generate_request_id(self):
        self.request_count += 1  # Increment the global request count
        request_id = f"{self.client_ip}:{self.client_port}:{self.request_count}"
        return request_id

    def read(self, filename, offset, num_bytes):
        # Implementation of the read method with caching logic
        print(f"Start cache: {self.cache}")
        cur_time = time.time()
        tm_server = None
        if filename not in self.cache:
            self.cache[filename] = {}
        byte_dict = self.cache[filename]
        first, last = None, None

        for i in range(offset, offset + num_bytes):
            if i not in byte_dict: # byte i is not cached
                if first == None:
                    first = i
                last = i

            else:
                data, tc, tm_client = byte_dict[i]
                # check freshness
                time_diff = cur_time - tc
                if time_diff >= self.ttl: # not fresh
                    if not tm_server:
                        response = self.get_tmserver(filename)
                        if not response or response['type'] == 'error':
                            print('No such filename exists on the server.')
                            return
                        tm_server = response['content']
                    if tm_server == tm_client:
                        tc = cur_time
                        byte_dict[i] = (data, tc, tm_client)
                    else:
                        if first == None:
                            first = i
                        last = i

        if first != None:
            message = {
                'id': self.generate_request_id(),
                'type': 'read',
                'filename': filename,
                'offset': first,
                'num_bytes': last - first + 1
            }
            self.client_socket.send(marshaller.marshal(message))
            #  Waiting for response from the server
            # print("Waiting for response...")
            try:
                server_data, server = self.client_socket.recvfrom(65535)
                server_object = marshaller.unmarshal(server_data)
                if server_object['type'] == 'error':
                    print(server_object['content'])
                    return
                # print(f"Received message from server: {server_data}")
            except socket.timeout:
                print("No response received, server might be busy or offline. Try again.")
                return

            if not tm_server:
                response = self.get_tmserver(filename)
                if not response or response['type'] == 'error':
                    print('No such filename exists on the server.')
                    return
                tm_server = response['content']

            # generate string to print on client side
            for i in range(last - first + 1):
                byte_dict[i + first] = (server_object['content'][i], cur_time, tm_server)
        
        output = ''.join([byte_dict[i][0] for i in range(offset, offset + num_bytes)])
        print(f'Content of file {filename} at offset = {offset} for num_bytes = {num_bytes}: {output}')
        print(f"End cache: {self.cache}")
        
    def get_tmserver(self, filename):
        # Implementation to get the last modification time from the server
        message_object = {
            'type': 'get_tmserver',
            'filename': filename
        }
        self.client_socket.send(marshaller.marshal(message_object))

        # Waiting for response from the server
        # print("Waiting for response...")
        try:
            server_data, server = self.client_socket.recvfrom(65535)
            server_object = marshaller.unmarshal(server_data)
            if server_object['type'] == 'response':
                print(f"File {filename} was last modified at server time: {server_object['content']}")
            else:
                print(f"Error: {server_object['content']}")
            return server_object
        except socket.timeout:
            print("No response received, server might be busy or offline. Try again.")
            return None

