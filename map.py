# coding: utf-8

import pygame
from pygame.locals import *

from block import Block


# マップを表現するクラス
class Map:
    # マップの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, w, h):
        self.w, self.h = w, h # ブロックの横幅と縦幅を設定する
        self.block_id_array = [ # マップデータ
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.set(self.block_id_array) # マップデータをブロックの集合に変換する

    # ブロックを生成する関数
    def blockFactory(self, id, ix, iy):
        if id == 0:
            return None
        else:
            return Block(ix*self.w, iy*self.h, self.w, self.h)

    # マップ情報をセットする
    def set(self, block_id_array):
        self.block_array = []
        for iy, block_id_list in enumerate(self.block_id_array):
            self.block_array.append(
                [
                    self.blockFactory(block_id, ix, iy)
                    for ix, block_id in enumerate(block_id_list)
                ]
            )

    # キャラクターとの衝突判定を行い更新する
    def collisionDetection(self, character):
        # キャラクターの左右の衝突判定
        character.updateX()
        if character.vx < 0: # 左側との衝突判定
            ix = int(character.x/self.w)
            for iy in range(int(character.y/self.h), int((character.y + character.h)/self.h) + 1):
                if self.block_array[iy][ix] and self.block_array[iy][ix].is_hit:
                    character.vx = 0 # 壁とぶつかると横方向の速度をゼロにする
                    character.x = (ix + 1)*self.w
                    break
        else: # 右側との衝突判定
            ix = int((character.x + character.w)/self.w)
            for iy in range(int(character.y/self.h), int((character.y + character.h)/self.h) + 1):
                if self.block_array[iy][ix] and self.block_array[iy][ix].is_hit:
                    character.vx = 0 # 壁とぶつかると横方向の速度をゼロにする
                    character.x = ix*self.w - character.w - 1
                    break

        # キャラクターの上下の衝突判定
        character.updateY()
        if character.vy < 0: # 上部との衝突判定
            iy = int(character.y/self.h)
            for ix in range(int(character.x/self.w), int((character.x + character.w)/self.w) + 1):
                if self.block_array[iy][ix] and self.block_array[iy][ix].is_hit:
                    character.vy = -0.5*character.vy # 頭をぶつけて少し跳ね返る
                    character.y = (iy + 1)*self.h
                    break
        else: # 下部との衝突判定
            character.is_fly = True
            iy = int((character.y + character.h)/self.h)
            for ix in range(int(character.x/self.w), int((character.x + character.w)/self.w) + 1):
                if self.block_array[iy][ix] and self.block_array[iy][ix].is_hit:
                    character.vy = 0
                    character.y = iy*self.h - character.h - 1
                    character.is_fly = False
                    break

    # マップの描画
    def draw(self, surface, imageManager):
        for block_list in self.block_array:
            for block in block_list:
                if block:
                    block.draw(surface, imageManager)
