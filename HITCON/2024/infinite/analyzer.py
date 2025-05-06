import json

with open('./comb_log.txt', 'r', encoding='utf-8') as log, \
     open('./targets.txt', 'r', encoding='utf-8') as target:
    targets = json.loads(target.read())
    targets = [pair[0] for pair in targets]
    targets.sort()

    logs = json.loads(log.read())
    logs = [log for log in logs if "english_name" in log["response"]]

L = set([log["response"]["english_name"] for log in logs])
sort_bykey = dict.fromkeys(L, None)
for key in sort_bykey.keys():
    sort_bykey[key] = list()

print(len(logs))
print(len(targets))

for log in logs:
    items = log["selected_terms"]
    items.sort()
    items = [targets.index(item) for item in items]

    key = log["response"]["english_name"]
    element = str(items)
    if element in sort_bykey[key]:
        continue

    sort_bykey[key].append(str(items))

with open('./log_based_on_key_looks_very_good.txt', 'w', encoding='utf-8') as log:
    log.write(json.dumps(sort_bykey, indent=1))

#순서 섞이는지 확인해보고
#LLM 학습 ㅅㄱ