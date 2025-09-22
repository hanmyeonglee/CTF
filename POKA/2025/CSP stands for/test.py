import requests

URL = 'http://3.37.52.71:7575'
r = requests.post(URL + '/report', data={'report_url': 'http://sol.plus.or.kr:18481/'})
#URL = 'http://127.0.0.1:7575'
#r=  requests.post(URL + '/report', data={'report_url': 'http://127.0.0.1:18481/'})
#print(r.text)