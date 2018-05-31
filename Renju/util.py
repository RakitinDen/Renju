import itertools
import numpy


POS_TO_LETTER = 'abcdefghjklmnop'
LETTER_TO_POS = {letter: pos for pos, letter in enumerate(POS_TO_LETTER)}

def to_move(pos):
    return POS_TO_LETTER[pos[1]] + str(pos[0] + 1)

def to_pos(move):
    return (int(move[1:]) - 1) * 15 +  LETTER_TO_POS[move[0]]

def to_coords(move):
    return int(move[1:]) - 1, LETTER_TO_POS[move[0]]

def to_mtx_coords(pos):
    return pos // 15, pos % 15


def list_positions(board, player):
    return numpy.vstack(numpy.nonzero(board == player)).T


def sequence_length(board, I, J, value):
    length = 0

    for i, j in zip(I, J):
        if board[i, j] != value:
            break
        length += 1

    return length


def check_horizontal(board, pos, line_length=5, width=15):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        itertools.repeat(i),
        range(j + 1, min(j + line_length, width)),
        player
    )

    length += sequence_length(
        board,
        itertools.repeat(i),
        range(j - 1, max(j - line_length, -1), -1),
        player
    )

    return length >= line_length

def check_vertical(board, pos, line_length=5, height=15):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        range(i + 1, min(i + line_length, height)),
        itertools.repeat(j),
        player
    )

    length += sequence_length(
        board,
        range(i - 1, max(i - line_length, -1), -1),
        itertools.repeat(j),
        player
    )

    return length >= line_length

def check_main_diagonal(board, pos, line_length=5, width=15, height=15):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        range(i + 1, min(i + line_length, height)),
        range(j + 1, min(j + line_length, width)),
        player
    )

    length += sequence_length(
        board,
        range(i - 1, max(i - line_length, -1), -1),
        range(j - 1, max(j - line_length, -1), -1),
        player
    )

    return length >= line_length

def check_side_diagonal(board, pos, line_length=5, width=15, height=15):
    player = board[pos]
    if not player:
        return False

    i, j = pos
    length = 1

    length += sequence_length(
        board,
        range(i - 1, max(i - line_length, -1), -1),
        range(j + 1, min(j + line_length, width)),
        player
    )

    length += sequence_length(
        board,
        range(i + 1, min(i + line_length, height)),
        range(j - 1, max(j - line_length, -1), -1),
        player
    )

    return length >= line_length

def check(board, pos, line_length=5, width=15, height=15):
    if not board[pos]:
        return False

    return check_vertical(board, pos, line_length, height) \
        or check_horizontal(board, pos, line_length, width) \
        or check_main_diagonal(board, pos, line_length, width, height) \
        or check_side_diagonal(board, pos, line_length, width, height)
