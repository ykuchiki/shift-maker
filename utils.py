import warnings
from datetime import datetime, timedelta
from random import random

import numpy as np
import pandas as pd



class Read_table:
    def __init__(self):
        warnings.simplefilter('ignore', UserWarning)
        print("処理開始")

    def read_excel(self, fname: str):
        df = pd.read_excel(fname, sheet_name="Sheet1", header=None)
        return df

    def excel_date(self, num):
        date = datetime(1899, 12, 30) + timedelta(days=num)
        return date.strftime("%A")


class Write_table:
    def __init__(self):
        warnings.simplefilter('ignore', UserWarning)
        print("処理終了")

    def write_excel(self, kiso_copy):
        # kiso_copy1 = np.where(kiso_copy == 0, 0, np.where(kiso_copy == 1, "A", kiso_copy))
        kiso_copy_df = pd.DataFrame(kiso_copy)
        # print(kiso_copy_df)
        kiso_copy_df.to_excel("moto.xlsx", index=False, header=False)


class CrossOver:
    def __init__(self):
        pass

    def crossover(self, ep,sd,p1,p2):
        #一か月の日数
        days = p1.shape[1]
        #一次元化
        p1 = np.array(p1).flatten()
        p2 = np.array(p2).flatten()

        #子の変数
        ch1 = []
        ch2 = []

        for p1_,p2_ in zip(p1,p2):
            x = True if ep > random() else False

            if x == True:
                ch1.append(p1_)
                ch2.append(p2_)
            else:
                ch1.append(p2_)
                ch2.append(p1_)

        # 突然変異
        ch1,ch2 = self.mutation(sd, np.array(ch1).flatten(), np.array(ch2).flatten())

        # pandasに変換
        ch1 = ch1.reshape((-1, days))
        ch2 = ch2.reshape((-1, days))

        # 列名の変更
        # ch1.columns = [i+1 for i in range(ch1.shape[1])]
        # ch2.columns = [i+1 for i in range(ch2.shape[1])]

        return ch1,ch2

    #突然変異の関数
    def mutation(self, sd,ch1,ch2):

        x = True if sd > random() else False

        if x == True:

            #遺伝子の10%を変異させる
            rand = np.random.permutation([i for i in range(len(ch1))])
            rand = rand[:int(len(ch1)//10)]
            for i in rand:
                if ch1[i] == 1:
                    ch1[i] == 0

                if ch1[i] == 0:
                    ch1[i] == 1
        x = True if sd > random() else False

        if x == True:
            rand = np.random.permutation([i for i in range(len(ch1))])
            rand = rand[:int(len(ch1)//10)]
            for i in rand:
                if ch2[i] == 1:
                    ch2[i] == 0
                if ch2[i] == 0:
                    ch2[i] == 1

        return ch1,ch2
