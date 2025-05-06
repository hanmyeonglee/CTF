import base64

packet = """
4500 003c 1c46 0000 4001 a6ec c0a8 01fd
c0a8 0101 
0800 4dcb 1f2b 0001 6162 6364 6566 6768
696a 6b6c 6d6e 6f70 7172 7374 7576 7761
""".strip()
packet_hex = ''.join(packet.split())
packet_bin = bytes.fromhex(packet_hex)

print(base64.b64encode(packet_bin).decode())