from tkinter import Tk, BOTH, Canvas, Frame
import tkinter
import numpy as np
import enum
import time
import os
import util


class Visual(Frame):
    def __init__(self, parent, w=850, h=850, cellx_n=15, celly_n = 15, color="#fff8b0"):
        Frame.__init__(self, parent, background="white")
        self.parent = parent
        self.canv = Canvas(self, bg=color)
        self.width = w
        self.height = h
        self.cellx_n = cellx_n
        self.celly_n = celly_n
        self.initUI()


    def get_canvas(self):
        return self.canv


    def get_width(self):
        return self.width


    def get_height(self):
        return self.height


    def print_coords(self):
        cellw = self.width // (self.cellx_n + 2)
        cellh = self.height // (self.cellx_n + 2)
        for i in range(1, self.cellx_n + 1):
            self.canv.create_text(cellw // 2, cellh // 2 + cellh * i,
                text=str(i), font=('Calibri', 13))

        string = 'abcdefghjklmnop'
        for i in range(1, self.celly_n + 1):
            self.canv.create_text(cellw // 2 + cellw * i, self.height - cellh // 2,
                text = string[i - 1], font=('Calibri', 13))


    def draw_lines(self, w, h):
        for i in range(0, self.cellx_n + 2):
            x = w * (i + 1) // (self.cellx_n + 2)
            cellw = w // (self.cellx_n + 2)
            self.canv.create_line(x, cellw, x, h - cellw, fill='#844200')

        for i in range(0, self.celly_n + 2):
            y = h * (i + 1) // (self.celly_n + 2)
            cellh = h // (self.cellx_n + 2)
            self.canv.create_line(cellh, y, w - cellh, y, fill='#844200')

        
    def draw_stone(self, x, y, player, num):
        cellw = self.width // (self.cellx_n + 2)
        cellh = self.height // (self.celly_n + 2)
        y1 = cellw + self.width  * x // (self.cellx_n + 2) + 0.1 * cellw
        x1 = cellh + self.height * y // (self.celly_n + 2) + 0.1 * cellh
        x2 = x1 + 0.8 * cellw
        y2 = y1 + 0.8 * cellh

        if player == 'white':
            stone = self.canv.create_oval(x1, y1, x2, y2,
                fill = 'white', width='2', tag='stone')
            self.canv.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                text=str(num), font=('Calibri', 11), fill='black')
        else:
            stone = self.canv.create_oval(x1, y1, x2, y2,
                fill = 'grey', width='2', tag='stone')
            self.canv.create_text((x1 + x2) // 2, (y1 + y2) // 2,
                text=str(num), font=('Calibri', 11), fill='white')


    def draw_result(self, player):
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = self.width // 2
        y = self.height // 2
        self.canv.create_rectangle(x - self.width // 4, y - self.height // 4,\
                                   x + self.width // 4, y + self.height // 4,\
                                   outline='black', fill='white', width=2)
        self.canv.create_text(x, y - 20, font='Calibri 16', text='Game is over')
        self.canv.create_text(x, y + 20, font='Calibri 16', text='Winner is ' + player)
        self.canv.bind("<Button-1>", self.destroyUI)


    def initUI(self):
        self.parent.title("Game Board")
        self.pack(fill=BOTH, expand=1)
        self.draw_lines(self.width, self.height)
        self.print_coords()
        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        x = (sw - self.width)/2
        y = (sh - self.height)/2
        self.parent.geometry('%dx%d+%d+%d' % (self.width, self.height, x, y))
        self.canv.pack(fill=BOTH, expand=1)

    def destroyUI(self, event):
        self.parent.destroy()



class Player(enum.IntEnum):
    NONE = 0
    BLACK = 1
    WHITE = -1


    def another(self):
        return Player(-self)


    def __repr__(self):
        if self == Player.BLACK:
            return 'black'
        elif self == Player.WHITE:
            return 'white'
        else:
            return 'none'


    def __str__(self):
        return self.__repr__()
        


class Game():
    width = 15
    height = 15
    shape = (width, height)
    line_length = 5

    def __init__(self):
        self._result = Player.NONE
        self._player = Player.BLACK
        self._positions = list()
        self._board = np.full(self.shape, Player.NONE, dtype=np.int8)


    def __bool__(self):
        return self.result() == Player.NONE and \
            len(self._positions) < self.width * self.height


    def move_n(self):
        return len(self._positions)


    def player(self):
        return self._player


    def result(self):
        return self._result


    def board(self):
        return self._board


    def getwidth(self):
        return self.width


    def getheight(self):
        return self.height


    def getline_length(self):
        return self.line_length


    def positions(self, player=Player.NONE):
        if not player:
            return self._positions

        begin = 0 if player == Player.BLACK else 1
        return self._positions[begin::2]


    def dumps(self):
        return ' '.join(map(util.to_move, self._positions))


    @staticmethod
    def loads(dump):
        game = Game()
        for pos in map(util.to_pos, dump.split()):
            game.move(pos)
        return game


    def is_possible_move(self, pos):
        return 0 <= pos[0] < self.height \
            and 0 <= pos[1] < self.width \
            and not self._board[pos]


    def move(self, pos):
        assert self.is_possible_move(pos), 'impossible pos: {pos}'.format(pos=pos)

        self._positions.append(pos)
        self._board[pos] = self._player

        if not self._result and util.check(self._board, pos, self.line_length, self.width, self.height):
            self._result = self._player
            return

        self._player = self._player.another()


class Controller():
    def __init__(self, visual, mode='Player', model1=None, model2=None):
        self._visual = visual
        self._mode = mode
        self._game = Game()
        self._model1 = model1
        self._model2 = model2
        self.start_visual()


    def make_act(self, x, y):
        if self._game.is_possible_move((x, y)):
            self._game.move((x, y))
        else:
            return

        self._visual.draw_stone(x, y, str(self._game.player()), self._game.move_n())

        if self._game.result() != Player.NONE:
            self._visual.draw_result(str(self._game.result()))
            return


    def game(self):
        return self._game


    def make_move(self, event):
        denom1 = self._visual.get_width() // (self._game.getwidth() + 2)
        denom2 = self._visual.get_height() // (self._game.getheight() + 2)
        y = event.x // denom1 - 1
        x = event.y // denom2 - 1
        if x < 0 or y < 0 or x > 14 or y > 14:
            return
        self.make_act(x, y)
        if self._game.result() != Player.NONE:
            return

        if self._mode != 'PvP':
            if self._game.player() == Player.BLACK:
                move = self._model1.get_move(self._game.board(), self._game.player())
                self.make_act(move[0], move[1])
            elif self._game.player() == Player.WHITE:
                move = self._model2.get_move(self._game.board(), self._game.player())
                self.make_act(move[0], move[1])


    def start_fun(self, event):
        if self._game.player() == Player.BLACK:
            move = self._model1.get_move(self._game.board(), self._game.player())
            self.make_act(move[0], move[1])
        elif self._game.player() == Player.WHITE:
            move = self._model2.get_move(self._game.board(), self._game.player())
            self.make_act(move[0], move[1])


    def start_visual(self):
        if self._mode == 'BlackVe':
            self._visual.get_canvas().bind("<Button-1>", self.make_move)
        elif self._mode == 'WhiteVe':
            move = self._model1.get_move(self._game.board(), self._game.player())
            self.make_act(move[0], move[1])
            self._visual.get_canvas().bind("<Button-1>", self.make_move)
        elif self._mode == 'PvP':
            self._visual.get_canvas().bind("<Button-1>", self.make_move)
        else:
            self._visual.get_canvas().bind("<Button-1>", self.start_fun)
