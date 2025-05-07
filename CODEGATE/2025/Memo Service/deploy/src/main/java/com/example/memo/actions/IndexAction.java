package com.example.memo.actions;
import com.opensymphony.xwork2.ActionSupport;
import javax.servlet.http.HttpServletRequest;

@SuppressWarnings("deprecation")
public class IndexAction extends ActionSupport {

    private HttpServletRequest request;
    private String message;

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
    
    public String execute() {
        return SUCCESS;
    }
}
