import datetime
import numpy as np
import pandas as pd

from utils import Read_table

class MakeTable:
    def __init__(self, fname):

        self.ins = Read_table()
        self.df = self.ins.read_excel(fname)
        # print(self.df)

    def update_shift_times_with_min_values(self, shift_times, zero_count):
        for week_index in range(len(shift_times)):
            updated_week_shift_times = []
            for person_index, shift_time in enumerate(shift_times[week_index]):
                if isinstance(shift_time, int):
                    # シフト希望日数とシフト可能日数の小さい方を選択
                    updated_week_shift_times.append(min(shift_time, zero_count[week_index][person_index], 3))
                else:
                    # 非整数値（例：'隔週'）はそのまま保持
                    updated_week_shift_times.append(shift_time)
            shift_times[week_index] = updated_week_shift_times
    def process_weekly_shifts(self, kiso, sun_days):
        weekly_shifts = []
        start_day = 0
        for sun_day in sun_days:
            weekly_shifts.append(kiso[:, start_day:sun_day + 1])
            start_day = sun_day + 1
        if start_day < kiso.shape[1]:
            weekly_shifts.append(kiso[:, start_day:])
        return weekly_shifts

    def count_zeros_per_week(self, weekly_shifts):
        zeros_count_per_week = []
        for week_data in weekly_shifts:
            count_zeros = np.sum(week_data == 0, axis=1)  # 各週ごとに0の数をカウント
            zeros_count_per_week.append(count_zeros)
        return zeros_count_per_week

    def assign_alternate_weeks_shifts(self, kiso, Sun, shift_times, total_days):
        for k in range(kiso.shape[0]):  # 従業員の数だけループ
            if shift_times[0][k] == "隔週":  # 最初の週のシフト時間で隔週を確認
                # 最初のシフトをランダムに選択
                first_shift_week = np.random.choice([0, 1])  # 0: 1週目, 1: 2週目
                week_range = range(Sun[first_shift_week] + 1) if first_shift_week == 0 else range(
                    Sun[first_shift_week - 1] + 1, Sun[first_shift_week] + 1)
                available_days = np.where(kiso[k, week_range] == 0)[0]
                if available_days.size > 0:
                    first_shift_day = np.random.choice(available_days)
                    # 最初のシフトを割り当て
                    kiso[k, first_shift_day + (0 if first_shift_week == 0 else Sun[first_shift_week - 1] + 1)] = 1

                # 次のシフトの割り当て
                for next_week in range(first_shift_week + 2, len(Sun), 2):  # 隔週でシフトを割り当て
                    week_end = Sun[next_week] + 1 if next_week < len(Sun) - 1 else total_days
                    next_week_range = range(Sun[next_week - 1] + 1, week_end)
                    available_days = np.where(kiso[k, next_week_range] == 0)[0]
                    if available_days.size > 0:
                        next_shift_day = np.random.choice(available_days)
                        kiso[k, next_shift_day + Sun[next_week - 1] + 1] = 1

    def assign_random_shifts(self, kiso, shift_times, Sun, total_days):
        kiso_copy = np.copy(kiso)
        num_weeks = len(Sun)
        num_employees = kiso.shape[0]

        for week_index in range(num_weeks):
            week_start = Sun[week_index - 1] + 1 if week_index > 0 else 0
            week_end = Sun[week_index] + 1 if week_index < num_weeks - 1 else total_days
            for person_index in range(num_employees):
                if shift_times[0][person_index] == "隔週":
                    continue
                shift_time = shift_times[week_index][person_index]
                if isinstance(shift_time, int) and shift_time > 0:
                    available_days = [i for i in range(week_start, week_end) if kiso_copy[person_index, i] == 0]
                    if len(available_days) >= shift_time:
                        assigned_days = np.random.choice(available_days, shift_time, replace=False)
                        for day in assigned_days:
                            kiso_copy[person_index, day] = 1
        return kiso_copy

    def first_gene(self):
        df = self.df.to_numpy()
        Hinichi = df[5, 5:36]
        # print(Hinichi)
        i = sum(isinstance(day, datetime.datetime) for day in Hinichi)

        Baito = df[7:26, 1]
        # print(Baito)
        j = sum(isinstance(hito, str) for hito in Baito)

        sex = df[7:7 + j, 2]
        trainee = df[7:7 + j, 3]
        gogen = df[7:7 + j, 37]
        gogen = np.where(gogen.astype(str) == 'nan', 'なし', gogen)

        youbi = df[5, 5:5 + i]
        Sun = [i for i, day in enumerate(youbi) if day.weekday() == 6] # インデックスが0から始まることに注意
        # print(Sun)

        kiso = df[7:7 + j, 5:5 + i]
        kiso = np.where(kiso == '休', 2, kiso)
        kiso = np.where(kiso == 'A', 3, kiso)
        kiso = np.where(kiso == 'B', 4, kiso)
        kiso = np.where(kiso.astype(str) == 'nan', 0, kiso).astype(int)

        # 週ごとのシフトデータを処理
        weekly_shifts = self.process_weekly_shifts(kiso, Sun)
        # print(weekly_shifts)

        # 週ごと人ごとに入れる数リスト
        valid_days = self.count_zeros_per_week(weekly_shifts)
        # print("sss", valid_days)

        # シフト時間のデータを取得
        times = df[7:7 + j, 36]
        times = np.where(times.astype(str) == 'nan', 7, times)
        times = np.where(times == '週1', 1, times)
        times = np.where(times == '週2', 2, times)
        times = np.where(times == '週3', 3, times)
        times = np.where(times == '隔週', '隔週', times)

        # 各従業員のシフト時間を週ごとに処理
        shift_times = [times.copy() for _ in weekly_shifts]
        self.update_shift_times_with_min_values(shift_times, valid_days)  # shift_times[week_index][person_index]
        self.assign_alternate_weeks_shifts(kiso, Sun, shift_times, i)

        kiso_copy = self.assign_random_shifts(kiso, shift_times, Sun, i)
        # print(kiso_copy)
        return kiso_copy, Sun, sex, trainee, gogen, shift_times

if __name__ == "__main__":
    d = MakeTable()
    d.first_gene()

