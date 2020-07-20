import LoadMap

import ccxt
import json
import time
import requests
import pandas as pd
import numpy as np
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

wsTradeLog = gc.open("Data").worksheet('TradeLog')  # เปิดหน้าชีท
dfTradeLog = get_as_dataframe(wsTradeLog)

#### รายละเอียด ก่อนเทรด -------------------------------------------------------
Balance = 'USD'
whatsymbol = "XRP-PERP"
###########  ตั้งค่า API -------------------------------------------------------
subaccount = '-------'  # ถ้ามี ซับแอคเคอร์ของ FTX
exchange = ccxt.ftx({
        'apiKey': '-------------------',
        'secret': '--------------------',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }

########### ----------------------------------------------------------------------------

def updatee(df):
    df._set_value(whatsymbol, 'Balance', get_balance(Balance))
    Multiply = df.loc[whatsymbol]['Multiply']
    StarPrice = df.loc[whatsymbol]['StarPrice']

    if df.loc[whatsymbol]['Stat'] == 'Cooldown':
        first_time = df.loc[whatsymbol]['Timer']
        target_time = time.time()
        timeElapsed = target_time - first_time
        if timeElapsed > 0:
            df._set_value(whatsymbol, 'Stat', '')
            df._set_value(whatsymbol, 'Timer', '')
    else:
        if pd.notna(df.loc[whatsymbol, 'IDorder']):  # ช่องไอดี ว่างไหม ถ้าไม่ว่างแสดงว่า ตั้ง pending อยู่
            df = orderFilled(df, Multiply)  # เช็ค ว่าลิมิตออเดอร์ ว่า fill ยัง
        else:
            NowPrice = getPrice(whatsymbol)
            df._set_value(whatsymbol, 'NowPrice', NowPrice)

            exposureRerate = df.loc[whatsymbol]['ExposureRerate']

            DifPrice = float(StarPrice) - float(NowPrice)
            df._set_value(whatsymbol, 'DifPrice', DifPrice)

            portvalue = LoadMap.get_PortValue(exposureRerate)
            df._set_value(whatsymbol, 'PortValue', portvalue)

            Dif = float(NowPrice) - float(DifPrice)
            amount = abs(Dif) / float(NowPrice)  # ปริมาณสินค้าที่จะตั้งออเดอร์

            conditionToAdjust = tradeFunction(df, whatsymbol)
            conditionToAdjust = False

            if conditionToAdjust == True:
                if pd.isna(df.loc[whatsymbol, 'IDorder']):  # ถ้าช่อง ไอดีออเดอร์ยังว่าง แสดงว่าเป็นเงื่อนไขแรก ไม่มีการตั้งลิมิต
                    df._set_value(whatsymbol, 'Stat', 'Action')
                    if Dif < 0:
                        df._set_value(whatsymbol, 'Side',"BUY")  # ต้อง set ค่าเริ่มต้นในชีทให้เป็น สติง ก่อน ไม่นั้นมันจะคิดว่า ช่องว่างๆ คือ ค่า float error ValueError: could not convert string to float
                        df = re(df, whatsymbol, 'buy', amount, Multiply, NowPrice)  # ยิงออเดอร์
                    if Dif > 0:
                        df._set_value(whatsymbol, 'Side', "SELL")
                        df = re(df, whatsymbol, 'sell', amount, Multiply, NowPrice)  # ยิงออเดอร์
            else:  # ยังไม่เข้าเงื่อนไข รอไปก่อน
                df._set_value(whatsymbol, 'Stat', 'Wait')  # 'Stat ' กับ 'Stat' ถ้ามีช่องว่าง คือไม่ใช่คำเดียวกัน
    return df

def get_balance(get_asset):
    result = 'result'
    listAsset = 'coin'
    params = {'recvWindow': 50000}

    balance = exchange.fetch_balance(params)
    df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
    df_balance['free'] = df_balance.free.astype(float)
    return df_balance.loc[get_asset]['free']

def getPrice(pair):
    r = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r)
    sendBack = float(dataPrice['last'])
    return sendBack

def re(df,symbol,side,amount,Multiply,price):
    types = 'limit'  # 'limit' or 'market'
    _amount = amount* Multiply
    order = exchange.create_order(symbol, types, side, _amount, price)

    df._set_value(whatsymbol, 'Amount',_amount)
    df._set_value(whatsymbol, 'IDorder', order['id'])  # รับไอดี
    df._set_value(whatsymbol, 'Date', order['datetime'])
    df._set_value(whatsymbol, 'Timer', time.time())
    return df

def orderFilled(df,Multiply): #เช็คดว่า แมต ยังหรือยัง # ต้นทางเช็คมาแล้วว่า ID ไม่ว่าง แสดงว่ามีการตั้ง Pending ออเดอร์
    id = df.loc[whatsymbol]['IDorder']
    orderMatched = checkByIDoder(id)
    if orderMatched['filled'] > 0:  # เช็ค Matched ไหม # ถ้ามากกว่า 0 แสดงว่า ลิมิตออเดอร์ แมต แล้ว..
        # เติมข้อมูล ออเดอร์ที่แมตแล้ว พร้อมคำนวณ exposure
        PositionSize = orderMatched['filled'] * orderMatched['price']
        if orderMatched['side'] == 'buy':
            PositionSize = PositionSize * (-1)
        ExposureReal = df.loc[0.1]['ExposureReal'] + PositionSize
        exposureRerate = ExposureReal / float(Multiply)
        df._set_value(0.1, 'ExposureReal', ExposureReal)
        df._set_value(0.1, 'ExposureRerate', exposureRerate)
        # บันทึกลง TradeLog
        dfTradeLog_ = dfTradeLog.append({'IDorder': orderMatched['id'],'Side': orderMatched['side'],'Price': orderMatched['price'],'Amount': orderMatched['amount'],'Filled': orderMatched['filled'], 'PositionSize': PositionSize, 'Fee': orderMatched['fee'], 'Cost': orderMatched['cost']}, ignore_index=True)
        set_with_dataframe(gc.open("Data").worksheet('dfTradeLog'), dfTradeLog_)
        # ตั้งดีเลย์
        df = TimeDelayForNextTrade(df)
        LineNotify(df, 'change')
    else:
        if orderMatched['type'] == 'limit':
            # ผ่านไป 10 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
            first_time = df.loc[whatsymbol]['Timer']
            start_time = first_time + 600  # นับถอยหลัง 10 นาที เพื่อยกเลิกออเดอร์
            target_time = time.time()
            timeElapsed = target_time - start_time
            if timeElapsed > 0:
                cancelOrder(df, id)
    return df

def checkByIDoder(id):
    oderinfo = exchange.fetch_order(id)
    return oderinfo

def cancelOrder(df,id):
    orderMatched = checkByIDoder(id)
    if orderMatched['status'] == 'closed':
        print('mannual cancel')
    else:
        exchange.cancel_order(id)
        # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
    df._set_value(whatsymbol, 'Amount', '')
    df._set_value(whatsymbol, 'IDorder', '')
    df._set_value(whatsymbol, 'Date', '')
    df._set_value(whatsymbol, 'Timer', '')



def TimeDelayForNextTrade(df):
    #หลังจาก รีบาลานซ์ครั้งก่อนให้ นับถอยหลัง ถึงจะมีสิทธิ์ยิงนัดถัดไปได้
    # 1% เท่ากับ 1 ชั่วโมง
    oderinfo = OHLC(whatsymbol,3)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr3 = oderinfo["Percent_Change"].mean()
    cooldownTime = 0.6*mean1hr3*100*60

    df._set_value(whatsymbol, 'Timer', time.time()+cooldownTime)
    df._set_value(whatsymbol, 'Stat', 'Cooldown')
    return df

def tradeFunction(df,symbol):
    ExposureRerate = df.loc[whatsymbol]['ExposureRerate']
    ExposureRerate = float(ExposureRerate)
    Price = getPrice(symbol)
    DifPercent = abs(ExposureRerate - Price) / (ExposureRerate / 100)
    minPercent = 0.5

    oderinfo = OHLC(symbol,168)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr168 = oderinfo["Percent_Change"].mean()

    df._set_value(whatsymbol, 'Dif', ExposureRerate - Price)
    df._set_value(whatsymbol, 'DifPercent', DifPercent)
    df._set_value(whatsymbol, 'DifPercent', DifPercent)
    df._set_value(whatsymbol, 'Condition', mean1hr168)

    minPercentToAdjust = (float(ExposureRerate) / 100) * float(minPercent)  # ตรวจดูว่า เกิน 0.5%ยัง

    if mean1hr168 > minPercentToAdjust:
        if DifPercent > mean1hr168:
            return True  # เข้าเงื่อนไขจริง
    else:
        return False #https://stackoverflow.com/questions/19498572/why-do-i-get-none-instead-of-true-false-in-python


#ดึงข้อมูลราคา เครดิต คุณ Sippavit Kittirattanadul
def OHLC(pair,count):  # นำขั้นตอนการเรียกข้อมุล ohlc มารวมเป็น function เพื่อเรียกใช้งานได้เรื่อยๆ

    try:  # try/except ใช้แก้ error : Connection aborted https://github.com/ccxt/ccxt/wiki/Manual#error-handling
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1h', limit=count)
        # print(ohlc)
    except ccxt.NetworkError as e:
        print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1h', limit=count)
        # retry or whatever

    except ccxt.ExchangeError as e:
        print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1h', limit=count)
        # retry or whatever

    except Exception as e:
        print(exchange.id, 'fetch_ohlcv failed with:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1h', limit=count)
        # retry or whatever

    ohlc_df = pd.DataFrame(ohlc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['datetime'], unit='ms')

    return ohlc_df

def LineNotify(df,typee) :
    # แจ้งเตือนผ่านไลน์เมื ่่อเกิดการรีบาลานซ์
    # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549
    url = 'https://notify-api.line.me/api/notify'
    token = 'MQaK3NTRG0gtC4PS2pQYiJvKC44J4prFY3hAcgzZ8EE'
    headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

    if typee == 'change':
        PositionSize = df.loc[whatsymbol]['PositionSize']
        Exposure = df.loc[whatsymbol]['ExposureReal']
        msg = PositionSize
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)
    if typee == 'error' :
        msg = '\nแจ้งคนเขียน\n'
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)