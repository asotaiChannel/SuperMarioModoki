# coding: utf-8

from src.gameManager import GameManager


### プログラムはここから開始される ###
if __name__ == "__main__":
    gm = GameManager() # ゲーム全体を管理するマネージャの準備
    gm.play() # ゲームマネージャの起動
