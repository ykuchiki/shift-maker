import numpy as np
# 例としてのスコアと2次元配列
score = -46
kiso_copy = np.array([
    [0, 0, 3, 1, 2, 0, 3, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 2, 1, 0],
    # ...（他の行のデータ）
])

# 空のリスト parent を作成
parent = []

# スコアと2次元配列を含むリストを parent に追加
parent.append([score, kiso_copy])

# テスト出力
print(parent[0][0])  # スコア (-46)
print(parent[0][1])  # 2次元配列 (kiso_copy)