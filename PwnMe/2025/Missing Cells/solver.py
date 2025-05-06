from takuzu.takuzu import Takuzu

B = \
"""
. . . . . . . . . . . . . . . .
. . . . . . . . . . . . . . . .
. . . . . . . . . . . . . . . .
. . . . . . . . 0 . . . . . 1 1
. 1 1 . . 1 . 1 . . . 1 . . . .
1 . . 0 . . . . . . . 1 . . . .
. . . . . . . 1 . 0 . . 0 . 0 .
0 . . . . . . . . . . . . . 0 0
. . 0 0 . . . . . . 1 1 . . . .
. . . . . . 0 . 1 . . . . . . 0
. . 1 . . 1 . . . 1 . . . . 1 .
. 1 1 . . . . . . . . 0 . . . .
. . . . . . 1 . . . . . 1 . 1 1
. . . . . . . . . . . . . . . .
. . . . . . 0 . . 1 . . . . . 0
. . . . . . . . . . . . . . . .
"""[1:-1]

board = []
for row in B.split('\n'):
    board.append(row.split()[:8])
    board.append(row.split()[8:])

key = bin(0xc56217e72f2ee27f0ec1f00f06956493ab02a2f8072159f3a27e79d399a4924f)[2:]
key = [key[i:i+8] for i in range(0, 256, 8)]

flag = 'PWNME{.........................}'
for i, ch, k in zip(range(32), flag, key):
    if ch == '.': continue
    ch_num = ord(ch)
    k_num = int(k, 2)
    answer = ch_num ^ k_num
    answer = '{:08b}'.format(answer)

    for j, b in enumerate(answer):
        board[i][j] = b

board = [board[i] + board[i + 1] for i in range(0, 32, 2)]

import clipboard
clipboard.copy(str(board))
exit()

for i in range(16):
    for j in range(16):
        ch = board[i][j]
        if ch == '.': board[i][j] = None
        else: board[i][j] = int(ch)