## CZ4013 Project: Design and Implementation of A System for Remote File Access

This repository contains the implementation of a system designed for remote file access, as part of CZ4013 Distributed Systems. The system utilizes UDP as the transport protocol, providing hands-on experience in constructing client-server applications.

## Getting Started

### Requirements
- Ensure that the client and server are on the same LAN and obtain the server's IP address.
- Python environment for running Python scripts.
- Java SDK for compiling and running Java applications.

### Server

- Launch the server application with:
  ```bash
  python server.py
  ```
  Optional flag --at_most_once can be used to invoke at most once invocation semantics.

### Client (Java)

- Ensure the server's IP address is correctly set in Client.java (line 30).
- Compile the Java files:
  ```bash
  javac *.java
  ```
- Launch the client application:
  ```bash
  java Client
  ```
  Optional flags:
  - --response_lost to simulate lost responses from the server.
  - --ttl <interval in seconds> to set the freshness interval for cache entries.

### Client (Python)

- Ensure the server's IP address is correctly set in client.py (line 8).
- Launch the Python client with the same optional flags as the Java client:
  ```
  python client.py
  ```

### Default Configuration
- Time to Live (TTL) for cache entries: 100 seconds.
- The client does not simulate lost responses from the server by default.
- The server runs with at least once invocation semantics by default.

### Components
The repository includes the following components:

- `CacheEntry.java`: Java class defining cache entries used on the client side.
- `Client.java`: Main client application in Java, to be launched on the client PC.
- `ClientTools.java`: Utility tools for facilitating operations in the Java client application.
- `Marshaller.java`: Handles marshalling and unmarshalling of messages between client and server (Java version).
- `marshaller.py`: Python version of the marshaller for message processing.
- `servertools.py`: Utility tools for the server application.
- `server.py`: Server application to be launched on the server machine.
- `client.py`: Main client application in Python, to be launched on the client PC.
- `clienttools.py`: Python version of utility tools for the client application.
- `./files/test.txt`: Text file that the distributed program edits.
