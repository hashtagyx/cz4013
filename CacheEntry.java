// CacheEntry.java
public class CacheEntry {
    private final byte data; // The cached data byte
    private final Double timestamp; // The client timestamp when the entry was cached
    private final Double tmServer; // The last modification time of the file on the server at the time the byte was cached

    /**
     * Constructs a CacheEntry object with the given data byte, timestamp, and server modification time.
     *
     * @param data     The data byte to be cached.
     * @param timestamp The timestamp when the entry was cached.
     * @param tmServer The last modification time of the file on the server.
     */
    public CacheEntry(byte data, Double timestamp, Double tmServer) {
        this.data = data;
        this.timestamp = timestamp;
        this.tmServer = tmServer;
    }

    public byte getData() {
        return data;
    }

    public Double getTimestamp() {
        return timestamp;
    }

    public Double getTmServer() {
        return tmServer;
    }

    // Returns a string representation of the CacheEntry object, helpful for printing CacheEntry objects
    @Override
    public String toString() {
        return "CacheEntry{" +
            "data=" + (char) data +
            ", timestamp=" + timestamp +
            ", tmServer=" + tmServer +
            '}';
    }
}