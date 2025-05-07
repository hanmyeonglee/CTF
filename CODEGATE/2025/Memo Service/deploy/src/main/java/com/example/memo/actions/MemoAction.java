package com.example.memo.actions;

import java.sql.SQLException;
import java.util.List;
import java.util.Map;
import java.io.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.example.memo.dao.MemoDAO;
import com.opensymphony.xwork2.ActionSupport;
import org.owasp.html.HtmlPolicyBuilder;
import org.owasp.html.PolicyFactory;
import org.apache.struts2.interceptor.ServletRequestAware;
import org.apache.struts2.interceptor.ServletResponseAware;

@SuppressWarnings("deprecation")
public class MemoAction extends ActionSupport implements ServletRequestAware, ServletResponseAware {

    private HttpServletRequest request;
    private HttpServletResponse response;
    private List<Map<String, String>> memos;
    private Map<String, String> memo;
    private Integer id;
    private Integer owner;
    private String title;
    private String content;
    private String username;
    private String message = "Error";
    private String CACHE_DIR = "/download/";
    private String CACHE_PATH = "";

    @Override
    public void setServletRequest(HttpServletRequest request) {
        this.request = request;
    }

    @Override
    public void setServletResponse(HttpServletResponse response) {
        this.response = response;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public void setOwner(Integer id) {
        this.owner = id;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public void setContent(String content) {
        this.content = content;
    }

    public Integer getId() {
        return id;
    }

    public Integer getOwner() {
        return owner;
    }

    public List<Map<String, String>> getMemos() {
        return memos;
    }

    public Map<String, String> getMemo() {
        return memo;
    }

    public String getMessage() {
        return message;
    }

    public String getUsername() {
        return username;
    }

    public String getCachepath() {
        return CACHE_PATH;
    }

    public boolean validateParam() {
        return title != null && content != null;
    }

    public String safeXSS(String str) {
        PolicyFactory policy = new HtmlPolicyBuilder()
                .allowElements("script")
                .allowTextIn("script")
                .toFactory();

        str = str.replaceAll("\"", "&quot;").replaceAll("\\\\", "\\\\\\\\");
        return policy.sanitize("<script>content = \"" + str + "\"</script>");
    }

    public String list() throws SQLException {
        Integer id = Integer.parseInt((String) request.getAttribute("id"));
        this.username = (String) request.getAttribute("username");
        MemoDAO dao = new MemoDAO();
        memos = dao.getMemos(id);
        return SUCCESS;
    }

    public String read() throws SQLException {
        Integer id = Integer.parseInt((String) request.getAttribute("id"));
        MemoDAO dao = new MemoDAO();

        memo = dao.getMemo(id, this.id);

        if (memo.isEmpty()) {
            message = "Not found";
            return ERROR;
        }

        memo.put("content", safeXSS(memo.get("content")));
        return SUCCESS;
    }

    public String write() throws SQLException {
        Integer id = Integer.parseInt((String) request.getAttribute("id"));

        if (id == 1) {
            this.message = "Admin cannot write posts";
            return ERROR;
        }

        if (!validateParam()) {
            return INPUT;
        }

        MemoDAO dao = new MemoDAO();
        return dao.addMemo(id, title, content) ? SUCCESS : ERROR;
    }

    public String download() throws SQLException {

        Integer id = Integer.parseInt((String) request.getAttribute("id"));

        if (id != 1) {
            message = "Only Admin";
            return ERROR;
        }

        if (this.id == null || this.owner == null) {
            message = "Not found";
            return ERROR;
        }

        int memoId = this.id;
        int owner = this.owner;

        String cacheFile = String.format("memo_%d_%d.csv", owner, memoId);
        CACHE_PATH = CACHE_DIR + cacheFile;

        File cacheDir = new File(request.getServletContext().getRealPath(CACHE_DIR));
        if (!cacheDir.exists()) {
            cacheDir.mkdirs();
        }
        File cachedFile = new File(cacheDir, cacheFile);

        if (!cachedFile.exists()) {

            MemoDAO dao = new MemoDAO();
            Map<String, String> memo = dao.getMemo(owner, memoId);
            if (memo.isEmpty()) {
                message = "Not found";
                return ERROR;
            }

            try (BufferedWriter writer = new BufferedWriter(new FileWriter(cachedFile))) {
                writer.write("id,title,content,owner\n");
                writer.write(String.format("\"%s\",\"%s\",\"%s\",\"%s\"\n",
                        memo.get("id"),
                        memo.get("title"),
                        memo.get("content"),
                        memo.get("owner")));
            } catch (IOException e) {
                message = "Some ERROR";
                return ERROR;
            }
        }

        return SUCCESS;

    }

}
