<%@ taglib uri="/struts-tags" prefix="s" %>
<!DOCTYPE html>
<html lang="en">

<head>
    <title>Login</title>
</head>

<body>
    <div class="container">
        <div class="common-container">
            <h3 class="text-center mb-4">Login</h3>
            <form action="login.action" method="post">
                <div class="mb-3">
                    <label for="username" class="form-label">username</label>
                    <input id="username" name="username" class="form-control" required="true"
                        placeholder="username" />
                </div>
                <div class="mb-3">
                    <label for="password" class="form-label">password</label>
                    <input type="password" id="password" name="password" class="form-control" required="true"
                        placeholder="password" />
                </div>
                <button type="submit" class="btn btn-primary w-100">Login</button>
                <div class="text-center mt-3">
                    <a href="/user/register.action">Register</a> | <a href="#">Find Password</a>
                </div>
            </form>
        </div>
    </div>
</body>

</html>