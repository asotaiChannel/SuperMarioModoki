# coding: utf-8

import pygame
from pygame.locals import *

from object import Object


# ブロックを表現するクラス
class Block(Object):
    # ブロックの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 0) # 物体として初期化する
        self.is_hit = True # 衝突判定があるかフラグ

    # ブロックの描画
    def draw(self, surface, imageManager):
        pygame.draw.rect(surface, (80, 80, 80), Rect(self.x + 10, self.y + 10, self.w, self.h))
        surface.blit(imageManager.images["block"], (self.x, self.y))
        pygame.draw.rect(surface, (0, 0, 0), Rect(self.x, self.y, self.w, self.h), 1)
