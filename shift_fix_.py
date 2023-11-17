import numpy as np

from make_table import MakeTable  # デバック様
from utils import Write_table

class shift_fixer:
    def __init__(self, ):
        pass

    # 隔週を希望してる場合の修正
    def adjust_biweekly_shifts(self, ho, shift_index, days, Sun):
        total_weeks = len(Sun)
        for i in range(0, total_weeks, 2):  # 隔週ごとに処理
            # 対象週の範囲を設定
            start_day = Sun[i - 1] + 1 if i > 0 else 0
            end_day = Sun[i + 1] if i < total_weeks - 1 else days

            # 対象週のシフト状態を取得
            week_shifts = ho[shift_index, start_day:end_day]
            shift_count = np.sum((week_shifts == 0) | (week_shifts == 3)| (week_shifts == 4))

            if shift_count < 1:
                # シフトが足りない場合、ランダムに1日追加
                available_days = np.where(week_shifts == 1)[0] + start_day
                if available_days.size > 0:
                    day_to_add = np.random.choice(available_days)
                    ho[shift_index, day_to_add] = 0
            elif shift_count > 1:
                # シフトが多い場合、ランダムに1日減らす
                shift_days = np.where(week_shifts == 0)[0] + start_day
                if shift_days.size > 0:
                    day_to_remove = np.random.choice(shift_days)
                    ho[shift_index, day_to_remove] = 1

    def adjust_shifts(self, ho, shift, start_day, end_day, shift_index, days, Sun):
        """
        シフトの追加と削除
        :param ho: 現在のシフト状態
        :param shift: 従業員のシフト希望
        :param start_day: 処理開始日
        :param end_day: 処理終了日
        :param shift_index: 従業員のインデックス
        """
        shift_count = np.sum(ho[shift_index, start_day:end_day] == 0)
        desired_shifts = shift[shift_index]

        if shift[shift_index] == "隔週":
            # 隔週シフトの処理
            desired_shift_count = 1  # 希望するシフトの回数を設定
            self.adjust_biweekly_shifts(ho, shift_index, days, Sun)
        else:
            # 通常のシフト処理
            shift_count = np.sum(ho[shift_index, start_day:end_day] == 0)
            desired_shifts = int(shift[shift_index])

            # 3,4に関してシフトが入ってるので、望んでる数から引く
            existing_shifts = np.sum(ho[shift_index, start_day:end_day] == 3) + np.sum(
                ho[shift_index, start_day:end_day] == 4)
            desired_shifts = max(desired_shifts - existing_shifts, 0)

            difference = shift_count - desired_shifts
            while difference != 0:
                day = np.random.randint(start_day, end_day)
                if difference > 0 and ho[shift_index, day] == 0:
                    ho[shift_index, day] = 1
                    difference -= 1
                elif difference < 0 and ho[shift_index, day] == 1:
                    ho[shift_index, day] = 0
                    difference += 1

    def adjust_shifts_per_day(self, ho, shift_times, sex, max_shifts_per_day):
        days = ho.shape[1]
        num_employees = ho.shape[0]

        for day in range(days):
            # その日のシフト状態を取得
            day_shifts = ho[:, day]

            # 全員が休みの場合はスキップ
            if np.sum(day_shifts) == num_employees * 2:
                continue

            # 出勤している人数をカウント
            shift_count = np.sum((day_shifts == 0) | (day_shifts == 3) | (day_shifts == 4))

            # 出勤人数が多い場合、減らす
            if shift_count > max_shifts_per_day:
                excess_shifts = shift_count - max_shifts_per_day
                for _ in range(excess_shifts):
                    # 出勤している人をランダムに選び、条件に合う場合にシフトを変更
                    possible_indices = np.where((day_shifts < 2) & ~(shift_times == 1) & ~(shift_times == "隔週"))[0]
                    if possible_indices.size > 0:
                        idx_to_change = np.random.choice(possible_indices)
                        ho[idx_to_change, day] = 1  # 出勤を休みに変更

            # 出勤人数が少ない場合、増やす
            if shift_count < max_shifts_per_day:
                needed_shifts = max_shifts_per_day - shift_count
                for _ in range(needed_shifts):
                    # 休んでいる人をランダムに選び、条件に合う場合にシフトを変更
                    possible_indices = \
                    np.where((day_shifts == 1) & ~(shift_times == 1) & ~(shift_times == "隔週"))[0]
                    if possible_indices.size > 0:
                        idx_to_change = np.random.choice(possible_indices)
                        ho[idx_to_change, day] = 0  # 休みから出勤に変更

            # 女性の出勤調整
            women_present = np.any((day_shifts < 2) & (sex == "女"))
            if not women_present:
                # 男性のシフトを一人減らす
                men_indices = \
                np.where((day_shifts < 2) & (sex == "男") & ~(shift_times == 1) & ~(shift_times == "隔週"))[0]
                if men_indices.size > 0:
                    man_to_reduce = np.random.choice(men_indices)
                    ho[man_to_reduce, day] = 1

                # 女性のシフトを一人増やす
                women_indices = \
                np.where((day_shifts == 1) & (sex == "女") & ~(shift_times == 1) & ~(shift_times == "隔週"))[0]
                if women_indices.size > 0:
                    woman_to_increase = np.random.choice(women_indices)
                    ho[woman_to_increase, day] = 0

    def adjust_saturday_shifts(self, ho, shift_times, sex, Sun):
        for day in Sun:
            if day == 0:  # 最初の日が日曜日の場合はスキップ
                continue

            # その日のシフト状態を取得
            day_shifts = ho[:, day - 1]

            # 全員が休みの場合はスキップ
            if np.sum(day_shifts) == len(ho) * 2:
                continue

            # 出勤している女性をカウント
            women_count = np.sum((day_shifts == 0) & (sex == "女"))

            # 女性が2人以上いる場合、シフトを調整
            if women_count > 1:
                women_indices = np.where((day_shifts == 0) & (sex == "女"))[0]
                men_indices = \
                np.where((day_shifts == 1) & (sex == "男") & ~(shift_times == 1) & ~(shift_times == "隔週"))[0]

                # 女性のシフトを減らし、同数の男性のシフトを増やす
                for _ in range(women_count - 1):
                    if women_indices.size > 0 and men_indices.size > 0:
                        woman_to_reduce = np.random.choice(women_indices)
                        man_to_increase = np.random.choice(men_indices)
                        ho[woman_to_reduce, day - 1] = 1
                        ho[man_to_increase, day - 1] = 0
                        women_indices = np.delete(women_indices, np.where(women_indices == woman_to_reduce))
                        men_indices = np.delete(men_indices, np.where(men_indices == man_to_increase))

    def shift_fix(self, kiso, shift_times, Sun ,sex, max_shifts_per_day = 3):
        days = kiso.shape[1]
        # 休日1、出勤0、希望休2、五時入り3、六時入り4
        # 3,4の記号的役割は2と同じで、場所も変わらない、数も変わらない、シフト希望数から数はすでにひかれてる
        # self.ho = kiso.replace({0: 9, 1: 0, 9: 1}) pandasはこれ
        ho = np.where(kiso == 0, 1, np.where(kiso == 1, 0, kiso))  # 休日1、出勤0に変換
        Sun = Sun
        shift_times = shift_times
        sex = sex
        for k in range(len(ho)):
            for i, sun_day in enumerate(Sun):
                start_day = Sun[i - 1] + 1 if i > 0 else 0
                end_day = sun_day + 1 if sun_day != days - 1 else sun_day + 1
                self.adjust_shifts(ho, shift_times[i], start_day, end_day, k, days, Sun)
                self.adjust_shifts_per_day(ho, shift_times[i], sex, max_shifts_per_day)
                self.adjust_saturday_shifts(ho, shift_times[i], sex, Sun)
        kiso_copy = np.where(ho == 0, 1, np.where(ho == 1, 0, ho))  # 休日1、出勤0に変換
        # print(kiso_copy)
        return kiso_copy

