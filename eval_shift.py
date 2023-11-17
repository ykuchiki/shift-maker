import numpy as np


class eval_shift_:
    def __init__(self):
        pass

    def evaluation_f(self, kiso_copy, Sun, sex, trainee, gogen, shift_times, max_shifts_per_day):
        kiso_copy = kiso_copy
        Sun = Sun
        sex = sex
        trainee = trainee
        gogen = gogen
        shift_times = [[row[i] for row in shift_times] for i in range(len(shift_times[0]))]

        days = kiso_copy.shape[1]
        num_employees = kiso_copy.shape[0]
        score = int(0)

        # 出勤を0、休みを1に変換
        ho = np.where(kiso_copy == 0, 2, kiso_copy)
        ho = np.where(ho == 1, 0, ho)
        ho = np.where(ho == 2, 1, ho)
        ho = np.where(ho == 3, 0, ho)
        ho = np.where(ho == 4, 0, ho)

        # 列方向の評価
        for k in range(num_employees):
            x = ''.join(ho[k, :].astype(str))

            # 各週の出勤日数を計算
            s1 = Sun[0] - np.count_nonzero(ho[k, :Sun[0]] == 0)
            s2 = (Sun[1] - Sun[0]) - np.count_nonzero(ho[k, Sun[0]:Sun[1]] == 0)
            s3 = (Sun[2] - Sun[1]) - np.count_nonzero(ho[k, Sun[1]:Sun[2]] == 0)
            s4 = (Sun[3] - Sun[2]) - np.count_nonzero(ho[k, Sun[2]:Sun[3]] == 0)

            s5, s6 = 0, 0
            if len(Sun) >= 4:
                s5 = (days - Sun[3]) - np.count_nonzero(ho[k, Sun[3]:days] == 0)
            if len(Sun) == 5:
                s5 = (Sun[4] - Sun[3]) - np.count_nonzero(ho[k, Sun[3]:Sun[4]] == 0)
                s6 = (days - Sun[4]) - np.count_nonzero(ho[k, Sun[4]:days] == 0)

            # 連勤などの評価ロジック
            # 3連勤以上の減点
            score += sum((1 - len(i)) ** 4 * -2 for i in x.split("1") if len(i) >= 3)
            # 2連勤以上の減点
            score += sum((1 - len(i)) ** 2 * -1 for i in x.split("1") if len(i) >= 2)

            # 出勤日数に基づく評価
            # 週ごとのシフト希望に応じた評価
            total_shifts = np.count_nonzero(ho[k, :] == 0)  # 出勤日数
            if shift_times[k] == 1:  # 週1の場合
                if total_shifts not in [3, 4, 5]:
                    score -= (4 - total_shifts) ** 4
                # 各週のシフト数に基づく減点
                score -= 50 * sum(s > 1 for s in [s1, s2, s3, s4, s5] if len(Sun) >= 4)
                score -= 50 * (s6 > 1 if len(Sun) == 5 else 0)
            elif shift_times[k] == 2:  # 週2の場合
                if total_shifts < 5 or total_shifts > 10:
                    score -= (9 - total_shifts) ** 2
                # 各週のシフト数に基づく減点
                score -= 50 * sum(s > 2 for s in [s1, s2, s3, s4, s5] if len(Sun) >= 4)
                score -= 50 * (s6 > 2 if len(Sun) == 5 else 0)
            elif shift_times[k] == 3:  # 週3の場合
                if total_shifts < 8 or total_shifts > 15:
                    score -= (10 - total_shifts) ** 2
            elif shift_times[k] == "隔週":  # 隔週の場合
                if total_shifts not in [2, 3]:
                    score -= (2 - total_shifts) ** 4

        # 行方向の評価
        for kk in range(days):
            # 全員休みの日はスキップ
            if np.sum(ho[:, kk]) == num_employees * 2:
                continue


            # max_shifts_per_day人かどうか
            on_shift = np.sum((ho[:, kk] == 0))
            if on_shift != max_shifts_per_day:
                score -= 50 * on_shift


            # その日に出勤している研修生の数をカウント
            trainee_on_shift = np.sum((ho[:, kk] == 0) & (trainee == "YES"))

            # 研修生が2人以上いる場合にスコアを減点
            if trainee_on_shift >= 2:
                score -= 25 * trainee_on_shift

            # その日に出勤している女性の数をカウント
            women_on_shift = np.sum((ho[:, kk] == 0) & (sex == "女"))

            # 女性が一人もいない場合にスコアを減点
            if women_on_shift == 0:
                score -= 25

        """for kk in Sun:
            # 土曜日のインデックスを調整（日曜日がリストの最初にある場合）
            saturday_index = kk - 1 if kk > 0 else days - 1

            # 全員休みの日はスキップ
            if np.sum(ho[:, saturday_index]) == num_employees * 2:
                continue

            # その日に出勤している男性の数をカウント
            men_on_shift = np.sum((ho[:, saturday_index] == 0) & (sex == "男"))

            # 男性が2人未満の場合にスコアを減点
            if men_on_shift < 2:
                score -= 50"""

        return score