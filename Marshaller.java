// Marshaller.java
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.HashMap;

public class Marshaller {
    /**
     * Marshals a Map<String, String> object into a byte array.
     * The key-value pairs are encoded as "key/value" strings separated by "|" delimiter.
     *
     * @param object The Map<String, String> object to be marshaled.
     * @return The marshaled byte array representation of the object.
     */
    public static byte[] marshal(Map<String, String> object) {
        StringBuilder sb = new StringBuilder();
        boolean first = true; // Flag to check if it's the first iteration
        // Iterate over the entries in the Map
        for (Map.Entry<String, String> entry : object.entrySet()) {
            if (first) {
                first = false; // It's no longer the first iteration
            } else {
                sb.append('|'); // Append delimiter before each entry except the first
            }
            sb.append(entry.getKey()).append('/').append(entry.getValue()); // Append "key/value" string
        }
        // Convert the StringBuilder to a byte array using UTF-8 encoding
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }
    /**
     * Unmarshals a byte array into a Map<String, String> object.
     * The byte array is expected to be in the format "key/value|key/value|...",
     * where "|" is the delimiter separating key-value pairs.
     *
     * @param received The byte array to be unmarshaled.
     * @param offset   The offset in the byte array where the data starts.
     * @param length   The length of the data in the byte array.
     * @return The unmarshaled Map<String, String> object.
     */
    public static Map<String, String> unmarshal(byte[] received, int offset, int length) {
        Map<String, String> obj = new HashMap<>();
        String receivedString = new String(received, offset, length, StandardCharsets.UTF_8); // Convert byte array to string
        // Split the string into key-value pairs using the "|" delimiter
        String[] pairs = receivedString.split("\\|");
        for (String pair : pairs) {
            if (!pair.isEmpty()) {
                String[] keyValue = pair.split("/"); // Split the pair into key and value
                obj.put(keyValue[0], keyValue[1]); // Add the key-value pair to the Map
            }
        }
        return obj;
    }
}
