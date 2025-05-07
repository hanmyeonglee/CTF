import clipboard, json
xss = open('xss.txt').read().splitlines(keepends=False)
clipboard.copy(json.dumps(xss))