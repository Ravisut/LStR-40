import callFuntion

import gspread
import time
import datetime
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

subAsset = ["BNB","XRP"]

#Update while Loop
while True:
     try:
         timeBegin = time.time()
         print(datetime.datetime.now().strftime('%H:%M'))
         for i in range(len(subAsset)):

             ws = gc.open("Data").worksheet(subAsset[i])  # เรียกชีทหน้า BNB XRP
             df = get_as_dataframe(ws).set_index('indexAround')  # เรียกข้อมูลใน google sheet และตั้งให้ คอลัม indexAround เป็น index ไว้ให้ pandas เรียกใช้
             Around = df.loc['Around']['Balance']  # ตัวนับ

             df = callFuntion.updatee(df, Around,subAsset[i])
             df = df.loc[:, ~df.columns.str.contains('^Unnamed')]  # ลบคอลัม์ที่ไม่ต้องการ

             print(" รอบ " + str(Around) + ' ของ ' + str(subAsset[i]) +' มีปริมาณ '+df.loc[Around]['Asset'] +' Balance = ' + df.loc[Around]['Balance'] + ' ' + str(callFuntion.MainAsset))
             # print(df.loc[Around].to_frame().T)
             set_with_dataframe(gc.open("Data").worksheet(subAsset[i]), df.reset_index()) # บันทึกลง ชีทหน้า

         timeEnd = time.time()
         timeElapsed = timeEnd - timeBegin
         time.sleep(60 - timeElapsed)  # ถ่วงเวลา 1 นาที

     except Exception as e:
            callFuntion.LineNotify('','','','error') # ถ้า error ไลน์ไป แจ้งคนเขียน
            break
#End while Loop