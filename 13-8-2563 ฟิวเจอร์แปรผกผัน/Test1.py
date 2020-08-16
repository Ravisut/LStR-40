import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

dfMap = get_as_dataframe(gc.open("Data").worksheet('Test'))

def check():

    for i, row in dfMap.iterrows():
        iStr =  '123456'
        row['Stat'] = iStr
        print(row['Stat'])
        if i == 5:

            dfMapp = dfMap.drop(columns=[c for c in dfMap.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
            #set_with_dataframe(gc.open("Data").worksheet('Test'), dfMapp)  # บันทึกลง ชีทหน้า
            print(dfMapp)
            return

def check2():
    df2 = pd.DataFrame({'Number':[str(2)]})

    dfMapp = dfMap.append(df2)
    dfMapp = dfMapp.drop(columns=[c for c in dfMapp.columns if "Unnamed" in c]).dropna(how="all")
    set_with_dataframe(gc.open("Data").worksheet('dfMap'), dfMapp)  # บันทึกชีทหน้า TradeLog
    print(dfMapp)

check2()


