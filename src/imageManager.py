# coding: utf-8

import pygame


# ゲームで使用する画像を管理するクラス
class ImageManager:
    # 画像を管理するマネージャの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self):
        self.images = {} # 画像を保持する辞書

    # 指定したパスの画像を名前を付けて読み込む
    def load(self, name, path):
        self.images[name] = pygame.image.load(path)

    # 読み込んだ画像を削除する
    def delete(self, name):
        if name in self.images:
            self.images.pop(name)
