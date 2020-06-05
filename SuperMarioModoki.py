# coding: utf-8
import pygame
from pygame.locals import *
import sys


# 定数
FPS = 60                            # 1秒間の描画回数
SCREEN_WIDTH = 800                  # ゲーム画面の横サイズ
SCREEN_HEIGHT = 600                 # ゲーム画面の縦サイズ
GAME_NAME = "Super Mario Modoki"    # ゲーム名
SCREEN_CLEAR_COLOR = (255,255,255)  # 画面をクリアする色

PLAY_BACK_COLOR = (170,170,250)     # ゲームプレイ時の背景の色
HEAD_REFLECT_POWER = 0.5            # 頭がブロックにぶつかった時の反発係数
G = 1.0                             # 重力加速度

BLOCK_W = 50                        # ブロックの横サイズ
BLOCK_H = 50                        # ブロックの縦サイズ
BLOCK_BACK_COLOR = (80,80,80)       # ブロックの影の色
BLOCK_EDGE_COLOR = (0,0,0)          # ブロックの縁の色
BLOCK_EDGE_THICKNESS = 1            # ブロックの縁の太さ
BLOCK_BACK_DX = 10                  # ブロックの影の相対X座標
BLOCK_BACK_DY = 10                  # ブロックの影の相対Y座標

PLAYER_W = 50                       # プレイヤーの横サイズ
PLAYER_H = 50                       # プレイヤーの縦サイズ
PLAYER_ANIME_INTERVAL = 10          # プレイヤーのアニメーションフレームの間隔
PLAYER_FLASH_INTERVAL = 4           # プレイヤーの無敵状態の点滅フレームの間隔
PLAYER_MAX_INVINCIBLE_TIME = 60     # プレイヤーの無敵状態の持続フレーム数
PLAYER_CHANGE_H = 40                # プレイヤーの巨大状態のプレイヤーの縦サイズの変化
PLAYER_JUMP_POWER = 15              # プレイヤーのジャンプの初速度
PLAYER_GAMEOVER_JUMP_POWER = 20     # プレイヤーのゲームオーバー時のジャンプの初速度
PLAYER_AX = 2                       # プレイヤーの左右移動の加速度
PLAYER_SLIP_DECAY_VELOCITY = 0.5    # プレイヤーの非入力状態での速度減衰
PLAYER_MAX_SPEED_X = 7              # プレイヤーの左右移動の最大速度
PLAYER_MAX_SPEED_Y = 30             # プレイヤーの上下移動の最大速度
PLAYER_GAMEOVER_STOP_TIME = 15      # プレイヤーのゲームオーバー時の硬直フレーム数

ENEMY_W = 50                        # 敵の横サイズ
ENEMY_H = 50                        # 敵の縦サイズ
ENEMY_ANIME_INTERVAL = 10           # 敵のアニメーションフレームの間隔
ENEMY_SPEED_X = 2                   # 敵の左右移動速度
ENEMY_MAX_SPEED_Y = 30              # 敵の上下移動の最大速度
ENEMY_DELETE_TIME = 30              # 敵が踏みつけられて消えるまでのフレーム数
ENEMY_PUSH_UP_PLAYER_POWER = 10     # 敵が踏みつけられたときにプレイヤーを突き上げる初速度
ENEMY_TREADED_AREA = 0.5            # 敵の踏みつけられ判定の範囲の割合
ENEMY_TREADED_COLOR = (240,100,0)   # 敵が踏みつけられたときの色
ENEMY_TREADED_H = 15                # 敵が踏みつけられたときの縦サイズ

ITEM_W = 30                         # アイテムの横サイズ
ITEM_H = 30                         # アイテムの縦サイズ
ITEM_SPEED_X = 5                    # アイテムの左右移動速度
ITEM_MAX_SPEED_Y = 20               # アイテムの上下移動の最大速度


# 初期化
pygame.init() # pygameを使えるようにする
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # ゲーム画面のサイズを設定
pygame.display.set_caption(GAME_NAME) # ゲーム画面上部にゲーム名を表示


""" キー入力管理クラス """
class KeyManager:
    """ コンストラクタ """
    def __init__(self):
        self.key = pygame.key.get_pressed()
        self.key_old = self.key

    """ キー入力状態の更新 """
    def update(self):
        self.key_old = self.key
        self.key = pygame.key.get_pressed()

    """ 指定したキーが押されているかを取得する """
    def get_key(self, name):
        return self.key[name]

    """ 指定したキーが押された瞬間かを取得する """
    def get_key_down(self, name):
        return self.key[name] and not self.key_old[name]


""" 画像管理クラス """
class ImageManager:
    """ コンストラクタ """
    def __init__(self):
        self.images = {} # 画像を保持する辞書

    """ 指定したパスの画像を名前を付けて読み込む """
    def load(self, name, path):
        self.images[name] = pygame.image.load(path)


# 各便利モジュール
keyManager = KeyManager()       # キー入力を管理する
imageManager = ImageManager()   # 画像を管理する
clock = pygame.time.Clock()     # フレームレート制御用


""" 物体 """
class Object:
    """ コンストラクタ """
    def __init__(self, x, y, w, h, max_speed_x, max_speed_y):
        self.x, self.y, self.w, self.h = x, y, w, h # 位置とサイズを初期化
        self.max_speed_x = max_speed_x  # 横方向の最大速度を設定
        self.max_speed_y = max_speed_y  # 縦方向の最大速度を設定
        self.frame_count = 0    # 経過フレーム数
        self.vx = self.vy = 0   # 速度
        self.ax = 0             # 横方向の加速度
        self.ay = G             # 縦方向の加速度は重力加速度
        self.is_fly = False     # 空中にあるフラグ
        self.is_deleted = False # 削除されるべきかフラグ

    """ 物体のX座標を更新 """
    def updateX(self):
        self.vx += self.ax
        self.vx = min(self.max_speed_x, self.vx)
        self.vx = max(-self.max_speed_x, self.vx)
        self.x += self.vx

    """ 物体のY座標を更新 """
    def updateY(self):
        if self.is_fly:
            self.vy += self.ay
            self.vy = min(self.max_speed_y, self.vy)
            self.vy = max(-self.max_speed_y, self.vy)
            self.y += self.vy

    """ 物体同士の衝突判定 """
    def collision_detection(self, object):
        return (object.x + object.w - self.x)*(self.x + self.w - object.x) >= 0 \
            and (object.y + object.h - self.y)*(self.y + self.h - object.y) >= 0


""" ブロック """
class Block:
    """ コンストラクタ """
    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h # 位置とサイズを初期化

    """ ブロックの描画 """
    def draw(self):
        pygame.draw.rect(screen, BLOCK_BACK_COLOR, Rect(self.x + BLOCK_BACK_DX, self.y + BLOCK_BACK_DY, self.w, self.h))
        screen.blit(pygame.transform.scale(imageManager.images["block"], (self.w, self.h)), (self.x, self.y))
        pygame.draw.rect(screen, BLOCK_EDGE_COLOR, Rect(self.x, self.y, self.w, self.h), BLOCK_EDGE_THICKNESS)


""" プレイヤー """
class Player(Object):
    """ コンストラクタ """
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, PLAYER_MAX_SPEED_X, PLAYER_MAX_SPEED_Y)
        self.is_invincible = False  # ダメージを受けて無敵状態であるフラグ
        self.invincible_time = 0    # 無敵継続時間
        self.is_big = False         # 巨大化状態であるかフラグ
        self.can_action = True      # キー入力によるアクションを受け付けるかフラグ

    """ キー入力によるアクションを受け付けるかフラグを設定 """
    def set_can_action(self, can_action):
        self.can_action = can_action

    """ ジャンプ処理 """
    def jump(self, power):
        self.vy = -power    # ジャンプの初速を与える
        self.is_fly = True  # 空中にいるフラグを立てる (空中でジャンプできないようにするため)

    """ ダメージを受ける処理 """
    def damage(self):
        if not self.is_invincible: # 無敵状態でなければダメージを受ける
            if self.is_big: # 巨大化状態ならば小さくなる
                self.is_big = False
                self.is_invincible = True
                self.h -= PLAYER_CHANGE_H
                self.y += PLAYER_CHANGE_H
            else: # 巨大化状態でなければゲームオーバー
                self.is_deleted = True

    """ アイテムを取った時の処理 """
    def powerUp(self):
        if not self.is_big:
            self.is_big = True
            self.h += PLAYER_CHANGE_H
            self.y -= PLAYER_CHANGE_H

    """ プレイヤーの状態の更新 """
    def update(self):
        # キー入力による状態の更新
        if self.can_action:
            if keyManager.get_key_down(K_SPACE) and not self.is_fly: # ジャンプする
                self.jump(PLAYER_JUMP_POWER)
            if keyManager.get_key(K_RIGHT): # 右方向に加速度をつける
                self.ax = PLAYER_AX
            elif keyManager.get_key(K_LEFT): # 左方向に加速度をつける
                self.ax = -PLAYER_AX
            else: # 入力していないとき滑りながら徐々に停止
                self.ax = 0
                if self.vx > 0:
                    self.vx -= PLAYER_SLIP_DECAY_VELOCITY
                    self.vx = max(0, self.vx)
                else:
                    self.vx += PLAYER_SLIP_DECAY_VELOCITY
                    self.vx = min(0, self.vx)

        # 無敵状態の更新
        if self.is_invincible:
            self.invincible_time += 1
            if self.invincible_time == PLAYER_MAX_INVINCIBLE_TIME:
                self.is_invincible = False
                self.invincible_time = 0

        self.frame_count += 1

    """ プレイヤーの描画 """
    def draw(self):
        if not self.is_invincible or (self.invincible_time//PLAYER_FLASH_INTERVAL) % 2 == 0: # 無敵の間点滅する
            anime = (self.frame_count//PLAYER_ANIME_INTERVAL) % 2
            if self.is_big:
                img = "player_big_1" if anime == 0 else "player_big_2"
            else:
                img = "player_1" if anime == 0 else "player_2"
            screen.blit(pygame.transform.scale(imageManager.images[img], (self.w, self.h)), (self.x, self.y))


""" 敵 """
class Enemy(Object):
    """ コンストラクタ """
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, ENEMY_SPEED_X, ENEMY_MAX_SPEED_Y)
        self.is_right = True    # 進行方向が右であるかフラグ
        self.is_treaded = False # 踏まれたかフラグ

    """ 敵の状態の更新 """
    def update(self):
        if self.is_treaded:
            if self.frame_count == ENEMY_DELETE_TIME:
                self.is_deleted = True
        else:
            if self.vx == 0: # 速度がゼロになる (壁に当たる) と方向転換する
                self.is_right = not self.is_right
                self.vx = ENEMY_SPEED_X if self.is_right else -ENEMY_SPEED_X
        self.frame_count += 1

    """ 敵の描画 """
    def draw(self):
        if self.is_treaded: # 踏まれていれば薄くなる
            pygame.draw.rect(screen, ENEMY_TREADED_COLOR, Rect(self.x, self.y + self.h - ENEMY_TREADED_H, self.w, ENEMY_TREADED_H))
        else:
            img = "enemy_1" if (self.frame_count//ENEMY_ANIME_INTERVAL) % 2 == 0 else "enemy_2"
            screen.blit(pygame.transform.scale(imageManager.images[img], (self.w, self.h)), (self.x, self.y))

    """ プレイヤーとの衝突処理 """
    def collision(self, player):
        if not self.is_treaded and self.collision_detection(player): # 踏まれていなければ判定がある
            if self.y <= player.y + player.h <= self.y + ENEMY_TREADED_AREA*self.h: # 敵の上部がプレイヤーの下部に触れると踏まれる
                player.jump(ENEMY_PUSH_UP_PLAYER_POWER) # 踏んだプレイヤーを押し上げる
                self.is_treaded = True
                self.vx = 0
                self.frame_count = 0
            else:
                player.damage()


""" アイテム """
class Item(Object):
    """ コンストラクタ """
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h, ITEM_SPEED_X, ITEM_MAX_SPEED_Y)
        self.is_right = True # 進行方向が右であるかフラグ

    """ アイテムの状態の更新 """
    def update(self):
        if self.vx == 0: # 速度がゼロになる (壁に当たる) と方向転換する
            self.is_right = not self.is_right
            self.vx = ITEM_SPEED_X if self.is_right else -ITEM_SPEED_X

    """ アイテムの描画 """
    def draw(self):
        screen.blit(pygame.transform.scale(imageManager.images["item"], (self.w, self.h)), (self.x, self.y))

    """ プレイヤーとの衝突処理 """
    def collision(self, player):
        if self.collision_detection(player):
            self.is_deleted = True # 取ったアイテムは削除する
            player.powerUp() # プレイヤーはパワーアップする


""" マップ """
class Map:
    """ コンストラクタ """
    def __init__(self, block_id_array, w, h):
        self.w, self.h = w, h       # ブロックの横幅と縦幅を設定する
        self.set(block_id_array)    # マップデータをブロックの集合に変換する

    """ ブロックを生成する関数 """
    def blockFactory(self, id, ix, iy):
        if id == 0:
            return None
        else:
            return Block(ix*self.w, iy*self.h, self.w, self.h)

    """ マップ情報をセットする """
    def set(self, block_id_array):
        self.block_array = []
        for iy, block_id_list in enumerate(block_id_array):
            self.block_array.append(
                [
                    self.blockFactory(block_id, ix, iy)
                    for ix, block_id in enumerate(block_id_list)
                ]
            )

    """ 物体との衝突判定を行い位置を更新 """
    def collision_update(self, object):
        # 左右の衝突判定
        object.updateX()
        if object.vx < 0: # 左側との衝突判定
            ix = int(object.x/self.w)
            for iy in range(int(object.y/self.h), int((object.y + object.h - 1)/self.h) + 1):
                if self.block_array[iy][ix]:
                    object.vx = 0 # 壁とぶつかると横方向の速度をゼロにする
                    object.x = (ix + 1)*self.w
                    break
        else: # 右側との衝突判定
            ix = int((object.x + object.w)/self.w)
            for iy in range(int(object.y/self.h), int((object.y + object.h - 1)/self.h) + 1):
                if self.block_array[iy][ix]:
                    object.vx = 0 # 壁とぶつかると横方向の速度をゼロにする
                    object.x = ix*self.w - object.w
                    break

        # 上下の衝突判定
        object.updateY()
        if object.vy < 0: # 上部との衝突判定
            iy = int(object.y/self.h)
            for ix in range(int(object.x/self.w), int((object.x + object.w - 1)/self.w) + 1):
                if self.block_array[iy][ix]:
                    object.vy = -HEAD_REFLECT_POWER*object.vy # 頭をぶつけて少し跳ね返る
                    object.y = (iy + 1)*self.h
                    break
        else: # 下部との衝突判定
            object.is_fly = True
            iy = int((object.y + object.h)/self.h)
            for ix in range(int(object.x/self.w), int((object.x + object.w - 1)/self.w) + 1):
                if self.block_array[iy][ix]:
                    object.vy = 0
                    object.y = iy*self.h - object.h
                    object.is_fly = False
                    break

    """ マップの描画 """
    def draw(self):
        for block_list in self.block_array:
            for block in block_list:
                if block:
                    block.draw()


""" タイトルシーン """
class TitleScene:
    """ コンストラクタ """
    def __init__(self):
        self.frame_count = 0                        # 経過フレーム数
        self.player = Player(150, 200, 200, 200)    # プレイヤーを生成
        self.player.set_can_action(False)           # キー入力によるアクションを無効にする
        self.enemy = Enemy(450, 200, 200, 200)      # 敵を生成

    """ タイトル画面の更新 """
    def update(self):
        self.player.update()    # プレイヤーの状態の更新
        self.enemy.update()     # 敵の状態の更新

        next_scene_name = None
        if keyManager.get_key_down(K_SPACE): # スペースキーを押すとゲームスタート
            next_scene_name = "play"
        return next_scene_name

    """ タイトル画面の描画 """
    def draw(self):
        screen.blit(imageManager.images["title"], (100, 50))
        self.player.draw()  # プレイヤーの描画
        self.enemy.draw()   # 敵の描画
        screen.blit(imageManager.images["please"], (150, 450))


""" プレイシーン """
class PlayScene:
    """ コンストラクタ """
    def __init__(self):
        self.frame_count = 0    # 経過フレーム数
        self.state = "play"     # ゲーム状態をフラグ管理
        self.create()           # ゲーム内オブジェクトを生成

    """ ゲーム内オブジェクトを初期化 """
    def reset(self):
        self.map = None
        self.player = None
        self.enemies = []
        self.items = []

    """ 敵を生成 """
    def create_enemy(self, x, y):
        self.enemies.append(Enemy(x, y, ENEMY_W, ENEMY_H))

    """ アイテムを生成 """
    def create_item(self, x, y):
        self.items.append(Item(x, y, ITEM_W, ITEM_H))

    """ ゲーム内オブジェクトを生成 """
    def create(self):
        self.reset()
        block_id_array = [ # マップデータ
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
        self.map = Map(block_id_array, BLOCK_W, BLOCK_H)    # マップを生成
        self.player = Player(300, 100, PLAYER_W, PLAYER_H)  # プレイヤーを生成
        self.create_enemy(100, 100) # 敵を生成
        self.create_enemy(300, 300) # 敵を生成
        self.create_enemy(500, 400) # 敵を生成
        self.create_item(100, 400)  # アイテムを生成

    """ ゲーム状態を遷移 """
    def change_state(self, state):
        self.state = state
        self.frame_count = 0

    """ プレイシーン全体を更新 """
    def update(self):
        next_scene_name = None
        if self.state == "play": # ゲーム状態が「ゲームプレイ」であるときの処理
            self.player.update() # プレイヤーの状態の更新
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

            self.map.collision_update(self.player) # プレイヤーとマップの衝突処理
            for other in self.enemies+self.items:
                self.map.collision_update(other) # プレイヤー以外の物体とマップの衝突処理

            for other in self.enemies+self.items:
                other.collision(self.player) # プレイヤーとプレイヤー以外の物体の衝突処理

            if self.player.is_deleted: # プレイヤーがやられたときの処理
                self.change_state("gameover_motion") # ゲーム状態を「ゲームオーバーモーション」に変更する
            if self.enemies == []: # 敵を全員倒したときの処理
                self.change_state("clear") # ゲーム状態を「ゲームクリア」に変更する

        elif self.state == "gameover_motion": # ゲーム状態が「ゲームオーバーモーション」であるときの処理
            # プレイヤーがやられてから数フレーム経過したらプレイヤーが飛ぶ
            if self.frame_count == PLAYER_GAMEOVER_STOP_TIME:
                self.player.jump(PLAYER_GAMEOVER_JUMP_POWER)
            if self.frame_count >= PLAYER_GAMEOVER_STOP_TIME:
                self.player.updateY()
                if self.player.y > SCREEN_HEIGHT: # プレイヤーが画面外にいくとゲームオーバー画面に変更する
                    self.change_state("gameover")

        elif self.state == "clear" or self.state == "gameover": # ゲーム状態が「ゲームクリア」か「ゲームオーバー」であるときの処理
            if keyManager.get_key_down(K_SPACE): # スペースキーを押すとゲームをはじめからやり直す
                next_scene_name = "title"

        self.frame_count += 1
        return next_scene_name

    """ プレイシーン全体を描画 """
    def draw(self):
        screen.fill(PLAY_BACK_COLOR) # 背景を青空で塗る
        self.map.draw() # マップの描画
        for other in self.enemies+self.items:
            other.draw() # プレイヤー以外の物体の描画
        self.player.draw() # プレイヤーの描画

        if self.state == "clear": # ゲームクリアと表示
            screen.blit(imageManager.images["clear"], (200, 50))
        elif self.state == "gameover": # ゲームオーバーと表示
            screen.blit(imageManager.images["gameover"], (0,50))


""" ゲーム """
class Game:
    """ コンストラクタ """
    def __init__(self, initial_scene_name):
        self.scene = self.getScene(initial_scene_name) # 初期シーンの準備

        # 画像の読み込み
        imageManager.load("title", "img/title.png")
        imageManager.load("please", "img/please.png")
        imageManager.load("block", "img/block.png")
        imageManager.load("item", "img/item.png")
        imageManager.load("clear", "img/clear.png")
        imageManager.load("gameover", "img/gameover.png")
        imageManager.load("player_1", "img/player_1.png")
        imageManager.load("player_2", "img/player_2.png")
        imageManager.load("player_big_1", "img/player_big_1.png")
        imageManager.load("player_big_2", "img/player_big_2.png")
        imageManager.load("enemy_1", "img/enemy_1.png")
        imageManager.load("enemy_2", "img/enemy_2.png")

    """ シーン名からシーンを取得 """
    def getScene(self, scene_name):
        if scene_name == "title":
            return TitleScene()
        elif scene_name == "play":
            return PlayScene()
        else:
            return None

    """ メインループ """
    def loop(self):
        while self.scene:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # 閉じるボタンを押せば終了
                    return
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: # EACAPEキーを押せば終了
                    return

            keyManager.update() # キー入力状態の更新
            next_scene_name = self.scene.update() # シーンの更新

            screen.fill(SCREEN_CLEAR_COLOR) # 背景をクリア
            self.scene.draw() # シーンを描画
            pygame.display.update() # 描画を反映

            clock.tick(FPS) # フレームレートを固定するために一定時間待機

            if next_scene_name: # シーン遷移
                self.scene = self.getScene(next_scene_name)


game = Game("title") # ゲームを準備
game.loop() # ゲームのメインループを開始する

# 終了処理
pygame.quit()
sys.exit(0)
