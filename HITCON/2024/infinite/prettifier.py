import json

""" with open('./G1v3_m3_soUr5e_C0dE.json', 'r', encoding='utf-8') as f0, \
     open('./sourcecode.json', 'w', encoding='utf-8') as f1:
    f1.write(json.dumps(json.loads(f0.read()), indent=2)) """

with open('./sourcecode.json') as sc:
    codes = json.loads(sc.read())['source']

for key, code in codes.items():
    print(code, file=open(f'./codes/{key}', 'w', encoding='utf-8'))