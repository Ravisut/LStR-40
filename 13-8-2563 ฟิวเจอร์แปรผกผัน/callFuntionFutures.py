import ccxt
import json
import time
import random
import requests
import numpy as np
import pandas as pd
from pandas.io.json import json_normalize
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

# เรียกข้อมูลใน google sheet และตั้งให้ คอลัม Product เป็น index ไว้ให้ pandas เรียกใช้
df = get_as_dataframe(gc.open("Data").worksheet('PERP') ).set_index('Product')
dfMap = get_as_dataframe(gc.open("Data").worksheet('Map'))
dfTradeLog = get_as_dataframe(gc.open("Data").worksheet('TradeLog'))

#### รายละเอียด ก่อนเทรด -------------------------------------------------------
Balance = 'USD'
whatsymbol = "XRP-PERP"
###########  ตั้งค่า API -------------------------------------------------------
subaccount = 'ForTest'  # ถ้ามี ซับแอคเคอร์ของ FTX
exchange = ccxt.ftx({
        'apiKey': '**********',
        'secret': '**********',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }

########### ----------------------------------------------------------------------------


def updatee():
    # ----- ตั้งค่า Map ว่าแต่ล่ะโซนควรมีกระสุนหรือไม่-----
    Set_MapTrigger()
    # ----- ส่วนแสดงผลในหน้า PERP --------
    set_Maninsheet()

    if df.loc[whatsymbol]['Stat'] == 'Cooldown':
        TimerDelay = df.loc[whatsymbol]['TimerDelay']
        TimerTrigger = TimeDelayForNextTrade()
        target_time = time.time()
        timeElapsed = target_time - (TimerDelay+TimerTrigger)

        df._set_value(whatsymbol, 'TimerTrigger', TimerTrigger)
        df._set_value(whatsymbol, 'CooldownTime', timeElapsed)
        if timeElapsed > 0:
            df._set_value(whatsymbol, 'Stat', 'Free')
            df._set_value(whatsymbol, 'TimerDelay', np.nan)
            df._set_value(whatsymbol, 'TimerTrigger', np.nan)
            df._set_value(whatsymbol, 'CooldownTime', np.nan)
    if df.loc[whatsymbol]['Stat'] != 'Cooldown':
        # ----- ดูว่าเข้าเงื่อนไขเทรดยัง
        Trigger_trade()

    dff = df.drop(columns=[c for c in df.columns if "Unnamed" in c]).dropna(how="all") # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
    set_with_dataframe(gc.open("Data").worksheet('PERP'), dff.reset_index())  # บันทึกชีทหน้า PERP
    dfMapp = dfMap.drop(columns=[c for c in dfMap.columns if "Unnamed" in c]).dropna(how="all")
    set_with_dataframe(gc.open("Data").worksheet('Map'), dfMapp)  # บันทึก ชีทหน้า Map

    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 1000)
    #print(dfMapp)
    print(dff.loc[whatsymbol].to_frame().T)

def Trigger_trade():
    dfTradeLog1 = dfTradeLog
    difZone = df.loc[whatsymbol]['DifZone']
    for i, row in dfMap.iterrows():
        if pd.notna(row['IDorderBuy']):
            idOrderbuy = row['IDorderBuy']
            orderMatchedBUY = checkByIDoder(idOrderbuy)
            if orderMatchedBUY['filled'] == 0:
                # ถ้าหมดเวลา cooldown แล้วไม่ได้เปิดสักทีให้ ยกเลิกออเดอร์ลิมิต Sell
                if pd.notna(row['timecancelbuy']):
                    # ผ่านไป 10 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
                    first_time = row['timecancelbuy']
                    start_time = first_time + 600  # นับถอยหลัง 10 นาที เพื่อยกเลิกออเดอร์
                    target_time = time.time()
                    timeElapsed = target_time - start_time
                    if timeElapsed > 0:
                        cancelOrder(idOrderbuy)
                        # ลบ ข้อมูลกระสุนนัดนี้ เมื่อยกเลิกออเดอร์
                        # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                        row['IDorderBuy'] = np.nan
                        row['OpenPrice'] = np.nan
                        row['AmountBuy'] = np.nan
                        row['FilledBuy'] = np.nan
                        row['ExposureBuy'] = np.nan
                        row['timecancelbuy'] = np.nan


            # จะเปิด ออเดอร์ sell ได้ต้องมี Position Szie ด้าน Buy ก่อน
            elif orderMatchedBUY['filled'] == orderMatchedBUY['amount']:
                row['timecancelbuy'] = np.nan
                if pd.isna(row['FilledBuy']):
                    row['FilledBuy'] = orderMatchedBUY['filled']
                    row['feeBuy'] = Getfee_ByIDoderinMyTrades(idOrderbuy, orderMatchedBUY['side']) #fee
                    # บันทึก TradeLog
                    # ต้องแปลงเป็น สติงทั้งหมดไม่งั้นบันทึกไม่ได้
                    # กำหนด PD ก่อน
                    print('OpenOrder Price : '+str(orderMatchedBUY['price']))
                    print('Amount : '+str(orderMatchedBUY['filled']))

                if pd.notna(row['IDorderSell']):
                    idOrdersell = row['IDorderSell']
                    orderMatchedSELL = checkByIDoder(idOrdersell)
                    # sell filled ทั้งหมด แสดงว่าปิด กำไร ได้
                    if orderMatchedSELL['filled'] == orderMatchedSELL['amount']:
                        row['LastClosePrice'] = row['ClosePrice']
                        row['feeSell'] = Getfee_ByIDoderinMyTrades(idOrdersell, orderMatchedSELL['side'])  # fee
                        ExposureBuy = row['ExposureBuy']
                        ExposureSell = orderMatchedSELL['filled'] * orderMatchedSELL['price']

                        if pd.isna(row['Profit']):
                            row['Profit'] = (ExposureSell - ExposureBuy) - (row['feeSell'] + row['feeBuy'])
                        elif pd.notna(row['round']):
                            row['Profit'] = row['Profit'] + ((ExposureSell - ExposureBuy) - (row['feeSell'] + row['feeBuy']))

                        if pd.isna(row['round']):
                            row['round'] = 1
                        elif pd.notna(row['round']):
                            row['round'] = row['round'] + 1

                        print('ราคาขาย : ' + str(orderMatchedSELL['price']))
                        print('กำไร : ' + str(row['Profit']))
                        LineNotify(row['Profit'], 'change')
                        # บันทึก TradeLog
                        # ต้องแปลงเป็น สติงทั้งหมดไม่งั้นบันทึกไม่ได้
                        # กำหนด PD ก่อน
                        dfTradeLog3 = pd.DataFrame({'IDorderOrderBuy': [str(idOrderbuy)]
                                                       , 'IDorderOrderSell': [str(idOrdersell)]
                                                       , 'Open': [str(orderMatchedBUY['price'])]
                                                       , 'Close': [str(orderMatchedSELL['price'])]
                                                       , 'Amount': [str(orderMatchedSELL['filled'])]
                                                       , 'TradeTrigger': [str(row['TradeTrigger'])]
                                                       , 'Zone': [str(row['Zone'])]
                                                       , 'OpenTime': [str(orderMatchedBUY['datetime'])]
                                                       , 'CloseTime': [str(orderMatchedSELL['datetime'])]
                                                       , 'Profit': [str(row['Profit'])]
                                                       , 'feeBuy': [str(row['feeBuy'])]
                                                       , 'feeSell': [str(row['feeSell'])]

                                                    })
                        dfTradeLog1 = dfTradeLog1.append(dfTradeLog3, ignore_index=True)

                        # ลบ ข้อมูลกระสุน เมื่อจบครบรอบ ทำให้กระสุนว่าง
                        # ข้อมูลกระสุน buy
                        row['IDorderBuy'] = np.nan
                        row['OpenPrice'] = np.nan
                        row['AmountBuy'] = np.nan
                        row['FilledBuy'] = np.nan
                        row['timecancelsell'] = np.nan
                        row['ExposureBuy'] = np.nan
                        row['NAV'] = np.nan
                        row['feeBuy'] = np.nan

                        # คืนสถานะ รูปแบบการเทรด เพื่อสุ่มใหม่
                        row['TradeTrigger'] = np.nan

                        # ข้อมูลกระสุน sell
                        row['IDorderSell'] = np.nan
                        row['ClosePrice'] = np.nan
                        row['AmountSell'] = np.nan
                        row['feeSell'] = np.nan

                        dfTradeLogg = dfTradeLog1.drop(columns=[c for c in dfTradeLog1.columns if "Unnamed" in c]).dropna(how="all")
                        set_with_dataframe(gc.open("Data").worksheet('TradeLog'), dfTradeLogg)  # บันทึกชีทหน้า TradeLog

                    elif orderMatchedSELL['filled'] == 0:
                        # ถ้าหมดเวลา cooldown แล้วไม่ได้เปิดสักทีให้ ยกเลิกออเดอร์ลิมิต Sell
                        if pd.notna(row['timecancelsell']):
                            # ผ่านไป 10 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
                            first_time = row['timecancelsell']
                            start_time = first_time + 600  # นับถอยหลัง 10 นาที เพื่อยกเลิกออเดอร์
                            target_time = time.time()
                            timeElapsed = target_time - start_time
                            if timeElapsed > 0:
                                cancelOrder(idOrdersell)
                                # ลบ ข้อมูลกระสุนนัดนี้ เพื่อยกเลิกออเดอร์
                                # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                                row['IDorderSell'] = np.nan
                                row['ClosePrice'] = np.nan
                                row['AmountSell'] = np.nan
                                row['timecancelsell'] = np.nan


                # เงื่อนไข ยิงกระสุน sell
                if pd.isna(row['IDorderSell']):
                    NowPrice = getPrice(whatsymbol)
                    if pd.notna(row['OpenPrice']):
                        if NowPrice > (row['OpenPrice'] + (difZone*2)):  # ต้องมากกว่า อย่างน้อย 2 โซน ถึงจะปิดกำไรได้
                            # MapTrigger = -1 คือ พื้นที่ๆ ลดของที่มีอยู่ โดยลด Buy Hold ที่ถือไว้ โดย เปิด Sell เท่ากับ จำนวน Position ของกระสุนนัดนั้นๆ
                            if row['MapTrigger'] == -1 and row['Zone'] > 0:
                                checktradesell = False
                                if row['TradeTrigger'] >= 1 and row['TradeTrigger'] <= 40:
                                    getRSIvalue = RSI('1m')
                                    if getRSIvalue > 70:
                                        print(getRSIvalue)
                                        checktradesell = True
                                if row['TradeTrigger'] >= 41 and row['TradeTrigger'] <= 70:
                                    getRSIvalue = RSI('5m')
                                    if getRSIvalue > 70:
                                        print(getRSIvalue)
                                        checktradesell = True
                                if row['TradeTrigger'] >= 71 and row['TradeTrigger'] <= 90:
                                    getRSIvalue = RSI('15m')
                                    if getRSIvalue > 70:
                                        print(getRSIvalue)
                                        checktradesell = True

                                if row['TradeTrigger'] >= 91:
                                    getRSIvalue = RSI('1h')
                                    if getRSIvalue > 70:
                                        print(getRSIvalue)
                                        checktradesell = True

                                if checktradesell == True:
                                    positionSizeClose = orderMatchedBUY['filled']

                                    # เปิดออเดอร์ Sell เพื่อปิดออเดอร์ Buy
                                    orderSell = re(whatsymbol, 'limit', 'sell', positionSizeClose)

                                    row['IDorderSell'] = orderSell['id']
                                    row['ClosePrice'] = orderSell['price']
                                    row['AmountSell'] = orderSell['amount']
                                    row['timecancelsell'] = time.time()

        # เงื่อนไข ยิงกระสุน buy ใช้งานกระสุนนัดนี้
        if pd.isna(row['IDorderBuy']):
            if row['MapTrigger'] == 1 and row['Zone'] > 0 and row['Exposure'] > 0 and row['UseZone'] == 1:  # MapTrigger = 1 คือ พื้นที่ๆ ควรมีกระสุน
                checktradebuy = False

                if row['TradeTrigger'] >= 1 and row['TradeTrigger'] <= 20:
                    getRSIvalue = RSI('1m')
                    if getRSIvalue < 40:
                        checktradebuy = True
                if row['TradeTrigger'] >= 21 and row['TradeTrigger'] <= 40:
                    getRSIvalue = RSI('1m')
                    if getRSIvalue < 30:
                        checktradebuy = True

                if row['TradeTrigger'] >= 41 and row['TradeTrigger'] <= 55:
                    getRSIvalue = RSI('5m')
                    if getRSIvalue < 40:
                        checktradebuy = True
                if row['TradeTrigger'] >= 56 and row['TradeTrigger'] <= 70:
                    getRSIvalue = RSI('5m')
                    if getRSIvalue < 30:
                        checktradebuy = True

                if row['TradeTrigger'] >= 71 and row['TradeTrigger'] <= 80:
                    getRSIvalue = RSI('15m')
                    if getRSIvalue < 40:
                        checktradebuy = True
                if row['TradeTrigger'] >= 81 and row['TradeTrigger'] <= 90:
                    getRSIvalue = RSI('15m')
                    if getRSIvalue < 30:
                        checktradebuy = True

                if row['TradeTrigger'] >= 91 and row['TradeTrigger'] <= 95:
                    getRSIvalue = RSI('1h')
                    if getRSIvalue < 40:
                        checktradebuy = True
                if row['TradeTrigger'] >= 96 and row['TradeTrigger'] <= 100:
                    getRSIvalue = RSI('1h')
                    if getRSIvalue < 30:
                        checktradebuy = True
                        #ถ่วงเวลา ตอนโวเข้า
                        #df._set_value(whatsymbol, 'TimerDelay', time.time())
                        #df._set_value(whatsymbol, 'Stat', 'Cooldown')

                if checktradebuy == True :
                    # ต้นทุนกระสุนต่อนัด
                    expousre = row['Exposure']
                    # ปริมาณสินค้าที่จะตั้งออเดอร์ ต่อ กระสุน 1นัด
                    amount = abs(expousre) / float(getPrice(whatsymbol))

                    orderBuy = re(whatsymbol, 'limit', 'buy', amount)

                    row['IDorderBuy'] = orderBuy['id']
                    row['OpenPrice'] = orderBuy['price']
                    row['AmountBuy'] = orderBuy['amount']
                    row['ExposureBuy'] = orderBuy['amount'] * orderBuy['price']
                    row['timecancelbuy'] = time.time()



def re(symbol,types,side,amount):
    #types = 'limit'  # 'limit' or 'market'
    order = exchange.create_order(symbol, types, side, amount,getPrice(whatsymbol))
    #print(order)
    return order


def FindDiffZone():
    Zone = dfMap['Zone']
    # Get the difference in zone from previous step
    delta = Zone.diff()
    delta = delta.mean()
    return delta


def checkByIDoder(id):
    idStr = ('%f' % id).rstrip('0').rstrip('.') # ลบ .0 หลัง หมายเลขไอดี
    oderinfo = exchange.fetch_order(idStr)
    return oderinfo


def Getfee_ByIDoderinMyTrades(id,side):
    idStr = ('%f' % id).rstrip('0').rstrip('.')  # ลบ .0 หลัง หมายเลขไอดี
    fetchTrades = exchange.fetch_my_trades(symbol=whatsymbol, since=None, limit=2000, params={})

    fetchTrades = pd.json_normalize(data=fetchTrades)
    df_fetchTrades = pd.DataFrame(data=fetchTrades,columns=['order','info.side', 'info.fee'])
    for i, row in df_fetchTrades.iterrows():
        if row['order'] == idStr and row['info.side'] == side:
            return row['info.fee']


def cancelOrder(id):
    orderMatched = checkByIDoder(id)
    if orderMatched['status'] == 'closed': # ถ้ามัน closed ไปแล้ว แสดงว่าโดนปิดมือ
        print('mannual cancel')
    else:
        exchange.cancel_order(id)

def TimeDelayForNextTrade():
    #หลังจาก รีบาลานซ์ครั้งก่อนให้ นับถอยหลัง ถึงจะมีสิทธิ์ยิงนัดถัดไปได้
    # 1% เท่ากับ 1 ชั่วโมง
    oderinfo = OHLC(whatsymbol,3,'1h')
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr3 = oderinfo["Percent_Change"].mean()
    TimerTrigger = mean1hr3*0.6*100*60 #ความต่าง 1% เท่ากับ 1ชั่วโมง

    return TimerTrigger


#ดึงข้อมูลราคา เครดิต คุณ Sippavit Kittirattanadul
def OHLC(pair,count,typee):  # นำขั้นตอนการเรียกข้อมุล ohlc มารวมเป็น function เพื่อเรียกใช้งานได้เรื่อยๆ
    # 5m 1h 1d

    try:  # try/except ใช้แก้ error : Connection aborted https://github.com/ccxt/ccxt/wiki/Manual#error-handling
        ohlc = exchange.fetch_ohlcv(pair, timeframe=typee, limit=count)
        # print(ohlc)
    except ccxt.NetworkError as e:
        print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe=typee, limit=count)
        # retry or whatever

    except ccxt.ExchangeError as e:
        print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe=typee, limit=count)
        # retry or whatever

    except Exception as e:
        print(exchange.id, 'fetch_ohlcv failed with:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe=typee, limit=count)
        # retry or whatever

    ohlc_df = pd.DataFrame(ohlc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['datetime'], unit='ms')

    return ohlc_df

def getPrice(pair):
    r = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r)
    sendBack = float(dataPrice['last'])
    return sendBack

def get_balance(get_asset):
    result = 'result'
    listAsset = 'coin'
    params = {'recvWindow': 50000}

    balance = exchange.fetch_balance(params)
    df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
    df_balance['free'] = df_balance.free.astype(float)
    return df_balance.loc[get_asset]['free']

def LineNotify(mse,typee):
    # แจ้งเตือนผ่านไลน์เมื อเกิดการรีบาลานซ์
    # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549
    url = 'https://notify-api.line.me/api/notify'
    token = 'MQaK3NTRG0gtC4PS2pQYiJvKC44J4prFY3hAcgzZ8EE'
    headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

    if typee == 'change':
        mse = str(mse)
        msg = 'Profit : '+ mse
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)
    if typee == 'error' :
        mse = str(mse)
        msg = '\nแจ้งคนเขียน\n' + mse
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)

def RSI(timeframe):
    # ที่มา https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
    # Window length for moving average
    window_length = 14

    # Get price XRP
    datainfo = OHLC("XRP-PERP", 100,timeframe)

    # Get just the  close
    close = datainfo['close']
    # Get the difference in price from previous step
    delta = close.diff()
    # Get rid of the first row, which is NaN since it did not have a previous
    # row to calculate the differences
    delta = delta[1:]

    # Make the positive gains (up) and negative gains (down) Series
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0

    # Calculate the SMA
    roll_up = up.rolling(window_length).mean()
    roll_down = down.abs().rolling(window_length).mean()

    # Calculate the RSI based on SMA
    RS = roll_up / roll_down
    RSI = 100.0 - (100.0 / (1.0 + RS))

    datainfo['RSI'] = RSI
    # datainfo.loc[datainfo['RSI'] >= 70, 'stat'] = 70
    # datainfo.loc[(datainfo['RSI'] < 70) & (datainfo['RSI'] > 30), 'stat'] = 1
    # datainfo.loc[datainfo['RSI'] <= 30, 'stat'] = 30
    lastinfoRSI = datainfo.tail(3)
    # meanValue = lastinfoRSI['RSI'].mean()
    # print(meanValue)
    RSIValue = 0
    for i, row in lastinfoRSI.iterrows():
        RSIValue = row['RSI']

    # return RSIValue ล่าสุด
    return RSIValue

    # pd.set_option('display.max_rows', None)
    # pd.set_option('display.max_columns', None)
    # pd.set_option('display.width', None)

    # Compare graphically
    # plt.figure(figsize=(8, 6))
    # RSI.plot()
    # plt.legend(['RSI via SMA'])
    # plt.show()


###### ---------- Map   -----------###############
def Set_MapTrigger():
    NowPrice = getPrice(whatsymbol)
    df._set_value(whatsymbol, 'NowPrice', NowPrice)
    MaxZone = df.loc[whatsymbol]['MaxZone']
    MinZone = df.loc[whatsymbol]['MinZone']
    MaxLimitZone = 0.4

    DifPrice = float(NowPrice) - float(MaxLimitZone)
    # หรือ NowPrice < MaxLimitZone
    if DifPrice < 0 : # BUY
        for i, row in dfMap.iterrows():
            if row['Zone'] >= MinZone and  row['Zone'] <= MaxZone:
                row['UseZone'] = 1
            elif row['Zone'] < MinZone or row['Zone'] > MaxZone:
                row['UseZone'] = -1
            if NowPrice < row['Zone']:
                row['MapTrigger'] = 1
            elif NowPrice > row['Zone']:
                row['MapTrigger'] = -1
            if pd.notna(row['Zone']):
                if pd.isna(row['TradeTrigger']):
                    # ---- เลือกว่าจะเทรดด้วยเงื่อนไขอะไรโดยการสุ่ม 3 ทามเฟรม 6 รูปแบบ
                    row['TradeTrigger'] = random.randint(1, 100)


###### ----------Position   -----------###############
def set_Maninsheet():
    ExposureBuy = 0
    Position = 0
    BulletHold = 0
    UseZone = 0
    for i, row in dfMap.iterrows():
        # ---- ดู Exposure ที่ถือครองอยู่
        if row['ExposureBuy'] > 0:
            countExposure = row['ExposureBuy']
            ExposureBuy = ExposureBuy + countExposure
            df._set_value(whatsymbol, 'ExposureSize', ExposureBuy)
        # ---- ดู จำนวนกระสุนที่สามารถใช้ได้ในโซนที่กำหนด
        if row['UseZone'] == 1:
            UseZone = UseZone + 1
            df._set_value(whatsymbol, 'BulletLimit', UseZone)
        if row['FilledBuy'] > 0:
            # ---- ดู ขนาด Position ที่ถือครองอยู่
            countPosition = row['FilledBuy']
            Position = Position + countPosition
            df._set_value(whatsymbol, 'PositionSize', Position)
            # ---- ดู จำนวนกระสุน ที่ถือครองอยู่
            BulletHold = BulletHold + 1
            df._set_value(whatsymbol, 'BulletHold', BulletHold)
        # ---- ดู NAV กระสุนแต่ล่ะนัด
        if row['FilledBuy'] !=0 and  pd.notna(row['FilledBuy']):
            Exposurediff = row['FilledBuy'] * getPrice(whatsymbol)
            NAV = Exposurediff - row['ExposureBuy']
            row['NAV'] = NAV
    TotalBalance = df.loc[whatsymbol]['TotalBalance']
    BulletLimit = df.loc[whatsymbol]['BulletLimit']
    avgExposurePerBullet = TotalBalance / BulletLimit
    df._set_value(whatsymbol, 'avgExposurePerBullet', avgExposurePerBullet)
    df._set_value(whatsymbol, 'Balance', get_balance(Balance))
    df._set_value(whatsymbol, 'DifZone', FindDiffZone())
