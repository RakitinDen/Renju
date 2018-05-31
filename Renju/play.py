#!/usr/bin/python3
from tkinter import Tk, BOTH, Canvas, Frame
import tkinter
import numpy as np
import enum
import keras
from keras.models import load_model

import util
import renju
import tree

import os


def gameplay(mode):
    model = load_model('policy.h5')
    rollout = load_model('rollout.h5')
    root = Tk()
    ex = renju.Visual(root)
    if mode == 'B':
        mode = 'BlackVe'
        controller = renju.Controller(ex, mode, model2=tree.MCTS(policy=tree.large_model(model),
                                                rollout=tree.large_model(rollout)))
    elif mode == 'W':
        mode = 'WhiteVe'
        controller = renju.Controller(ex, mode, model1=tree.MCTS(policy=tree.large_model(model),
                                                rollout=tree.large_model(rollout)))
    elif mode == 'P':
        mode = 'PvP'
        controller = renju.Controller(ex, mode)
    else:
        controller = renju.Controller(ex, mode, model1=tree.MCTS(policy=tree.large_model(model),
                                                rollout=tree.large_model(rollout)),
                                                model2=tree.MCTS(policy=tree.large_model(rollout),
                                                rollout=tree.large_model(rollout)))
    root.mainloop()



def main():
    print('Введите тип игры, возможные варианты:')
    print('W - за белых, B - за черных, P - игрок против игрока')
    print('При вводе любого другого значения модели играют друг с другом')
    print('Шаг в таком случае осуществляется по клику внутри доски')
    s = str(input())
    gameplay(s)

if __name__ == '__main__':
    main()