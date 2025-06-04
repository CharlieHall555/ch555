package com.example.nfcscannerapp;
import java.util.regex.*;
import java.security.MessageDigest;

public class Utillities {

    public static boolean isValidEndPoint(String endpoint){
        String pattern = "^(https?://)((25[0-5]|2[0-4]\\d|1\\d{2}|[1-9]?\\d)\\.){3}"
                + "(25[0-5]|2[0-4]\\d|1\\d{2}|[1-9]?\\d):"
                + "\\d{1,5}/credentials$";

        endpoint = endpoint.trim();
        if (endpoint.matches(pattern)){
            return true;
        }else{
            return false;
        }


    }

    public static boolean isValidCredentials(String scannedText){
        String pattern = "\\{\\s*\"elector_id\"\\s*:\\s*\"[^\"]+\"\\s*,\\s*\"public_key\"\\s*:\\s*\"[^\"]+\"\\s*,\\s*\"private_key\"\\s*:\\s*\"[^\"]+\"\\s*\\}";
        scannedText = scannedText.trim();
        if (scannedText.matches(pattern)){
            return true;
        }else{
            return false;
        }


    }

    public static String sha256First4(String input) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] hash = digest.digest(input.getBytes("UTF-8"));
        StringBuilder hex = new StringBuilder();
        for (byte b : hash) {
            hex.append(String.format("%02x", b));
        }
        return hex.substring(0, 4);
    }

}
