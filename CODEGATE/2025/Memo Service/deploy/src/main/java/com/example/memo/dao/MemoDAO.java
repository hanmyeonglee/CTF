package com.example.memo.dao;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MemoDAO extends SQLiteDAO {

    public List<Map<String, String>> getMemos(int owner) {
        String sql = "SELECT id, title, content FROM memos WHERE owner = ?";
        List<Map<String, String>> memos = new ArrayList<>();

        try (Connection conn = connect();
                PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setInt(1, owner);

            try (ResultSet rs = pstmt.executeQuery()) {
                while (rs.next()) {
                    Map<String, String> memo = new HashMap<>();
                    memo.put("id", rs.getString("id"));
                    memo.put("title", rs.getString("title"));
                    memo.put("content", rs.getString("content"));
                    memos.add(memo);
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return memos;
    }

    public Map<String, String> getMemo(Integer owner, Integer id) {
        String sql = "SELECT id, title, content, owner FROM memos WHERE owner = ? AND id = ?";
        Map<String, String> memo = new HashMap<>();

        try (Connection conn = connect();
                PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setInt(1, owner);
            pstmt.setInt(2, id);

            try (ResultSet rs = pstmt.executeQuery()) {
                if (rs.next()) {
                    memo.put("id", rs.getString("id"));
                    memo.put("title", rs.getString("title"));
                    memo.put("content", rs.getString("content"));
                    memo.put("owner", rs.getString("owner"));
                }
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }

        return memo;
    }

    public boolean addMemo(Integer owner, String title, String content) {
        String sql = "INSERT INTO memos (owner, title, content) VALUES (?, ?, ?)";

        try (Connection conn = connect();
                PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setInt(1, owner);
            pstmt.setString(2, title);
            pstmt.setString(3, content);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean delMemo(Integer id) {
        String sql = "DELETE FROM memos WHERE id = ?";

        try (Connection conn = connect();
                PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setInt(1, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }

    public boolean editMemo(Integer id, String title, String content) {
        String sql = "UPDATE memos SET title = ?, content = ? WHERE id = ?";

        try (Connection conn = connect();
                PreparedStatement pstmt = conn.prepareStatement(sql)) {

            pstmt.setString(1, title);
            pstmt.setString(2, content);
            pstmt.setInt(3, id);
            return pstmt.executeUpdate() > 0;
        } catch (SQLException e) {
            e.printStackTrace();
            return false;
        }
    }
}