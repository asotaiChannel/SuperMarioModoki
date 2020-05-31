# coding: utf-8

import pygame

from inputManager import InputManager
from imageManager import ImageManager
from scene import Scene


# 定数の定義
FPS = 60 # 1秒間の描画階数


# ゲーム全体を管理するマネージャ
class GameManager:
    # マネージャの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self):
        pygame.init() # pygameを使えるようにする
        pygame.display.set_mode((800, 600), 0, 32) # ゲーム画面のサイズを横800,縦600に設定
        pygame.display.set_caption("Super Mario Modoki") # ゲーム画面上部にゲーム名を表示
        self.surface = pygame.display.get_surface() # ゲーム画面の描画先を取得

        self.inputManager = InputManager() # ユーザ入力を受け付けるマネージャの準備
        self.imageManager = ImageManager() # 画像を管理するマネージャの準備
        self.scene = Scene(self.inputManager, self.imageManager) # シーンの準備

    # ゲーム全体を更新する関数
    def update(self):
        self.inputManager.update() # ユーザ入力状態の更新
        self.scene.update() # ゲームプレイシーンの更新

    # ゲーム全体の更新結果をゲーム画面に描画する関数
    def draw(self):
        self.surface.fill((255, 255, 255)) # 背景を真っ白に塗る
        self.scene.draw(self.surface) # ゲームプレイシーンを描画する
        pygame.display.update() # 描画内容をゲーム画面に反映する

    # フレームレートを固定するために一定時間待機する関数
    def wait(self):
        pygame.time.wait(int(1000 / FPS))

    # ゲームマネージャを起動する関数
    def play(self):
        while True:
            self.update() # ゲーム全体を更新
            self.draw() # ゲーム全体を描画
            self.wait() # 一定時間待機
