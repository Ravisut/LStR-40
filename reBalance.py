import pandas as pd
import gspread
import time
import callFuntion
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)
ws = gc.open("Data").worksheet("test2") #เรียกชีทหน้า test2

#df = get_as_dataframe(ws).set_index('indexAround')
#Around = df.loc['Around']['Balance'] # ตัวนับ

#Update while Loop
while True:
    try:
        df = get_as_dataframe(ws).set_index('indexAround') #เรียกข้อมูลใน google sheet และตั้งให้ คอลัม indexAround เป็น index ไว้ให้ pandas เรียกใช้
        Around = df.loc['Around']['Balance'] # ตัวนับ

        timeBegin = time.time()

        df = callFuntion.updatee(df, Around)

        df = df.loc[:, ~df.columns.str.contains('^Unnamed')] # ลบคอลัม์ที่ไม่ต้องการ
        print(df.loc[Around].to_frame().T)
        # บันทึกลง ชีทหน้า test2
        set_with_dataframe(gc.open("Data").worksheet("test2"), df.reset_index())


        timeEnd = time.time()
        timeElapsed = timeEnd - timeBegin
        time.sleep(60 - timeElapsed) #ถ่วงเวลา 1 นาที
        #print(timeBegin,timeEnd)
        # รอใส่ฟังก์ชั่น แจ้งเตือนผ่านไลน์
    except Exception as e:
        print("แจ้งคนเขียน")
#End while Loop