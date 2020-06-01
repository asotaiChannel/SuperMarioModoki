# coding: utf-8

import pygame
from pygame.locals import *

from .object import Object


# マリオを表現するクラス
class Player(Object):
    # マリオの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 7) # 物体として初期化する
        self.is_invincible = False # ダメージを受けて無敵状態であるフラグ
        self.invincible_time = 0 # 無敵継続時間
        self.is_big = False # 巨大化状態であるかフラグ

    # ジャンプ処理
    def jump(self, power):
        self.vy = -power # ジャンプの初速を与える
        self.is_fly = True # 空中にいるフラグを立てる (空中でジャンプできないようにするため)

    # ダメージを受ける処理
    def damage(self):
        if not self.is_invincible: # 無敵状態でなければダメージを受ける
            if self.is_big: # 巨大化状態ならば小さくなる
                self.is_big = False
                self.is_invincible = True
                self.h -= 40
                self.y += 40
            else: # 巨大化状態でなければゲームオーバー
                self.is_deleted = True

    # キノコを取った時の処理
    def powerUp(self):
        self.is_big = True
        self.h += 40
        self.y -= 40

    # マリオの状態の更新
    def update(self, im):
        # キー入力による状態の更新
        if im.isPushKeyNow(K_SPACE) and not self.is_fly: # 着地している状態のときにジャンプが可能
            self.jump(15) # ジャンプする
        self.ax = 0
        if im.isPushKey(K_RIGHT): # 右方向に加速度をつける
            self.ax += 2
        if im.isPushKey(K_LEFT): # 左方向に加速度をつける
            self.ax -= 2
        if self.ax == 0: # 入力していないとき滑りながら停止する処理
            if self.vx > 0:
                self.vx -= 0.5
                if self.vx < 0:
                    self.vx = 0
            else:
                self.vx += 0.5
                if self.vx > 0:
                    self.vx = 0

        # 無敵状態の更新
        if self.is_invincible:
            self.invincible_time += 1
            if self.invincible_time == 60: # ダメージを受けた後60フレーム無敵が続く
                self.is_invincible = False
                self.invincible_time = 0

        super().update() # 物体に共通する更新処理

    # マリオの描画
    def draw(self, surface, imageManager):
        if not self.is_invincible or (self.invincible_time//4) % 2 == 0: # 無敵の間点滅する
            if self.is_big:
                if (self.t//10) % 2 == 0:
                    surface.blit(imageManager.images["big_mario_1"], (self.x, self.y))
                else:
                    surface.blit(imageManager.images["big_mario_2"], (self.x, self.y))
            else:
                if (self.t//10) % 2 == 0:
                    surface.blit(imageManager.images["mario_1"], (self.x, self.y))
                else:
                    surface.blit(imageManager.images["mario_2"], (self.x, self.y))
