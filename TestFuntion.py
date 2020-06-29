import pandas as pd
import gspread
import callFuntion
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)
ws = gc.open("Data").worksheet("test3") #เรียกชีทหน้า test3

df = get_as_dataframe(ws)

test = 2
# พื้นที่ทดสอบฟังก์ชั่น ก่อนเอาไปใส่ใน คลาส reBalance
if test == 1: # เรียกดูว่า เหรียญนั้นๆ มีจำนวนเท่าไร
    df = callFuntion.get_balance('BNB', 1)
    print(df)
if test == 2: # เรียกดูว่าในพอร์ตมีเหรียญอะไรบ้างเท่าไร
    df = callFuntion.get_balance('', 2)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    set_with_dataframe(gc.open("Data").worksheet("test3"), df.reset_index())  #บันทึกลง ชีทหน้า test3
    print(df)
if test == 3: # ดูโครงสร้าง json เพื่อปรับคำสั่ง
    df = callFuntion.get_balance('', 3)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    set_with_dataframe(gc.open("Data").worksheet("test3"), df.reset_index() )  #บันทึกลง ชีทหน้า test3
    print(df)





