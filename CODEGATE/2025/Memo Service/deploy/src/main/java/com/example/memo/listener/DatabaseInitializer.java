package com.example.memo.listener;

import javax.servlet.ServletContext;
import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.sql.*;
import java.util.stream.Collectors;

@WebListener
public class DatabaseInitializer implements ServletContextListener {

    private static final String DB_URL = "jdbc:sqlite:/tmp/database.db";

    public static void initDatabase() {
        try (Connection conn = DriverManager.getConnection(DB_URL)) {

            // 이미 users 테이블이 있는지 확인
            if (tableExists(conn, "users")) {
                System.out.println("⚠️  Database already initialized. Skipping init.sql.");
                return;
            }

            // init.sql 읽기
            InputStream inputStream = DatabaseInitializer.class.getClassLoader().getResourceAsStream("init.sql");
            if (inputStream == null) {
                throw new RuntimeException("Not found init.sql");
            }

            String sql = new BufferedReader(new InputStreamReader(inputStream))
                    .lines().collect(Collectors.joining("\n"));

            try (Statement stmt = conn.createStatement()) {
                stmt.executeUpdate(sql);
                System.out.println("✅ Database Initialized!");
            }

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Database init fail", e);
        }
    }

    private static boolean tableExists(Connection conn, String tableName) {
        try (ResultSet rs = conn.getMetaData().getTables(null, null, tableName, null)) {
            return rs.next();
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        initDatabase();
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
    }
}
