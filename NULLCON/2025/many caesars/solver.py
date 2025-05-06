import string
chars = string.ascii_letters + string.digits + '+/='

def islower(text):
    return all(ch in string.ascii_lowercase for ch in text)

def reverse_caesar(msg, shift):
    return ''.join(chars[(chars.index(c) - shift) % len(chars)] for c in msg)

flag = []
text = open('./many caesars/output.txt','r').read()
i = 0
count = 0
calculated = "hacker ethics is a set of principles that guide the behavior of individuals who explore and manipulate computer systems, often emphasizing curiosity, creativity, and the pursuit of knowledge. rooted in values such as openness, free access to information, and the belief in using skills to improve systems rather than harm them, hacker ethics encourages responsible and ethical use of technology. it advocates for transparency, collaboration, and respecting privacy, while discouraging malicious activities".replace(',', '').replace('.', '').split()
fulltext = ''
while i < len(text):
    if text[i] not in chars:
        fulltext += text[i]
        i += 1
    else:
        j = i
        while text[j] in chars: j += 1
        msg = text[i:j]        
        ress = []
        for ind in range(len(chars)):
            res = reverse_caesar(msg, ind)

            if count < len(calculated):
                if res == calculated[count]:
                    ress.clear()
                    ress.append([ind, res])
                    break

            if islower(res):
                print(f'{ind}.', res)
                ress.append([ind, res])

        if len(ress) == 1:
            inp = ress[0][0]
        else:
            inp = int(input(f'{fulltext = }\nindex : '))
        flag.append(chars[inp])
        fulltext += reverse_caesar(msg, inp)
        count += 1
        i = j

    print('flag = ', *flag, sep='')

print(*flag, sep='')