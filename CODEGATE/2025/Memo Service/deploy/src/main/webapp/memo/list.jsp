<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib uri="/struts-tags" prefix="s" %>
<!DOCTYPE html>
<html lang="en">

<head>
    <title>
        <s:property value="username" />'s Memo
    </title>
</head>

<body>
    <div class="container mt-4">
        <h2 class="text-center mb-4">
            <s:property value="username" />'s Memo
        </h2>
        <div class="row row-cols-1 row-cols-md-3 g-4">
            <s:iterator value="memos">
                <div class="col d-flex justify-content-center">
                    <div class="memo-card" onclick="location.href='/memo/read.action?id=<s:property value="id" />'">
                    <div class="memo-title">
                        <s:property value="title" />
                    </div>
                    <div class="memo-content">
                        <s:property value="content" />
                    </div>
                </div>
        </div>
        </s:iterator>
        <div class="col d-flex justify-content-center">
            <div class="memo-card add-memo-card" onclick="location.href='/memo/write.action'">
                +
            </div>
        </div>
    </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>