# coding: utf-8

import pygame
from pygame.locals import *

from map import Map
from player import Player
from goomba import Goomba
from mushroom import Mushroom


# 定数の定義
GAME_PLAY_MODE = 0 # ゲームプレイ中であるフラグ
GAME_OVER_MOTION_MODE = 1 # ゲームオーバーモーション中であるフラグ
GAME_CLEAR_MODE = 2 # ゲームクリア画面であるフラグ
GAME_OVER_MODE = 3 # ゲームオーバー画面であるフラグ


# ゲームプレイシーンを管理するクラス
class GamePlayScene:
    # シーンの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, im):
        self.im = im # ユーザ入力を受け付けるマネージャ
        self.state = GAME_PLAY_MODE # ゲーム状態をフラグ管理する
        self.t = 0 # 時間 (アニメーションなどに使う)
        self.create() # ゲーム内オブジェクトを生成する

        # テキストの準備
        font = pygame.font.SysFont(None, 100)
        self.gameClearText = font.render("CLEAR", True, (255,0,0))
        self.gameOverText = font.render("GAME OVER", True, (0,0,0))

    # ゲーム内オブジェクトを生成する
    def create(self):
        self.map = Map(50, 50) # マップを生成
        self.mario = Player(300, 100, 50, 50) # マリオを生成
        self.enemies = [Goomba(100, 100, 50, 50), Goomba(300, 200, 50, 50), Goomba(500, 500, 50, 50)] # 敵リストにクリボーを生成
        self.items = [Mushroom(100, 400, 30, 30)] # アイテムリストにキノコを生成

    # シーン全体を更新する関数
    def update(self):
        if self.state == GAME_PLAY_MODE: # ゲーム状態が「ゲームプレイ」であるときの処理
            self.mario.update(self.im) # マリオの状態の更新
            i = 0
            while i < len(self.enemies):
                if self.enemies[i].is_deleted: # 用済みの敵はリストから削除していく
                    self.enemies.pop(i)
                else:
                    self.enemies[i].update() # 敵の状態の更新
                    i += 1
            i = 0
            while i < len(self.items):
                if self.items[i].is_deleted: # 用済みのアイテムはリストから削除していく
                    self.items.pop(i)
                else:
                    self.items[i].update() # アイテムの状態の更新
                    i += 1

            self.map.collisionDetection(self.mario) # マリオとマップの衝突処理
            for other in self.enemies+self.items:
                self.map.collisionDetection(other) # マリオ以外の物体とマップの衝突処理

            for other in self.enemies+self.items:
                other.collisionDetection(self.mario) # マリオとマリオ以外の物体の衝突処理

            if self.mario.is_deleted: # マリオがやられたときの処理
                self.state = GAME_OVER_MOTION_MODE # ゲーム状態を「ゲームオーバーモーション」に変更する
                self.t = 0
            if self.enemies == []: # 敵を全員倒したときの処理
                self.state = GAME_CLEAR_MODE # ゲーム状態を「ゲームクリア」に変更する
        elif self.state == GAME_OVER_MOTION_MODE: # ゲーム状態が「ゲームオーバーモーション」であるときの処理
            # マリオがやられてから15フレーム経過したらマリオが飛ぶ
            if self.t == 15:
                self.mario.jump(20)
            if self.t >= 15:
                self.mario.updateY()
                if self.mario.y > 600: # マリオが画面外にいくとゲームオーバー画面に変更する
                    self.state = GAME_OVER_MODE
        elif self.state == GAME_CLEAR_MODE or self.state == GAME_OVER_MODE: # ゲーム状態が「ゲームクリア」か「ゲームオーバー」であるときの処理
            if self.im.isPushKeyNow(K_SPACE): # スペースキーを押すとゲームをはじめからやり直す
                self.state = GAME_PLAY_MODE # ゲーム状態を「ゲームプレイ」に変更する
                self.create() # ゲーム内オブジェクトを生成しなおす

        # 時間を進める
        self.t += 1
        if self.t == 2**16:
            self.t = 0

    # シーン全体を描画する関数
    def draw(self, surface):
        surface.fill((170, 170, 250)) # 背景を青空で塗る
        self.map.draw(surface) # マップの描画
        for other in self.enemies+self.items:
            other.draw(surface) # マリオ以外の物体の描画
        self.mario.draw(surface) # マリオの描画

        if self.state == GAME_CLEAR_MODE: # ゲームクリアと表示
            surface.blit(self.gameClearText, (40,30))
        elif self.state == GAME_OVER_MODE: # ゲームオーバーと表示
            surface.blit(self.gameOverText, (40,30))
