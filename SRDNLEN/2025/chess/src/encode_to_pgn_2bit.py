from collections import defaultdict
from chess import Board, pgn
import chess
from Crypto.Util.number import bytes_to_long

def string_to_bits(s):
    binary_string = bin(bytes_to_long(s.encode()))[2:]
    padding_length = (8 - len(binary_string) % 8) % 8
    padded_binary_string = binary_string.zfill(len(binary_string) + padding_length)
    return padded_binary_string

dic_tile_to_bits = { 
    f"{chr(col + ord('a'))}{8 - row}": f"{row % 2}{col % 2}"
    for row in range(8)
    for col in range(8)
}

dic_bits_to_tile = defaultdict(list)
for k, v in dic_tile_to_bits.items():
    dic_bits_to_tile[v].append(k)
dic_bits_to_tile = dict(dic_bits_to_tile)

def encode_to_pgn(string_to_encode, prng):
    chess_board = Board()
    output_pgns = []
    bits_to_encode = string_to_bits(string_to_encode)

    for i in range(len(bits_to_encode) // 2):
        current_2bits = bits_to_encode[i * 2:i * 2 + 2]

        legal_moves = list(str(k) for k in chess_board.generate_legal_moves())
        possible_moves = dic_bits_to_tile[current_2bits]

        legal_possible_moves = [ legal_move for legal_move in legal_moves if legal_move[2:4] in possible_moves ]

        if not legal_possible_moves:
            pgn_board = pgn.Game()
            pgn_board.add_line(chess_board.move_stack)
            output_pgns.append(str(pgn_board))
            chess_board = Board()

            legal_moves = list(str(k) for k in chess_board.generate_legal_moves())
            possible_moves = dic_bits_to_tile[current_2bits]
            legal_possible_moves = [ legal_move for legal_move in legal_moves if legal_move[2:4] in possible_moves ]

            chosen_move = prng.choice(legal_possible_moves)
            chess_board.push(chess.Move.from_uci(chosen_move))
            print(chosen_move)

        else:
            chosen_move = prng.choice(legal_possible_moves)
            chess_board.push(chess.Move.from_uci(chosen_move))
            print(chosen_move)

            if chess_board.is_insufficient_material() or chess_board.can_claim_draw():
                pgn_board = pgn.Game()
                pgn_board.add_line(chess_board.move_stack)
                output_pgns.append(str(pgn_board))
                chess_board = Board()

    pgn_board = pgn.Game()
    pgn_board.add_line(chess_board.move_stack)
    output_pgns.append(str(pgn_board))

    return output_pgns

