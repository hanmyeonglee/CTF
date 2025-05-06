import requests
path = 'https://osint-food-blog-web.chal.irisc.tf/'
res = requests.get(path)
while True:
    ind = res.find('')