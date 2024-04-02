// CacheEntry.java
public class CacheEntry {
    private final byte data;
    private final long timestamp;
    private final long tmServer;

    public CacheEntry(byte data, long timestamp, long tmServer) {
        this.data = data;
        this.timestamp = timestamp;
        this.tmServer = tmServer;
    }

    public byte getData() {
        return data;
    }

    public long getTimestamp() {
        return timestamp;
    }

    public long getTmServer() {
        return tmServer;
    }
}