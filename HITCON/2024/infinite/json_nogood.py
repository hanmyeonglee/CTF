import json

with open('./recipe_backup.json', 'r', encoding='utf-8') as data, \
     open('./recipe_backup.backup.json', 'w', encoding='utf-8') as data2:
    data2.write(json.dumps(json.loads(data.read()),ensure_ascii=False))