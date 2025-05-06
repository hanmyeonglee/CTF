import json

with open('./combination_log.txt', 'r', encoding='utf-8') as log1, \
     open('./logs.txt', 'r', encoding='utf-8') as log2:
    log = json.loads(log1.read())
    log.extend(json.loads(log2.read()))


with open('./comb_log.txt', 'w', encoding='utf-8') as comb:
    comb.write(json.dumps(log, indent=1, ensure_ascii=False))