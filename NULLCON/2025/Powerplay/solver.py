import numpy as np

goal = {-i-1 for i in range(24)}
num = 3
while True:
    a = np.array([num], dtype=np.int32)
    cnt = 0
    while (a := a ** 2)[0] != 1:
        cnt += 1
        if int(a[0]) in goal:
            print(num, cnt)
            exit()
    
    num += 1