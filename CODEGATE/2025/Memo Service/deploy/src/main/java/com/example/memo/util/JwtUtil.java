package com.example.memo.util;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;

import java.util.*;

import javax.crypto.SecretKey;
import javax.servlet.ServletContext;

public class JwtUtil {

    private static SecretKey key;

    public static void init(ServletContext context) {
        String secret = context.getInitParameter("SECRET_KEY");

        if (secret == null || secret.length() < 32) {
            throw new IllegalArgumentException("SECRET_KEY ERROR");
        }

        key = Keys.hmacShaKeyFor(secret.getBytes());
    }

    public static String generateToken(String username, String id) {
        if (key == null) {
            throw new IllegalStateException("Missing key");
        }

        return Jwts.builder()
                .subject("user")
                .claim("username", username)
                .claim("id", id)
                .signWith(key)
                .compact();
    }

    public static List<Map<String, String>> verifyToken(String jwtString) {
        if (key == null) {
            throw new IllegalStateException("Missing key");
        }

        try {
            Claims claims = Jwts.parser()
                    .verifyWith(key)
                    .build()
                    .parseSignedClaims(jwtString)
                    .getPayload();

            List<Map<String, String>> claimsList = new ArrayList<>();

            for (String key : claims.keySet()) {
                Map<String, String> claim = new HashMap<>();
                claim.put("key", key);
                claim.put("value", (String) claims.get(key));
                claimsList.add(claim);
            }

            return claimsList;

        } catch (JwtException e) {
            return null;
        }
    }
}