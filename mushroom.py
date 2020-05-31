# coding: utf-8

import pygame
from pygame.locals import *

from object import Object


# キノコを表現するクラス
class Mushroom(Object):
    # キノコの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 5) # 物体として初期化する
        self.is_right = True # 進行方向が右であるかフラグ

    # キノコの状態の更新
    def update(self):
        if self.vx == 0: # 速度がゼロになる (壁に当たる) と方向転換する
            self.is_right = not self.is_right
            if self.is_right:
                self.vx = 5
            else:
                self.vx = -5
        super().update() # 物体に共通する更新処理

    # キノコの描画
    def draw(self, surface, imageManager):
        surface.blit(imageManager.images["mushroom"], (self.x, self.y))

    # プレイヤー (今回はマリオ) との衝突処理をする
    def collisionDetection(self, player):
        if super().collisionDetection(player):
            self.is_deleted = True # 取ったキノコは削除する
            player.powerUp() # プレイヤーはパワーアップする
