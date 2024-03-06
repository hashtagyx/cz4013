import os
import time
import marshaller

def read(filename, offset, num_bytes):
    
    read_object = {}
    
    try:
        # Get the current directory path
        current_directory = os.getcwd()

        # Specify the path to the file
        file_path = os.path.join(current_directory, "files", filename)

        # Initialize an empty string to store the extracted text
        read_bytes = ""

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError("Error: File not found")

        # Get the size of the file
        file_size = os.path.getsize(file_path)
        print(file_size)

        # Convert offset and num_bytes to integers
        offset = int(offset)
        num_bytes = int(num_bytes)

        # Check if offset is within the file size
        if offset >= file_size:
            raise ValueError("Error: Offset exceeds file length")

        elif offset + num_bytes > file_size:
            raise ValueError("Error: Offset + number of bytes exceeds file length")

        # Open the text file in read mode
        with open(file_path, "r") as file:
            # Set the file pointer to the specified offset
            file.seek(offset)

            # Read the specified number of bytes and store them as text
            read_bytes = file.read(num_bytes)
            read_object['type'] = 'response'
            read_object['content'] = read_bytes

        return marshaller.marshal(read_object)

    except Exception as e:
        read_object['type'] = 'error'
        read_object['content'] = e
        return marshaller.marshal(read_object)

def get_tmserver(filename):
    try:
        current_directory = os.getcwd()

        # Specify the path to the file
        file_path = os.path.join(current_directory, "files", filename)

        # Get the last modification time of the file
        timestamp = os.path.getmtime(file_path)

        res = {
            'type': 'response',
            'content': timestamp
        }
        return marshaller.marshal(res)
    except FileNotFoundError:
        res = {
            'type': 'error',
            'content': 'File not found.'
        }
        return marshaller.marshal(res)

def insert(filename, offset, content):
    pass

def monitor(filename, interval, client_address):
    pass

def delete(filename, offset, num_bytes):
    pass

def create(filename):
    pass
