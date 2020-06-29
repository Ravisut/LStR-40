import pandas as pd
import gspread
import callFuntion
import numpy as np
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)
ws = gc.open("Data").worksheet("test2") #เรียกชีทหน้า test2

#เรียกข้อมูลใน google sheet และตั้งให้ คอลัม indexAround เป็น index ไว้ให้ pandas เรียกใช้
df = get_as_dataframe(ws).set_index('indexAround')

#ตัวนับ
Around = df.loc['Around']['Balance']

#Update รอใส่ while Loop
df = callFuntion.updatee(df,Around)
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

#บันทึกลง ชีทหน้า test2
set_with_dataframe(gc.open("Data").worksheet("test2"), df.reset_index() )
print(df)

#รอใส่ฟังก์ชั่น แจ้งเตือนผ่านไลน์

#End while Loop