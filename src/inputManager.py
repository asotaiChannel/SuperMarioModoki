# coding: utf-8

import pygame
from pygame.locals import *

import sys


# ユーザ入力を受け付けるマネージャ
class InputManager:
    # マネージャの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self):
        self.key_push = {} # どのキーが何フレーム押され続けているかを保持する

    # 指定したキーが「押された瞬間」であるかどうかを判定する (True or False)
    def isPushKeyNow(self, key):
        return self.key_push.get(key, 0) == 1

    # 指定したキーが「何フレーム押され続けているか」を取得する
    def getPushKeyFrames(self, key):
        return self.key_push.get(key, 0)

    # 指定したキーが「押されているか」を取得する
    def isPushKey(self, key):
        return key in self.key_push

    # ユーザ入力状態を取得し更新する関数
    def update(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN: # キー入力されていればキー入力フレーム数を増加する
                if event.key in self.key_push:
                    self.key_push[event.key] += 1
                else:
                    self.key_push[event.key] = 1
            elif event.type == KEYUP: # キーが離されたらキー入力フレーム数を消去する
                if event.key in self.key_push:
                    self.key_push.pop(event.key)
            elif event.type == QUIT: # ゲーム画面と閉じるボタンが押されたら終了する
                pygame.quit()
                sys.exit()
