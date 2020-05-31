# coding: utf-8

import pygame
from pygame.locals import *
import numpy as np
import sys


# 定数の定義
MAX_SPEED_X = 30 # 横方向の最大速度制限
MAX_SPEED_Y = 30 # 縦方向の最大速度制限
G = 1.0 # 重力加速度

GAME_PLAY_MODE = 0 # ゲームプレイ中であるフラグ
GAME_OVER_MOTION_MODE = 1 # ゲームオーバーモーション中であるフラグ
GAME_CLEAR_MODE = 2 # ゲームクリア画面であるフラグ
GAME_OVER_MODE = 3 # ゲームオーバー画面であるフラグ

FPS = 60 # 1秒間の描画階数


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


# 物体を表現するクラス
class Object:
    # 物体の準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, x, y, w, h, max_speed_X):
        self.x, self.y, self.w, self.h = x, y, w, h # 判定の位置とサイズを初期化
        self.max_speed_X = min(MAX_SPEED_X, max_speed_X) # 横方向の最大速度を設定する
        self.t = 0 # 時間 (アニメーションなどに使う)
        self.vx = self.vy = 0 # 速度
        self.ax = 0 # 横方向の加速度
        self.is_fly = False # 空中にあるフラグ
        self.is_deleted = False # 削除されるべきかフラグ

    # 物体に共通する更新処理
    def update(self):
        # 時間を進める
        self.t += 1
        if self.t == 2**16:
            self.t = 0

    # 物体のX座標を更新する
    def updateX(self):
        # x座標の更新
        self.vx += self.ax
        if self.vx > self.max_speed_X:
            self.vx = self.max_speed_X
        elif self.vx < -self.max_speed_X:
            self.vx = -self.max_speed_X
        self.x += self.vx

    # 物体のY座標を更新する
    def updateY(self):
        # y座標の更新
        if self.is_fly: # 空中にあるときだけ更新する
            self.vy += G
            if self.vy > MAX_SPEED_Y:
                self.vy = MAX_SPEED_Y
            elif self.vy < -MAX_SPEED_Y:
                self.vy = -MAX_SPEED_Y
            self.y += self.vy

    # 物体同士の衝突処理をする
    def collisionDetection(self, object):
        if (object.x + object.w - self.x)*(self.x + self.w - object.x) >= 0 \
        and (object.y + object.h - self.y)*(self.y + self.h - object.y) >= 0:
            return True
        return False


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
    def draw(self, surface):
        pygame.draw.rect(surface, (200, 0, 0), Rect(self.x, self.y, self.w, self.h + 1))

    # プレイヤー (今回はマリオ) との衝突処理をする
    def collisionDetection(self, player):
        if super().collisionDetection(player):
            self.is_deleted = True # 取ったキノコは削除する
            player.powerUp() # プレイヤーはパワーアップする


# ブロックを表現するクラス
class Block(Object):
    # ブロックの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, 0) # 物体として初期化する
        self.is_hit = True # 衝突判定があるかフラグ

    # ブロックの描画
    def draw(self, surface):
        pygame.draw.rect(surface, (80, 80, 80), Rect(self.x + 10, self.y + 10, self.w, self.h))
        pygame.draw.rect(surface, (150, 150, 150), Rect(self.x, self.y, self.w, self.h))
        pygame.draw.rect(surface, (0, 0, 0), Rect(self.x, self.y, self.w, self.h), 2)


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
    def draw(self, surface):
        if not self.is_invincible or (self.invincible_time//4) % 2 == 0: # 無敵の間点滅する
            pygame.draw.rect(surface, (40, 255, 255) if self.is_big else (247, 195, 156), Rect(self.x, self.y, self.w, self.h + 1))


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
    def draw(self, surface):
        for block_list in self.block_array:
            for block in block_list:
                if block:
                    block.draw(surface)


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


# ゲーム全体を管理するマネージャ
class GameManager:
    # マネージャの準備時に初めに呼ばれる関数 (コンストラクタ)
    def __init__(self):
        pygame.init() # pygameを使えるようにする
        pygame.display.set_mode((800, 600), 0, 32) # ゲーム画面のサイズを横800,縦600に設定
        pygame.display.set_caption("Super Mario Modoki") # ゲーム画面上部にゲーム名を表示
        self.surface = pygame.display.get_surface() # ゲーム画面の描画先を取得

        self.im = InputManager() # ユーザ入力を受け付けるマネージャの準備
        self.gps = GamePlayScene(self.im) # ゲームプレイシーンの準備

    # ゲーム全体を更新する関数
    def update(self):
        self.im.update() # ユーザ入力状態の更新
        self.gps.update() # ゲームプレイシーンの更新

    # ゲーム全体の更新結果をゲーム画面に描画する関数
    def draw(self):
        self.surface.fill((255, 255, 255)) # 背景を真っ白に塗る
        self.gps.draw(self.surface) # ゲームプレイシーンを描画する
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


### プログラムはここから開始される ###
if __name__ == "__main__":
    gm = GameManager() # ゲーム全体を管理するマネージャの準備
    gm.play() # ゲームマネージャの起動
