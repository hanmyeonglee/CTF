package com.example.memo.filter;

import java.util.*;
import javax.servlet.*;
import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import com.example.memo.util.JwtUtil;
import java.io.IOException;

public class AuthFilter implements Filter {

    @Override
    public void init(FilterConfig filterConfig) {
    }

    @Override
    public void doFilter(ServletRequest request, ServletResponse response, FilterChain chain)
            throws IOException, ServletException {
        HttpServletRequest req = (HttpServletRequest) request;
        HttpServletResponse res = (HttpServletResponse) response;
        String uri = req.getRequestURI();

        Cookie[] cookies = req.getCookies();
        String token = "dummy";

        if (cookies != null) {
            for (Cookie cookie : cookies) {
                if ("token".equals(cookie.getName())) {
                    token = cookie.getValue();
                    break;
                }
            }
        }

        List<Map<String, String>> claimsList = JwtUtil.verifyToken(token);

        if (claimsList == null) {
            res.sendRedirect(req.getContextPath() + "/user/login.action");
            return;
        }

        for (Map<String, String> claim : claimsList) {
            req.setAttribute(claim.get("key"), (String) claim.get("value"));
        }

        if (uri.startsWith("/download") && !req.getAttribute("id").equals("1")) {
            res.sendRedirect("/user/login.action");
            return;
        }

        chain.doFilter(request, response);
    }

    @Override
    public void destroy() {
    }
}