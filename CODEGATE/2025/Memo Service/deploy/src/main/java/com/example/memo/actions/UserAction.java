package com.example.memo.actions;

import java.sql.SQLException;
import java.util.Map;

import com.example.memo.dao.UserDAO;
import com.example.memo.util.JwtUtil;
import com.opensymphony.xwork2.ActionSupport;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletResponse;
import org.apache.struts2.ServletActionContext;

@SuppressWarnings("deprecation")
public class UserAction extends ActionSupport {

    private String username;
    private String password;
    private String message;

    public void setUsername(String username) {
        this.username = username;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public String getMessage() {
        return message;
    }

    public boolean validateParam() {
        return username != null && password != null;
    }

    private void setCookie(String key, String value, int ttl) {
        HttpServletResponse response = ServletActionContext.getResponse();
        Cookie cookie = new Cookie(key, value);
        cookie.setMaxAge(ttl);
        cookie.setPath("/");
        response.addCookie(cookie);
    }

    public String login() throws SQLException {
        if (!validateParam()) {
            return INPUT;
        }

        UserDAO dao = new UserDAO();
        Map<String, Object> user = dao.getUser(username);

        if (user == null || !user.get("password").equals(dao.sha256(password))) {
            message = "Login fail";
            return ERROR;
        }

        setCookie("token", JwtUtil.generateToken(username, Integer.toString((Integer) user.get("id"))), 3600);
        return SUCCESS;
    }

    public String register() throws SQLException {
        if (!validateParam()) {
            return INPUT;
        }

        if (this.username.length() < 10 && this.password.length() < 10) {
            message = "Username or password is too short";
            return ERROR;
        }

        UserDAO dao = new UserDAO();
        Map<String, Object> user = dao.getUser(username);

        if (user != null) {
            message = "User already exists";
            return ERROR;
        }

        return dao.addUser(username, password) ? SUCCESS : ERROR;
    }

    public String logout() {
        setCookie("token", "", 0);
        return SUCCESS;
    }
}