import callFuntion
import time
import datetime
import pandas as pd

subAsset = "BTC"

while True:
     #try:
         timeBegin = time.time()
         print(datetime.datetime.now().strftime('%H:%M'))
         df1 = pd.read_csv('Data.csv')
         df = df1.set_index('indexAround')

         Around = df.loc['Around']['Balance']  # ตัวนับ

         df = callFuntion.updatee(df, Around, subAsset)
         df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # ลบคอลัม์ที่ไม่ต้องการ

         # print(" รอบ " + str(Around) + ' ของ ' + str(subAsset[i]) +' มีปริมาณ '+df.loc[Around]['Asset'] +' Balance = ' + df.loc[Around]['Balance'] + ' ' + str(callFuntion.MainAsset))
         print(df.loc[Around].to_frame().T)
         df = df.reset_index()
         df.to_csv("Data.csv", index=False)

         timeEnd = time.time()
         timeElapsed = timeEnd - timeBegin
         time.sleep(60 - timeElapsed)  # ถ่วงเวลา 1 นาที

     #except Exception as e:
     #       callFuntion.LineNotify('','',e,'error') # ถ้า error ไลน์ไป แจ้งคนเขียน
     #       break
