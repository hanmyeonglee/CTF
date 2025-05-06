img = ''
with open('noshark.pcap', 'r') as pcap:
    for i, line in enumerate(pcap.readlines()):
        if i < 3: continue
        if i % 2 == 0: continue
        img += line[132:]

with open('img.jpg', 'wb') as image:
    image.write(bytes.fromhex(img))