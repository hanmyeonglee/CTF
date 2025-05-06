from matplotlib import pyplot as plt
import json
import pandas as pd
import statsmodels.api as sm

with open('./candidates.txt', 'r', encoding='utf-8') as targets, \
     open('./combination_log.txt', 'r', encoding='utf-8') as log:
    data = json.loads(targets.read())
    data = dict(map(tuple, data))

    logs = json.loads(log.read())


point_x = [list() for _ in range(8)]
point_y = []
for log in logs:
    try:
        comb = log['selected_terms']
        res = ord(log['response']['symbol'])

        comb = [ord(data[name]) for name in comb]
        for i in range(8):
            point_x[i].append(comb[i])
    except:
        print(log)
        continue

    point_y.append(res)

data = {f'x{i}': point_x[i] for i in range(8)}
data['y'] = point_y
data = pd.DataFrame(data)

X = data[[f'x{i}' for i in range(8)]]
y = data['y']

model = sm.OLS(y, X).fit()

print(model.summary())