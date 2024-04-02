// Client.java
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.regex.Pattern;

public class Client {
    public static void main(String[] args) {
        int ttl = 100 * 1000; // Default TTL value (100 seconds)
        boolean responseLost = false; // Default value for handling lost responses

        // Parse command-line arguments
        if (args.length > 0) {
            for (String arg : args) {
                if (arg.startsWith("--ttl=")) {
                    ttl = Integer.parseInt(arg.substring(6)) * 1000; // TTL value in milliseconds
                } else if (arg.equals("--response_lost")) {
                    responseLost = true;
                }
            }
        }

        String ipAddress = "192.168.0.102";
        ClientTools clientTools = new ClientTools(ipAddress, 2222, ttl, responseLost);
        BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));

        while (true) {
            printMenu(); // Print the menu of options
            String choice = getValidInput(reader, "Enter your choice: ", "^[0-5]$"); // Get user's choice

            if (choice.equals("0")) { // Exit the program
                System.out.println("Exiting client.");
                clientTools.closeSocket();
                break;
            }

            switch (choice) {
                case "1": // Read file
                    String filename = getValidInput(reader, "Enter the filename to read: ", "^[\\w.]+$");
                    int offset = getPositiveInt(reader, "Enter the offset: ");
                    int numBytes = getPositiveInt(reader, "Enter the number of bytes to read: ");
                    clientTools.read(filename, offset, numBytes);
                    break;
                case "2": // Insert content into file
                    filename = getValidInput(reader, "Enter the filename to insert content into: ", "^[\\w.]+$");
                    offset = getPositiveInt(reader, "Enter the offset: ");
                    String content = getValidInput(reader, "Enter the content to insert: ", "^[\\w.]+$");
                    clientTools.insert(filename, offset, content);
                    break;
                case "3": // Register for updates
                    filename = getValidInput(reader, "Enter the filename to monitor: ", "^[\\w.]+$");
                    int interval = getPositiveInt(reader, "Enter the monitor interval: ");
                    clientTools.monitor(filename, interval);
                    break;
                case "4": // Delete bytes from file
                    filename = getValidInput(reader, "Enter the filename to delete bytes from: ", "^[\\w.]+$");
                    offset = getPositiveInt(reader, "Enter the offset: ");
                    numBytes = getPositiveInt(reader, "Enter the number of bytes to delete: ");
                    clientTools.delete(filename, offset, numBytes);
                    break;
                case "5": // Check last modified time of a file
                    filename = getValidInput(reader, "Enter the filename to check the last modified time at the server: ", "^[\\w.]+$");
                    clientTools.getTmServer(filename);
                    break;
            }
        }
    }

    private static void printMenu() {
        System.out.println("\nSelect an option:");
        System.out.println("1: Read File");
        System.out.println("2: Insert content into file");
        System.out.println("3: Register for updates");
        System.out.println("4: Delete bytes from file");
        System.out.println("5: Check last modified time of a file");
        System.out.println("0: Exit");
    }

    private static String getValidInput(BufferedReader reader, String prompt, String regex) {
        String input;
        Pattern pattern = Pattern.compile(regex); // Compile the regular expression pattern

        while (true) {
            System.out.print(prompt);
            try {
                input = reader.readLine();
                if (pattern.matcher(input).matches()) { // Check if the input matches the pattern
                    return input;
                } else {
                    System.out.println("Invalid input. Please try again.");
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private static int getPositiveInt(BufferedReader reader, String prompt) {
        while (true) {
            String input = getValidInput(reader, prompt, "\\d+"); // Get a valid input that matches the digit pattern
            try {
                int value = Integer.parseInt(input);
                if (value >= 0) { // Check if the value is non-negative
                    return value;
                } else {
                    System.out.println("Please enter a non-negative number.");
                }
            } catch (NumberFormatException e) {
                System.out.println("Invalid input. Please enter a number.");
            }
        }
    }
}