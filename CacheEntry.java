// CacheEntry.java
public class CacheEntry {
    private final byte data;
    private final Double timestamp;
    private final Double tmServer;

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
}