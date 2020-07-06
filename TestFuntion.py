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
ws = gc.open("Data").worksheet("BTC") #เรียกชีทหน้า

df = get_as_dataframe(ws)

test = 6
# พื้นที่ทดสอบฟังก์ชั่น ก่อนเอาไปใส่ใน คลาส reBalance
if test == 1: # เรียกดูว่า เหรียญนั้นๆ มีจำนวนเท่าไร
    df = callFuntion.get_balance('BNB', 1)
    print(df)
if test == 2: # เรียกดูว่าในพอร์ตมีเหรียญอะไรบ้างเท่าไร
    df = callFuntion.get_balance('', 2)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    set_with_dataframe(gc.open("Data").worksheet("test3"), df.reset_index())  #บันทึกลง ชีทหน้า test3
    print(df)

if test == 3: # ทดสอบยิงออเดอร์
    infooder = callFuntion.re('BNB/USDT', 'sell', 0.001, 18.00)
    #df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    #set_with_dataframe(gc.open("Data").worksheet("test3"), df.reset_index() )  #บันทึกลง ชีทหน้า test3
    print(type(infooder))
    print(infooder)

if test == 4: #ทดสอบดูข้อมูลด้วยไอดี
    oderinfo = callFuntion.checkByIDoder('5efe39302f778b0007f4d2b1')
    print(oderinfo)
if test == 5: #ทดสอบเวลา
    start_time  = time.time()+60
    target_time = time.time()
    timeElapsed = target_time - start_time
    print(timeElapsed)
    #delta = target_time - start_time

if test ==6:
    oderinfo = callFuntion.OHLC("BTC/USD")
    print(oderinfo)




