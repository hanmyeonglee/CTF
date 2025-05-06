import numpy as np 
from time import sleep

a = np.array([3, 5, 7, 11, 13], dtype=np.int32)
i = 0
while True:
    i += 1
    print(i, a := a ** 2)
    sleep(0.5)