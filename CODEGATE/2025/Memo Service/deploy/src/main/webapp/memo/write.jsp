<%@ page contentType="text/html; charset=UTF-8" %>
<%@ taglib uri="/struts-tags" prefix="s" %>
<!DOCTYPE html>
<html lang="en">

<head>
    <title>Create Memo</title>
</head>

<body>
    <div class="container">
        <div class="memo-container">
            <h3 class="text-center mb-4">New Memo</h3>
            <form action="/memo/write.action" method="post">
                <div class="mb-3">
                    <label for="title" class="form-label">title</label>
                    <input id="title" name="title" class="form-control" required="true" placeholder="title" />
                </div>
                <div class="mb-3">
                    <label for="content" class="form-label">content</label>
                    <textarea id="content" name="content" class="form-control" required="true" rows="5"
                        placeholder="content"></textarea>
                </div>
                <button type="submit" class="btn btn-primary w-100">Save</button>
                <div class="text-center mt-3">
                    <a href="/memo/list.action" class="btn btn-secondary w-100">Cancel</a>
                </div>
            </form>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>

</html>