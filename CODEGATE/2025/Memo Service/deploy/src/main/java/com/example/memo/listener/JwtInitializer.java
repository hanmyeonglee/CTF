package com.example.memo.listener;

import com.example.memo.util.JwtUtil;

import javax.servlet.ServletContext;
import javax.servlet.ServletContextEvent;
import javax.servlet.ServletContextListener;
import javax.servlet.annotation.WebListener;

@WebListener
public class JwtInitializer implements ServletContextListener {

    @Override
    public void contextInitialized(ServletContextEvent sce) {
        ServletContext context = sce.getServletContext();
        JwtUtil.init(context);
    }

    @Override
    public void contextDestroyed(ServletContextEvent sce) {
    }
}