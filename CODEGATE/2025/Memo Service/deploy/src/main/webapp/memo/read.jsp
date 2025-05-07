<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib uri="/struts-tags" prefix="s" %>
<!DOCTYPE html>
<html lang="en">

<head>
    <title>
        <s:property value="memo.title" />
    </title>
</head>

<body>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/dompurify/3.2.3/purify.min.js"></script>

    <div class="container mt-5">
        <!-- <s:property value="memo.owner" /> -->
        <div id="memo"></div>
        <s:property value="memo.content" escapeHtml="false" />
        <script>
            content = DOMPurify.sanitize(content);
            memo.innerHTML = content;
        </script>
        <a href="/memo/list.action" class="btn btn-secondary">Back to memos</a>
    </div>
</body>

</html>