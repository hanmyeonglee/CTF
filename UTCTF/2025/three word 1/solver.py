import json

data = json.loads(open('what3words.com.har', encoding='utf-8').read()).get('log').get('entries')
arranged = []
words = []
for D in data:
    req = D.get('request', None)
    if req is None: continue
    #print(req)

    query = req.get('queryString', None)
    if query is None: continue
    #print(query)

    for Q in query:
        q = Q.get("name", None)
        if q is None: continue
        if q != 'coordinates': continue
        #print(q)
        
        coordinate = Q.get("value", None)
        if coordinate is None: continue
        coordinate = tuple(map(float, coordinate.split('%2C')))
        
        res = D.get('response', None)
        if res is None: continue

        content = res.get('content', None)
        if content is None: continue

        text = content.get('text', None)
        if text is None: continue
    
        js = json.loads(text)
        w3w = js.get('words', None)
        if w3w is None: continue

        arranged.append((coordinate, w3w))
        words.append(w3w)

print(arranged)

json.dump(arranged, fp=open('w3w.json', 'w'), ensure_ascii=False, indent=1)
json.dump(words, fp=open('words.json', 'w'), ensure_ascii=False, indent=1)
