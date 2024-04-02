import os
import time
import marshaller

current_directory = os.getcwd()
# Specify the path to the files folder
files_folder = os.path.join(current_directory, "files")

# Initialize an empty dictionary to store filenames
monitor_dictionary = {}  # key: filename, val: list of tuples e.g. [(client_address, end_time), ... ]
# pass in as an argument into the function that creates new files 

# Check if the files folder exists
if os.path.exists(files_folder) and os.path.isdir(files_folder):
    # List all files in the files folder
    file_names = os.listdir(files_folder)

    # Iterate over the file names
    for file_name in file_names:
        # Add each file name to the dictionary as a key
        monitor_dictionary[file_name] = []
    
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
        # Return object of type 'error'
        read_object['type'] = 'error'
        read_object['content'] = e
        return marshaller.marshal(read_object)

def get_tmserver(filename): # idempotent 
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
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, "files", filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return { 'type': 'error', 'content': 'File does not exist.' }

    # Open the file to read its content
    with open(file_path, 'r+') as file:
        file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
        file_length = file.tell()  # Get the total length of the file

        # Check if the offset is within the file's length
        if offset > file_length:
            return { 'type': 'error', 'content': 'Offset is beyond the end of the file.' }

        # If the offset is within bounds, proceed with the insertion
        file.seek(offset)  # Move the cursor to the specified offset
        remaining_content = file.read()  # Read the content from the offset to the end
        file.seek(offset)  # Move back the cursor to the offset
        file.write(content + remaining_content)  # Write the new content and then the remaining content

    # After the insertion, get the timestamp
    timestamp = os.path.getmtime(file_path)

    return { 'type': 'response', 'tm_server': timestamp }

def callback(filename):
    # Check if filename is in monitor dictionary
    if filename not in monitor_dictionary:
        callback_obj = {
                'type': 'error',
                'content': 'File Not Found',
            }
        return (callback_obj, [])
    
    current_directory = os.getcwd()

    # Specify the path to the file
    file_path = os.path.join(current_directory, "files", filename)

    # Read the entire file content as a string
    with open(file_path, 'r') as file:
        file_content = file.read()

    # Get the modification time of the file
    tm_server = os.path.getmtime(file_path)
    time_now = time.time()
    new_list = []
    for client_address, interval_expiry in monitor_dictionary[filename]:
        # Check validity of the monitoring client
        if time_now <= interval_expiry:
            new_list.append((client_address, interval_expiry))

    # Update the monitor dictionary with the valid monitoring clients
    monitor_dictionary[filename] = new_list

    # If no valid monitoring clients, return error object
    if len(new_list) == 0:
        no_clients_callback_obj = {
            'type': 'error',
            'content': 'No clients to callback.',
        }
        return (no_clients_callback_obj, [])
    
    callback_obj = {
        'type': 'response',
        'content': file_content,
        'tm_server': tm_server
    }
    client_callback_list = [client_address for client_address, _ in new_list]
    return (callback_obj, client_callback_list)

def monitor(filename, interval, client_address):
    # Check if filename is in monitor dictionary
    if filename not in monitor_dictionary:
        error = {
            'type': 'error',
            'content': 'File not found.'
        } 
        return marshaller.marshal(error)
    time_now = time.time()

    # Add new monitoring client
    monitor_dictionary[filename].append((client_address, time_now + interval))
    print(f'Old Monitor List after adding: {monitor_dictionary}')
    
    new_list = []
    # Iterate over the file registry to remove expired entries
    for i in range(len(monitor_dictionary[filename])):
        client_address, interval_expiry = monitor_dictionary[filename][i]
        # Only add monitoring clients who are still valid
        if interval_expiry >= time_now:
            new_list.append((client_address, interval_expiry))

    # Update monitor dictionary to only have valid clients
    monitor_dictionary[filename] = new_list
    print('New Monitor List', monitor_dictionary)
    print(f"Client {client_address} is now monitoring file {filename} for the next {interval} seconds.")
    return None

def delete(filename, offset, num_bytes): # non-idempotent
    current_directory = os.getcwd()
    file_path = os.path.join(current_directory, "files", filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        return { 'type': 'error', 'content': 'File does not exist.' }

    # Open the file to read and update its content
    with open(file_path, 'r+') as file:
        file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
        file_length = file.tell()  # Get the total length of the file

        # Check if the offset is within the file's length
        if offset >= file_length:
            return { 'type': 'error', 'content': 'Offset is beyond the end of the file.' }

        # Check if the deletion range is within the file's content
        if offset + num_bytes > file_length:
            return { 'type': 'error', 'content': 'Offset + num_bytes is beyond the end of the file.' }

        file.seek(0)  # Move back the cursor to the beginning of the file
        file_content = file.read()  # Read the entire file content

        # Construct new content without the specified range
        new_content = file_content[:offset] + file_content[offset + num_bytes:]

        # Truncate the file and write the new content
        file.seek(0)
        file.truncate()
        file.write(new_content)

    return { 'type': 'response' }
