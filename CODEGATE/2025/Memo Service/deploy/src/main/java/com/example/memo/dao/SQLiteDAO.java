package com.example.memo.dao;

import java.sql.Connection;
import java.sql.DriverManager;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class SQLiteDAO {
    private static final String URL = "jdbc:sqlite:/tmp/database.db";

    public Connection connect() {
        try {
            Class.forName("org.sqlite.JDBC");
            return DriverManager.getConnection(URL);
        } catch (Exception e) {
            e.printStackTrace();
            return null;
        }
    }

    public String sha256(String str) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(str.getBytes());
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                hexString.append(String.format("%02x", b));
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
            return null;
        }
    }
}
