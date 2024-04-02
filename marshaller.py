def marshal(object):
    # Initialize an empty list to hold the string representations of the key/value pairs.
    string_array = []

    # Iterate over the key/value pairs in the dictionary.
    for key, value in object.items():
        # For each pair, convert the key and value to strings (if they aren't already),
        # join them with a '/', and append the result to 'string_array'.
        string_array.append(str(key) + '/' + str(value))
    
    # Join all the elements in 'string_array' with a '|', resulting in a single string
    # where each key/value pair is separated by '/', and each pair is delimited by '|'.
    string = '|'.join(string_array)

    # Encode the final string into bytes using the default encoding (utf-8) and return it.
    return string.encode('utf-8')

def unmarshal(received: bytes) -> object:
    # Decode the bytes argument 'received' into a UTF-8 string.
    received = received.decode('utf-8')

    # Split the decoded string by '|' to create a list, where each element
    # is expected to be a key/value pair joined by '/'.
    received_arr = received.split('|')

    # Initialize an empty dictionary to hold the key/value pairs.
    obj = {}

    # Iterate through each key/value pair in the list 'received_arr'.
    for pair in received_arr:
        # Split each pair by '/' to separate the key and value.
        key, val = pair.split('/')

        # Assign the value to its corresponding key in the 'obj' dictionary.
        obj[key] = val

    # Return the dictionary containing all the key/value pairs.
    return obj
