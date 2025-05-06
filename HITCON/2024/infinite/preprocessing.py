import json, random

with open('./comb_log.txt', 'r', encoding='utf-8') as log:
    logs = json.loads(log.read())
    logs = [log for log in logs if "english_name" in log["response"]]

L = set([log["response"]["english_name"] for log in logs])
data = dict.fromkeys(L, None)
for key in data.keys():
    data[key] = list()

for log in logs:
    items = log["selected_terms"]
    items.sort()

    key = log["response"]["english_name"]
    element = str(items)
    if element in data[key]:
        continue

    data[key].append(items)


instruction = 'Make single(output has no +) simple(No Assistant opinion) short(maximum length is 100) new word that is appropriate to the concept of given 8 words which are connected each other by + character'
preprocessed_data = []
dict_format = [
    ['instruction', instruction],
    ['input', None],
    ['output', None],
]

for result, combinations in data.items():
    for combination in combinations:
        for _ in range(30):
            dict_format[1][1] = '+'.join(combination)
            dict_format[2][1] = result
            preprocessed_data.append(dict(dict_format))
            random.shuffle(combination)


with open('./bagua_extended.json', 'w', encoding='utf-8') as js:
    js.write(json.dumps(preprocessed_data, indent=1))