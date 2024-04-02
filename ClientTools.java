// ClientTools.java
import java.io.*;
import java.net.*;
import java.util.*;

public class ClientTools {
    private final String serverIp;
    private final int serverPort;
    private final int ttl; // Time to live (in milliseconds) for cached data
    private final boolean responseLost; // Flag to simulate lost response scenario
    private final Map<String, Map<Integer, CacheEntry>> cache; // Cache data structure
    private final InetAddress serverAddress;
    private final DatagramSocket clientSocket;
    private final String clientIp;
    private final int clientPort;
    private int uniqueReqCount; // Counter for generating unique request IDs
    private int requestCount; // Counter for tracking the number of requests sent

    public ClientTools(String serverIp, int serverPort, int ttl, boolean responseLost) {
        this.serverIp = serverIp;
        this.serverPort = serverPort;
        this.ttl = ttl;
        this.responseLost = responseLost;
        this.cache = new HashMap<>();
        try {
            this.serverAddress = InetAddress.getByName(serverIp);
            this.clientSocket = new DatagramSocket();
            this.clientIp = InetAddress.getLocalHost().getHostAddress();
            this.clientPort = clientSocket.getLocalPort();
        } catch (IOException e) {
            throw new RuntimeException("Failed to initialize client socket", e);
        }
        this.uniqueReqCount = 0;
        this.requestCount = 0;
    }

    public void read(String filename, int offset, int numBytes) {
        System.out.println("Start cache: " + cache);
        Double timeNow = (double) System.currentTimeMillis(); // Current time for freshness checks
        Double tmServer = null; // Server's last modification time for the file

        // Initialize cache for the file if not present
        if (!cache.containsKey(filename)) {
            cache.put(filename, new HashMap<>());
        }

        Map<Integer, CacheEntry> byteDict = cache.get(filename); // Reference to the cache for the specific file
        Integer first = null, last = null; // Markers for the first and last byte positions needing update from server


        // Iterate through the requested byte range
        for (int i = offset; i < offset + numBytes; i++) {
            if (!byteDict.containsKey(i)) { // If byte i is not cached
                if (first == null) {
                    first = i; // Mark the start of the range to be fetched from the server
                }
                last = i; // Update the end of the range to be fetched from the server
            } else {
                // Check if cached byte is fresh
                CacheEntry cacheEntry = byteDict.get(i);
                Double timeDiff = timeNow - cacheEntry.getTimestamp();
                if (timeDiff >= ttl) { // If cached byte is stale
                    if (tmServer == null) { // Retrieve server's last modification time if not already done
                        Map<String, String> response = getTmServer(filename);
                        if (response.get("type").equals("error")) {
                            System.out.println("No such filename exists on the server.");
                            return;
                        }
                        tmServer = Double.parseDouble(response.get("content"));
                    }
                    if (tmServer == cacheEntry.getTmServer()) { // Refresh timestamp in cache since the file hasn't been modified
                        byteDict.put(i, new CacheEntry(cacheEntry.getData(), timeNow, tmServer));
                    } else { // Server's version is newer than cache's version
                        if (first == null) {
                            first = i; // Mark the start of the range to be fetched from the server
                        }
                        last = i; // Update the end of the range to be fetched from the server
                    }
                }
            }
        }

        // Request data from the server for uncached or stale bytes
        if (first != null) {
            Map<String, String> message = new HashMap<>();
            message.put("id", generateRequestId());
            message.put("type", "read");
            message.put("filename", filename);
            message.put("offset", String.valueOf(first));
            message.put("num_bytes", String.valueOf(last - first + 1));

            Map<String, String> serverObject = sendAndReceive(message);
            if (serverObject.get("type").equals("error")) { // No such file or offset invalid
                return;
            }

            // Retrieve server's last modification time if not already done
            if (tmServer == null) {
                Map<String, String> response = getTmServer(filename);
                if (response.get("type").equals("error")) {
                    System.out.println("No such filename exists on the server.");
                    return;
                }
                tmServer = Double.parseDouble(response.get("content"));
            }

            // Update cache for fetched bytes
            for (int i = 0; i <= last - first; i++) {
                byte data = (byte) serverObject.get("content").charAt(i);
                byteDict.put(i + first, new CacheEntry(data, timeNow, tmServer));
            }
        }

        // Generate client requested string for output
        StringBuilder output = new StringBuilder();
        for (int i = offset; i < offset + numBytes; i++) {
            output.append((char) byteDict.get(i).getData());
        }
        System.out.println("Content of file " + filename + " at offset = " + offset + " for num_bytes = " + numBytes + ": " + output.toString());
        System.out.println("End cache: " + cache);
    }

    public Map<String, String> getTmServer(String filename) {
        Map<String, String> message = new HashMap<>();
        message.put("id", generateRequestId());
        message.put("type", "get_tmserver");
        message.put("filename", filename);

        Map<String, String> serverObject = sendAndReceive(message);
        if (serverObject.get("type").equals("error")) { // No such file or offset invalid
            System.out.println(serverObject.get("content"));
        } else if (serverObject.get("type").equals("response")) { // Print last modified time
            System.out.println("File " + filename + " was last modified at server time: " + serverObject.get("content"));
        }


        return serverObject;
    }

    public void monitor(String filename, int interval) {
        System.out.println("Start cache: " + cache);
        Map<String, String> message = new HashMap<>();
        message.put("id", generateRequestId());
        message.put("type", "monitor");
        message.put("filename", filename);
        message.put("interval", String.valueOf(interval));

        Double endTime = (double) System.currentTimeMillis() + interval * 1000L;

        try {
            sendMessage(message); // Send the monitor request to the server
        } catch (IOException e) {
            e.printStackTrace();
        }

        try {
            System.out.println("Client is monitoring file " + filename + " for the next " + interval + " seconds.");
            // Set the socket timeout to the remaining time in the monitoring interval
            int remainingTime = (int) (endTime - System.currentTimeMillis());
            clientSocket.setSoTimeout(remainingTime);
            while ((double) System.currentTimeMillis() < endTime) {
                try {
                    byte[] buffer = new byte[65535];
                    DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
                    clientSocket.receive(packet); // Receive updates from the server
                    Map<String, String> messageObject = Marshaller.unmarshal(packet.getData(), packet.getOffset(), packet.getLength());
                    if (messageObject.get("type").equals("error")) { // No file by the filename found on server
                        System.out.println("Error: " + messageObject.get("content"));
                        return;
                    }
                    // Update cache with the latest file content from the server.
                    Double tmServer = Double.parseDouble(messageObject.get("tm_server"));
                    String content = messageObject.get("content");
                    Double tc = (double) System.currentTimeMillis();
                    cache.put(filename, new HashMap<>()); // Reset cache for the file.
                    for (int i = 0; i < content.length(); i++) { // Populate with new cache entries
                        cache.get(filename).put(i, new CacheEntry((byte) content.charAt(i), tc, tmServer));
                    }

                    // Generate string for output on command line
                    StringBuilder output = new StringBuilder();
                    for (CacheEntry entry : cache.get(filename).values()) {
                        output.append((char) entry.getData());
                    }
                    System.out.println("Callback for file " + filename + " triggered. New file content: " + output.toString());

                } catch (SocketTimeoutException e) {
                    // Continue the loop if socket times out
                }
            }
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }

    public void insert(String filename, int offset, String content) {
        System.out.println("Old cache before insert: " + cache);
        Map<String, String> message = new HashMap<>();
        message.put("id", generateRequestId());
        message.put("type", "insert");
        message.put("filename", filename);
        message.put("offset", String.valueOf(offset));
        message.put("content", content);

        Map<String, String> serverObject = sendAndReceive(message);
        if (serverObject.get("type").equals("error")) { // No such file or offset invalid
            return;
        }

        // serverObject['type'] == 'response'
        Double timeNow = (double) System.currentTimeMillis(); // Current time for cache update
        Double tmServer = Double.parseDouble(serverObject.get("tm_server")); // Last modification time from server

        // Initialize file cache if not present
        if (!cache.containsKey(filename)) {
            cache.put(filename, new HashMap<>());
        }

        Map<Integer, CacheEntry> fileCache = cache.get(filename);
        // Sort the items of fileCache in descending/reverse order by keys (byte positions)
        List<Map.Entry<Integer, CacheEntry>> sortedEntries = new ArrayList<>(fileCache.entrySet());
        sortedEntries.sort(Map.Entry.comparingByKey(Comparator.reverseOrder()));

        // Calculate the length of the content to be inserted
        int LENGTH = content.length();
        Map<Integer, CacheEntry> newFileCache = new HashMap<>();


        // Update cache: shift existing bytes to the right to make space for new content (iterating through bytes in descending/reverse order)
        for (Map.Entry<Integer, CacheEntry> entry : sortedEntries) {
            int byteNum = entry.getKey();
            if (byteNum >= offset) {
                newFileCache.put(byteNum + LENGTH, entry.getValue()); // Shift bytes to the right
            } else if (byteNum < offset) {
                newFileCache.put(byteNum, entry.getValue()); // Keep bytes before offset unchanged
            }
        }

        // Insert new content into the cache at the specified offset
        for (int byteNum = offset; byteNum < offset + LENGTH; byteNum++) {
            int idx = byteNum - offset;
            newFileCache.put(byteNum, new CacheEntry((byte) content.charAt(idx), timeNow, tmServer));
        }

        // Update the file cache with the new changes
        cache.put(filename, newFileCache);
        System.out.println("New cache after insert: " + cache);
        System.out.println("Inserted " + LENGTH + " bytes at position " + offset + " of " + filename + ".");
    }

    public void delete(String filename, int offset, int numBytes) {
        System.out.println("Old cache before delete: " + cache);
        Map<String, String> message = new HashMap<>();
        message.put("id", generateRequestId());
        message.put("type", "delete");
        message.put("filename", filename);
        message.put("offset", String.valueOf(offset));
        message.put("num_bytes", String.valueOf(numBytes));

        Map<String, String> serverObject = sendAndReceive(message);

        if (serverObject.get("type").equals("error")) { // No such file or offset invalid
            return;
        }

        // Ensure cache exists for the file; if not, initialize it
        if (!cache.containsKey(filename)) {
            cache.put(filename, new HashMap<>());
        }

        Map<Integer, CacheEntry> fileCache = cache.get(filename);
        // Sort the items of file_cache in ascending order by keys (byte positions)
        List<Map.Entry<Integer, CacheEntry>> sortedEntries = new ArrayList<>(fileCache.entrySet());
        sortedEntries.sort(Map.Entry.comparingByKey());

        int LENGTH = numBytes; // Length of content to be deleted
        Map<Integer, CacheEntry> newFileCache = new HashMap<>(); // Temporary cache to hold updated values

        for (Map.Entry<Integer, CacheEntry> entry : sortedEntries) {
            int byteNum = entry.getKey();
            // Keep bytes before deletion offset unchanged
            if (byteNum < offset) {
                newFileCache.put(byteNum, entry.getValue());
            }
            // Shift bytes after the deleted section to the left
            else if (byteNum >= offset + LENGTH) {
                newFileCache.put(byteNum - LENGTH, entry.getValue());
            }
        }

        // Replace the old cache with the updated cache reflecting deletions
        cache.put(filename, newFileCache);
        System.out.println("New cache after delete: " + cache);
        System.out.println("Deleted " + LENGTH + " bytes at position " + offset + " of " + filename + ".");
    }

    private Map<String, String> sendAndReceive(Map<String, String> message) {
        try {
            sendMessage(message);
            requestCount++;
            if (responseLost) {
                // Simulate a lost response scenario
                byte[] buffer = new byte[65535];
                DatagramPacket dummyPacket = new DatagramPacket(buffer, buffer.length);
                clientSocket.receive(dummyPacket); // Dummy receive to simulate waiting for a lost response
                sendMessage(message);
                requestCount++;
            }


            System.out.println("Request Count: " + requestCount);
            byte[] buffer = new byte[65535];
            DatagramPacket packet = new DatagramPacket(buffer, buffer.length);
            clientSocket.receive(packet);
            Map<String, String> serverObject = Marshaller.unmarshal(packet.getData(), packet.getOffset(), packet.getLength());
            if (serverObject.get("type").equals("error")) {
                System.out.println(serverObject.get("content"));
            }
            return serverObject;
        } catch (SocketTimeoutException e) {
            System.out.println("No response received, server might be busy or offline. Try again.");
            return Map.of("type", "error", "content", "No response received, server might be busy or offline. Try again.");
        } catch (IOException e) {
            e.printStackTrace();
            return Map.of("type", "error", "content", "An error occurred while sending or receiving data.");
        }
    }

    private void sendMessage(Map<String, String> message) throws IOException {
        byte[] data = Marshaller.marshal(message);
        DatagramPacket packet = new DatagramPacket(data, data.length, serverAddress, serverPort);
        clientSocket.send(packet);
    }

    private String generateRequestId() {
        uniqueReqCount++;
        return clientIp + ":" + clientPort + ":" + uniqueReqCount; // Generate a unique request ID
    }

    public void closeSocket() {
        clientSocket.close();
    }
}
