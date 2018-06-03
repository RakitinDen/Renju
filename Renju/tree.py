import numpy as np
import keras
import time

import renju
import util


class large_model():
    def __init__(self, model):
        self._model = model

    def make_pred(self, board):
        pred = self._model.predict(np.reshape(board, [1, 15, 15, 1])).reshape((225))
        pred *= (board.ravel() == renju.Player.NONE)
        return pred / np.sum(pred)


class Node():
    def __init__(self, player, move=None, parent=None):
        self._player = player
        self._policy = np.zeros(225, dtype=np.int16)
        self._board_visits = np.zeros(225, dtype=np.int16)
        self._rewards = np.zeros(225, dtype=np.int16)
        self._children = [None for i in range(225)]
        self._visit_n = 0


    def expand(self, child):
        self._children[child] = Node(self._player.another())
        if self._visit_n == 0:
            self._visit_n = 1


    def is_leaf(self):
        return self._visit_n == 0


class MCTS():
    def __init__(self, policy, rollout, max_depth=10, timeout= 2.9):
        self._policy = policy
        self._rollout = rollout
        self._max_depth = max_depth
        self._timeout = timeout
        self._root = None
        self._board = None


    def search(self):
        init_time = time.time()
        while time.time() - init_time < self._timeout:
            path, winner = self.simulate_game()
            self.backpropagate(path, winner)


    def backpropagate(self, path, winner):
        cur = self._root
        for move in path:
            cur._board_visits[move] += 1
            if cur._player == winner:
                cur._rewards[move] += 1
            elif cur._player.another() == winner:
                cur._rewards[move] -= 1
            cur = cur._children[move]
        del path


    def select(self, board, node):
        moves = (board == renju.Player.NONE).ravel()
        probs = node._policy * np.sqrt(node._visit_n) / (node._board_visits + 1)
        q_value = node._rewards / (node._board_visits + 1)
        return np.argmax((probs + q_value) * moves)


    def selection(self, flag):
        path = []
        depth = 0
        node = self._root
        board = np.copy(self._board)
        while depth < self._max_depth:
            if node.is_leaf():
                return board, node, path, depth

            node._visit_n += 1
            move = self.select(board, node)
            path.append(move)
            if not node._children[move]:
                node.expand(move)
            board[util.to_mtx_coords(move)] = node._player
            if util.check(board, util.to_mtx_coords(move)):
                flag = 1
                return board, node, path, depth

            node = node._children[move]
            depth += 1

        return board, node, path, depth


    def simulate_game(self):
        flag = 0
        board, leaf, path, depth = self.selection(flag)

        if flag:
            return path, leaf._player

        if depth >= self._max_depth:
            return path, renju.Player.NONE

        leaf._policy = self._policy.make_pred(board)
        move = np.random.choice(225, p=leaf._policy)
        board[util.to_mtx_coords(move)] = leaf._player
        path.append(move)
        leaf.expand(move)

        if util.check(board, util.to_mtx_coords(move)):
            return path, leaf._player

        return path, self.playout(board, move, depth)


    def playout(self, board, move, depth):
        def check_winner(board, player):
            for row in range(15):
                for col in range(15):
                    if board[row, col] == renju.Player.NONE:
                        board[row, col] = player
                        if util.check(board, (row, col)):
                            return 1
                        board[row, col] = renju.Player.NONE
            return 0

        cur_player = -board[util.to_mtx_coords(move)]
        while depth < self._max_depth:
            if check_winner(board, cur_player):
                return cur_player

            if np.count_nonzero(board == renju.Player.NONE) == 0:
                return renju.Player.NONE

            probs = self._rollout.make_pred(board)
            move = np.random.choice(225, p=probs)
            board[util.to_mtx_coords(move)] = cur_player
            if util.check(board, util.to_mtx_coords(move)):
                return cur_player

            depth += 1
            cur_player = -cur_player

        return renju.Player.NONE


    def get_move(self, board, player):
        def check_winner(board, player):
            for row in range(15):
                for col in range(15):
                    if board[row, col] == renju.Player.NONE:
                        board[row, col] = player
                        if util.check(board, (row, col)):
                            board[row, col] = renju.Player.NONE
                            return (row, col)
                        board[row, col] = renju.Player.NONE
            return (-1, -1)

        pos = check_winner(board, player)
        if not pos[0] == -1:
            return pos

        self._root = Node(player)
        self._root._policy = self._policy.make_pred(board)
        self._board = board
        self.search()
        moves = (board == renju.Player.NONE).ravel()
        res = np.argmax(self._root._board_visits * moves)
        res = util.to_mtx_coords(res)
        return res
