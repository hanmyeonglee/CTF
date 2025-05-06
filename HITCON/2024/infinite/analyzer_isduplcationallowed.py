import json

with open('./comb_log.txt', 'r', encoding='utf-8') as log, \
     open('./targets.txt', 'r', encoding='utf-8') as target:
    targets = json.loads(target.read())
    targets = [pair[0] for pair in targets]
    targets.sort()

    logs = json.loads(log.read())
    logs = [log for log in logs if "english_name" in log["response"]]

sort_bykey = dict()
for log in logs:
    res = log["response"]["english_name"]

    items = log["selected_terms"]
    items = [targets.index(item) for item in items]
    key = ''.join(map(str, sorted(items)))

    if key not in sort_bykey:
        sort_bykey[key] = set()

    sort_bykey[key].add(res)

for key in sort_bykey.keys():
    sort_bykey[key] = list(sort_bykey[key])

print(json.dumps(sort_bykey, indent=1))

for key, val in sort_bykey.items():
    if len(val) > 1:
        print(key, val)

#순서 섞이는지 확인해보고
#LLM 학습 ㅅㄱ