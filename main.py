from make_table import MakeTable  # デバック様
from utils import *
from shift_fix_ import shift_fixer
from eval_shift import eval_shift_

if __name__ == "__main__":
    d = MakeTable("main.xlsm")
    Sf = shift_fixer()
    Cf = CrossOver()
    Ev = eval_shift_()

    # 1日何人のシフトを入れるか
    max_shifts_per_day = 3

    # 親の保存
    parent = []

    # 第一世代を100個作る
    for i in range(100):
        # 第一世代の生成
        kiso_copy, Sun, sex, trainee, gogen, shift_times = d.first_gene()

        # 出勤数の修正
        kiso_copy = Sf.shift_fix(kiso_copy, shift_times, Sun, sex, max_shifts_per_day)

        # 評価
        score = Ev.evaluation_f(kiso_copy, Sun, sex, trainee, gogen, shift_times, max_shifts_per_day)

        # 第一世代を格納
        parent.append([score, kiso_copy])

    # 上位個体数
    elite_length = 20
    # 世代数
    gene_length = 50

    # 一様交叉確率
    ep = 0.5
    # 突然変異確率
    sd = 0.05
    # スコア更新しなかった回数保存用
    best_num_flag = 0
    for i in range(gene_length):
        # 点数で並び替え
        parent = sorted(np.array(parent, dtype=object), key=lambda x: -x[0])
        # 上位個体を選別
        parent = parent[:elite_length]

        # 最高得点の更新
        if i == 0 or top[0] < parent[0][0]:
            top = parent[0]
            # スコア更新時リセット
            best_num_flag = 0
        else:
            parent.append(top)
            best_num_flag += 1
            # ８回最高スコア更新なかったら処理終了
            if best_num_flag > 7:
                print("8回最高スコアが更新されませんでした")
                break

        # 各世代
        print("第" + str(i + 1) + "世代")
        # 各世代の最高得点の表示
        print(top[0])
        print(np.array(top[1]))

        # 子世代
        children = []

        # 遺伝子操作
        for k1, v1 in enumerate(parent):
            for k2, v2 in enumerate(parent):
                if k1 < k2:
                    # 一様交叉
                    ch1, ch2 = Cf.crossover(ep, sd, v1[1], v2[1])

                    # 出勤数の修正
                    # ch1の出勤数の修正
                    ch1 = Sf.shift_fix(ch1, shift_times, Sun, sex, max_shifts_per_day)
                    # ch2の出勤数の修正
                    ch2 = Sf.shift_fix(ch2, shift_times, Sun, sex, max_shifts_per_day)

                    # 評価
                    score1 = Ev.evaluation_f(ch1, Sun, sex, trainee, gogen, shift_times, max_shifts_per_day)
                    score2 = Ev.evaluation_f(ch2, Sun, sex, trainee, gogen, shift_times, max_shifts_per_day)

                    # 子孫を格納
                    children.append([score1, ch1])
                    children.append([score2, ch2])

        # 子を親にコピー
        parent = children.copy()

    x = np.array(top[1], dtype=object)  # オブジェクト型の配列に変換

    # 条件に基づいて値を置換
    x[x == 1] = "B"
    x[x == 0] = ""
    x[x == 2] = "休"
    x[x == 3] = "A"
    x[x == 4] = "B"

    num_rows, num_cols = x.shape

    for kk in range(num_cols):
        # 全員休みの時はスキップ
        if np.sum(x[:, kk] == "休") == num_rows:
            continue

        # すでに5時入りがいたらスキップ
        if np.any(x[:, kk] == "A"):
            continue

        # 女性の数をカウント
        onna = np.sum((x[:, kk] == "B") & (sex == "女"))

        if onna == 1:
            # 女性のステータスを更新
            women_indices = np.where((x[:, kk] == "B") & (sex == "女"))[0]
            if women_indices.size > 0:
                x[women_indices[0], kk] = "A"

        elif onna in [2, 3]:
            # ランダムに一人の女性のステータスを更新
            women_indices = np.where((x[:, kk] == "B") & (sex == "女"))[0]
            if women_indices.size > 0:
                chosen_index = np.random.choice(women_indices)
                x[chosen_index, kk] = "A"

    z = Write_table()
    za = z.write_excel(x)