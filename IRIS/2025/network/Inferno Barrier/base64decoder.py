import base64

while True:
    s = input('base64: ')
    print(base64.b64decode(s).hex())
    try:
        print(base64.b64decode(s).decode())
    except:
        pass