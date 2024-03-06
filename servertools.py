import os
import time
import marshaller

current_directory = os.getcwd()
# Specify the path to the files folder
files_folder = os.path.join(current_directory, "files")

# Initialize an empty dictionary to store filenames
monitor_dictionary = {}  # key: filename, val: list of tuples [(client_address, end_time), ... ]

# Check if the files folder exists
if os.path.exists(files_folder) and os.path.isdir(files_folder):
    # List all files in the files folder
    file_names = os.listdir(files_folder)

    # Iterate over the file names
    for file_name in file_names:
        # Add each file name to the dictionary as a key
        monitor_dictionary[file_name] = []
    
    # {
    #     'a.txt': [(client_address, 8pm), (client_address, 7.30pm), (client_address, 7pm)], 
    #     'b.txt': []
    # }
    
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

def callback(filename):
    pass

def monitor(filename, interval, client_address):
    # If filename not in dictionary error handling 
    if filename not in monitor_dictionary:
        error = {
            'type': 'error',
            'content': 'File not found.'
        } 
        return marshaller.marshal(error)
    time_now = time.time()
    # Array of [(client_address, 8pm), (client_address, 7.30pm), (client_address, 7pm)]... 
    file_registry = monitor_dictionary[filename]
    file_registry.append((client_address, time_now + interval))
    monitor_dictionary[filename] = file_registry

    # Iterate over the file registry to remove expired entries
    for i in range(len(file_registry)):
        client_address, interval_expiry = file_registry[i]
        if interval_expiry < time_now:
            del file_registry[i]
    print('Monitor List', monitor_dictionary)
    print(f"Client {client_address} is now monitoring file {filename} for the next {interval} seconds.")
    return None

def delete(filename, offset, num_bytes):
    pass

def create(filename):
    pass
