import datetime
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

# Google sheet
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)
sheetName = 'sequential'
#settingbot = get_as_dataframe(gc.open(sheetName).worksheet('setting')).set_index('index')
data = get_as_dataframe(gc.open(sheetName).worksheet('data'))
#tradelog = get_as_dataframe(gc.open(sheetName).worksheet('TradeLog'))


def checkmatch():
   x = datetime.datetime.now().strftime("%H:%M:%S")
   h, m, s = map(int, x.split(':'))
   sec = h * 3600 + m * 60 + s
   one_min = round(sec / 60, 2)
   print(x)
   print(int(one_min))

   f = data.loc[data['pi'] == one_min]
   #v = f.loc[0]['pi']

   #return int(v)

print(checkmatch())
