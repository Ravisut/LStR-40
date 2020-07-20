import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

RangMap = 5
StartPrice = 0.195
pip = 0.001
Exposure = 1

#Load MapSell
dfMapSell = pd.DataFrame({'MinPrice': [],'MaxPrice': [], 'Exposure': [], 'MinPortValue': [], 'MaxPortValue': []})
for i in range(RangMap):

    Price = pip*i
    MinPrice = StartPrice+Price
    MaxPrice = MinPrice+0.001
    MinPortValue = i
    MaxPortValue = MinPortValue+Exposure

    dfMapSell = dfMapSell.append({'MinPrice': MinPrice,'MaxPrice': MaxPrice, 'Exposure': Exposure, 'MinPortValue': MinPortValue, 'MaxPortValue': MaxPortValue}, ignore_index=True)
    set_with_dataframe(gc.open("Data").worksheet('MapSell'), dfMapSell)

#Load MapBuy
dfMapBuy = pd.DataFrame({'MaxPrice': [],'MinPrice': [], 'Exposure': [], 'MinPortValue': [], 'MaxPortValue': []})
for i in range(RangMap):
    Price = -pip*i
    MaxPrice = StartPrice+Price
    MinPrice = MaxPrice+(-pip)
    MinPortValue = i*(-1)
    MaxPortValue = MinPortValue+Exposure*(-1)

    dfMapBuy = dfMapBuy.append({'MaxPrice': MaxPrice,'MinPrice': MinPrice, 'Exposure': Exposure, 'MinPortValue': MinPortValue, 'MaxPortValue': MaxPortValue}, ignore_index=True)
    set_with_dataframe(gc.open("Data").worksheet('MapBuy'), dfMapBuy)

def get_PortValue(exposureRerate):
    # Sell
    if exposureRerate > 0:
        wsMapSell = gc.open("Data").worksheet('MapSell')  # เปิดหน้าชีท
        df = get_as_dataframe(wsMapSell)
        for i, row in df.iterrows():
            if exposureRerate <= row['MinPortValue']:
                Price = row['MinPrice']
                return Price
    # BUY
    if exposureRerate < 0:
        wsMapBuy = gc.open("Data").worksheet('MapBuy')  # เปิดหน้าชีท
        df = get_as_dataframe(wsMapBuy)
        for i, row in df.iterrows():
            if exposureRerate >= row['MinPortValue']:
                Price = row['MaxPrice']
                return Price

print(get_PortValue(-3))