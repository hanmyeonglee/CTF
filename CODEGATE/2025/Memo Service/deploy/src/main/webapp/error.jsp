<%@ taglib uri="/struts-tags" prefix="s" %>
<html>

<head>
    <title>
        <s:property value="message" />
    </title>

</head>

<body>
    <script>alert('<s:property value="message"/>'); history.back();</script>
</body>

</html>