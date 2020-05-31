# coding: utf-8

import pygame
from pygame.locals import *

from object import Object


# クリボーを表現するクラス
class Goomba(Object):
    # クリボーの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 2) # 物体として初期化する
        self.is_right = True # 進行方向が右であるかフラグ
        self.is_treaded = False # 踏まれたかフラグ

    # クリボーの状態の更新
    def update(self):
        if self.is_treaded:
            if self.t == 30: # 踏まれてから30フレーム経過するとゲーム画面から削除する
                self.is_deleted = True
        else:
            if self.vx == 0: # 速度がゼロになる (壁に当たる) と方向転換する
                self.is_right = not self.is_right
            if self.is_right:
                self.vx = 2
            else:
                self.vx = -2
        super().update() # 物体に共通する更新処理

    # クリボーの描画
    def draw(self, surface):
        if self.is_treaded: # 踏まれていれば薄くなる
            dy = 0.7*self.h
            pygame.draw.rect(surface, (200, 80, 0), Rect(self.x, self.y + dy, self.w, self.h - dy + 1))
        else:
            pygame.draw.rect(surface, (200, 80, 0), Rect(self.x, self.y, self.w, self.h + 1))

    # プレイヤー (今回はマリオ) との衝突処理をする
    def collisionDetection(self, player):
        if not self.is_treaded and super().collisionDetection(player): # 踏まれていなければ判定がある
            if self.y <= player.y + player.h <= self.y + 0.5*self.h: # クリボーの上部がプレイヤーの下部に触れると踏まれる
                player.jump(10) # 踏んだプレイヤーは軽くジャンプする
                self.is_treaded = True
                self.vx = 0
                self.t = 0
            else:
                player.damage()
