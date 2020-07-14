import callFuntionFutures
import time
import datetime
import pandas as pd

#เวอร์ชั่น CSV

while True:
     #try:
         timeBegin = time.time()
         print(datetime.datetime.now().strftime('%H:%M'))
         df1 = pd.read_csv('Data.csv', error_bad_lines=False)
         df = df1.set_index('indexAround')

         Around = df.loc['Around']['Balance']  # ตัวนับ

         df = callFuntionFutures.updatee(df,Around)
         df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # ลบคอลัม์ที่ไม่ต้องการ

         pd.set_option('display.width', 1000)
         print(df.loc[Around].to_frame().T)
         df = df.reset_index()
         df.to_csv("Data.csv", index=False)

         timeEnd = time.time()
         timeElapsed = timeEnd - timeBegin
         time.sleep(60 - timeElapsed)  # ถ่วงเวลา 1 นาที

     #except Exception as e:
     #       callFuntion.LineNotify('','',e,'error') # ถ้า error ไลน์ไป แจ้งคนเขียน
     #       break
