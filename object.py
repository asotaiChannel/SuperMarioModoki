# coding: utf-8

# 定数の定義
MAX_SPEED_X = 30 # 横方向の最大速度制限
MAX_SPEED_Y = 30 # 縦方向の最大速度制限
G = 1.0 # 重力加速度


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
