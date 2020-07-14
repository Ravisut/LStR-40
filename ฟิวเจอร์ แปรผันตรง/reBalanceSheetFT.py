import callFuntionFutures

import gspread
import time
import pandas as pd
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

#Update while Loop
while True:
     #try:
         timeBegin = time.time()
         print(datetime.datetime.now().strftime('%H:%M'))
         ws = gc.open("Data").worksheet('PERP')  # เปิดหน้าชีท
         df = get_as_dataframe(ws).set_index('indexAround')  # เรียกข้อมูลใน google sheet และตั้งให้ คอลัม indexAround เป็น index ไว้ให้ pandas เรียกใช้
         Around = df.loc['Around']['Balance']  # ตัวนับ

         df = callFuntionFutures.updatee(df, Around)
         df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # ลบคอลัม์ที่ไม่ต้องการ

         pd.set_option('display.width', 1000)
         print(df.loc[Around].to_frame().T)
         set_with_dataframe(gc.open("Data").worksheet('PERP'), df.reset_index())  # บันทึกลง ชีทหน้า

         timeEnd = time.time()
         timeElapsed = timeEnd - timeBegin
         time.sleep(60 - timeElapsed)  # ถ่วงเวลา 1 นาที

     #except Exception as e:
     #       callFuntion.LineNotify('','',e,'error') # ถ้า error ไลน์ไป แจ้งคนเขียน
     #       break
#End while Loop