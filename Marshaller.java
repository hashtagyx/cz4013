
// Marshaller.java
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.HashMap;

public class Marshaller {
    public static byte[] marshal(Map<String, String> object) {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> entry : object.entrySet()) {
            sb.append(entry.getKey()).append('/').append(entry.getValue()).append('|');
        }
        return sb.toString().getBytes(StandardCharsets.UTF_8);
    }

    public static Map<String, String> unmarshal(byte[] received, int offset, int length) {
        Map<String, String> obj = new HashMap<>();
        String receivedString = new String(received, offset, length, StandardCharsets.UTF_8);
        String[] pairs = receivedString.split("\\|");
        for (String pair : pairs) {
            if (!pair.isEmpty()) {
                String[] keyValue = pair.split("/");
                obj.put(keyValue[0], keyValue[1]);
            }
        }
        return obj;
    }
}
