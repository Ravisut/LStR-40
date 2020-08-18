import ccxt
import json
import time
import requests
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
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
        'apiKey': '********************',
        'secret': '*********************',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }

########### ----------------------------------------------------------------------------
MaxZone = df.loc[whatsymbol]['MaxZone']
Multiply = df.loc[whatsymbol]['Leverage']
difZone = df.loc[whatsymbol]['DifZone']
#------------------------------

def updatee():
    # ----- ตั้งค่า Map ว่าแต่ล่ะโซนควรมีกระสุนหรือไม่-----
    Set_MapTrigger()
    # ---- ดู NAV กระสุนแต่ล่ะนัด
    Update_NAV()
    # ----- ส่วนแสดงผลในหน้า PERP --------
    df._set_value(whatsymbol, 'Balance', get_balance(Balance))
    df._set_value(whatsymbol, 'BulletHold', get_BulletHold())
    df._set_value(whatsymbol, 'PositionSize', get_Expsoure())

    if df.loc[whatsymbol]['Stat'] == 'Cooldown':
        TimerDelay = df.loc[whatsymbol]['TimerDelay']
        TimerTrigger = TimeDelayForNextTrade()
        target_time = time.time()
        timeElapsed = target_time - (TimerDelay+TimerTrigger)
        Check_orderFilled()

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

def Check_orderFilled():
    dfTradeLog1 = dfTradeLog
    for i, row in dfMap.iterrows():
        if pd.notna(row['IDorderBuy']):
            idOrderbuy = row['IDorderBuy']
            orderMatchedBUY = checkByIDoder(idOrderbuy)
            if orderMatchedBUY['filled'] == orderMatchedBUY['amount']:  # จะเปิด ออเดอร์ sell ได้ต้องมี Position Szie ด้าน Buy ก่อน
                if pd.isna(row['FilledBuy']):
                    row['Stat'] = 1  # 1 คือ กระสุนเปิด buy ลิมิตสำเร็จแมตซ์แล้ว
                    row['FilledBuy'] = orderMatchedBUY['filled']
                    row['feeBuy'] = Getfee_ByIDoderinMyTrades(idOrderbuy, orderMatchedBUY['side']) #fee
                    # บันทึก TradeLog
                    # ต้องแปลงเป็น สติงทั้งหมดไม่งั้นบันทึกไม่ได้
                    # กำหนด PD ก่อน
                    print('OpenOrder Price : '+str(orderMatchedBUY['price']))
                    print('Amount : '+str(orderMatchedBUY['filled']))
                    dfTradeLog2 = pd.DataFrame({'IDorder': [str(idOrderbuy)]
                                                    ,'Side': [str(orderMatchedBUY['side'])]
                                                    ,'Price':[str(orderMatchedBUY['price'])]
                                                    ,'Amount':[str(orderMatchedBUY['filled'])]
                                                    ,'Exposure':[str(row['ExposureBuy'])]
                                                    ,'Fee': [str(row['feeBuy'])]})
                    dfTradeLog1 = dfTradeLog1.append(dfTradeLog2, ignore_index=True) # เหตุผลที่ออก 2 ครั้ง เพราะ มันเพิ่มไปแล้วรอบแรกข้างบน และมา append อีกรอบ


                if pd.notna(row['IDorderSell']):
                    idOrdersell = row['IDorderSell']
                    orderMatchedSELL = checkByIDoder(idOrdersell)
                    if orderMatchedSELL['filled'] == orderMatchedSELL['amount']:  # sell filled แสดงว่าปิด กำไร ได้
                        row['Stat'] = 0  # 0 คือ กระสุนเปิด sell ลิมิตสำเร็จแมตซ์แล้ว
                        ExposureBuy = row['ExposureBuy']
                        ExposureSell = orderMatchedSELL['filled'] * orderMatchedSELL['price']
                        row['feeSell'] = Getfee_ByIDoderinMyTrades(idOrdersell, orderMatchedBUY['side'])  # fee
                        row['LastClosePrice'] = row['ClosePrice']
                        row['Profit'] = ExposureSell - ExposureBuy
                        row['round'] += 1
                        print('OpenOrder Price : ' + str(orderMatchedSELL['price']))
                        print('Profit : '+str(row))
                        LineNotify(row['Profit'], 'change')
                        # บันทึก TradeLog
                        dfTradeLog3 = pd.DataFrame({'IDorder': [str(idOrdersell)]
                                                       , 'Side': [str(orderMatchedSELL['side'])]
                                                       , 'Price': [str(orderMatchedSELL['price'])]
                                                       , 'Amount': [str(orderMatchedSELL['filled'])]
                                                       , 'Exposure': [str(ExposureSell)]
                                                       , 'Fee': [str(row['feeSell'])]})
                        dfTradeLog1 = dfTradeLog1.append(dfTradeLog3, ignore_index=True)

                        # ลบ ข้อมูลกระสุน เมื่อจบครบรอบ ทำให้กระสุนว่าง
                        # ข้อมูลกระสุน buy
                        row['IDorderBuy'] = np.nan
                        row['OpenPrice'] = np.nan
                        row['AmountBuy'] = np.nan
                        row['FilledBuy'] = np.nan
                        row['ExposureBuy'] = np.nan
                        row['NAV'] = np.nan

                        # ข้อมูลกระสุน sell
                        row['IDorderSell'] = np.nan
                        row['ClosePrice'] = np.nan
                        row['AmountSell'] = np.nan

            if row['MapTrigger'] == -1 and orderMatchedBUY['filled'] == 0:
                row['Stat'] = 0  # 0 ยกเลิกมิมิต buy
                cancelOrder(idOrderbuy)
                # ลบ ข้อมูลกระสุนด้าน Buyนัดนี้ เมื่อยกเลิกออเดอร์
                # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                row['IDorderBuy'] = np.nan
                row['OpenPrice'] = np.nan
                row['AmountBuy'] = np.nan
                row['FilledBuy'] = np.nan
                row['ExposureBuy'] = np.nan


    dfTradeLogg = dfTradeLog1.drop(columns=[c for c in dfTradeLog1.columns if "Unnamed" in c]).dropna(how="all")
    set_with_dataframe(gc.open("Data").worksheet('TradeLog'), dfTradeLogg)  # บันทึกชีทหน้า TradeLog

def Trigger_trade():
    for i, row in dfMap.iterrows():
        if pd.notna(row['IDorderBuy']):
            idOrderbuy = row['IDorderBuy']
            orderMatchedBUY = checkByIDoder(idOrderbuy)
            if orderMatchedBUY['filled'] == 0:  # ถ้าหมดเวลา cooldown แล้วไม่ได้เปิดสักทีให้ ยกเลิกออเดอร์ลิมิต
                row['Stat'] = 0  # 0 ยกเลิกมิมิต buy
                cancelOrder(idOrderbuy)
                # ลบ ข้อมูลกระสุนด้าน Buyนัดนี้ เมื่อยกเลิกออเดอร์
                # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                row['IDorderBuy'] = np.nan
                row['OpenPrice'] = np.nan
                row['AmountBuy'] = np.nan
                row['FilledBuy'] = np.nan
                row['ExposureBuy'] = np.nan

            elif orderMatchedBUY['filled'] == orderMatchedBUY['amount']:  # จะเปิด ออเดอร์ sell ได้ต้องมี Position Szie ด้าน Buy ก่อน
                if pd.notna(row['IDorderSell']):
                    idOrdersell = row['IDorderSell']
                    orderMatchedSELL = checkByIDoder(idOrdersell)
                    if orderMatchedSELL['filled'] == 0:  # ถ้าหมดเวลา cooldown แล้วไม่ได้เปิดสักทีให้ ยกเลิกออเดอร์ลิมิต
                        cancelOrder(idOrdersell)
                        # ลบ ข้อมูลกระสุนด้าน Buyนัดนี้ เพื่อยกเลิกออเดอร์
                        # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                        row['IDorderSell'] = np.nan
                        row['ClosePrice'] = np.nan
                        row['AmountSell'] = np.nan

                # เงื่อนไข ยิงกระสุน sell
                if pd.isna(row['IDorderSell']):
                    NowPrice = getPrice(whatsymbol)
                    if pd.notna(row['OpenPrice']):
                        if NowPrice > (row['OpenPrice'] + (difZone*3)):  # ต้องมากกว่า อย่างน้อย 3 โซน ถึงจะปิดกำไรได้
                            # MapTrigger = -1 คือ พื้นที่ๆ ลดของที่มีอยู่ โดยลด Buy Hold ที่ถือไว้ โดย เปิด Sell เท่ากับ จำนวน Position ของกระสุนนัดนั้นๆ
                            if row['MapTrigger'] == -1 and row['Zone'] > 0:
                                row['Stat'] = 2  # 2 คือ sell ลิมิต เพื่อปิดกระสุนนัดนี้
                                positionSizeClose = orderMatchedBUY['filled']

                                # เปิดออเดอร์ Sell เพื่อปิดออเดอร์ Buy
                                orderSell = re(whatsymbol, 'limit', 'sell', positionSizeClose)

                                row['IDorderSell'] = orderSell['id']
                                row['ClosePrice'] = orderSell['price']
                                row['AmountSell'] = orderSell['amount']

                                # ถ้าเปิดออเดอร์ให้ ตั้งเวลานับถอยหลัง
                                df._set_value(whatsymbol, 'TimerDelay', time.time())
                                df._set_value(whatsymbol, 'Stat', 'Cooldown')


        # เงื่อนไข ยิงกระสุน buy ใช้งานกระสุนนัดนี้
        if pd.isna(row['IDorderBuy']):
            if row['MapTrigger'] == 1 and row['Zone'] > 0 and row['Exposure'] > 0:  # MapTrigger = 1 คือ พื้นที่ๆ ควรมีกระสุน
                row['Stat'] = -1  # -1 ตั้งลิมิต buy
                expousre = row['Exposure'] * Multiply # คูณเลเวอเรจ
                amount = abs(expousre) / float(getPrice(whatsymbol))  # ปริมาณสินค้าที่จะตั้งออเดอร์ ต่อ กระสุน 1นัด

                orderBuy = re(whatsymbol, 'limit', 'buy', amount)

                row['IDorderBuy'] = orderBuy['id']
                row['OpenPrice'] = orderBuy['price']
                row['AmountBuy'] = orderBuy['amount']
                row['ExposureBuy'] = orderBuy['amount'] * orderBuy['price']

                # ถ้าเปิดออเดอร์ให้ ตั้งเวลานับถอยหลัง
                df._set_value(whatsymbol, 'TimerDelay', time.time())
                df._set_value(whatsymbol, 'Stat', 'Cooldown')


def re(symbol,types,side,amount):
    #types = 'limit'  # 'limit' or 'market'
    order = exchange.create_order(symbol, types, side, amount,getPrice(whatsymbol))
    #print(order)
    return order


def checkByIDoder(id):
    idStr = ('%f' % id).rstrip('0').rstrip('.') # ลบ .0 หลัง หมายเลขไอดี
    oderinfo = exchange.fetch_order(idStr)
    return oderinfo

#เครดิตพี่นัท LazyTrader
def Getfee_ByIDoderinMyTrades(id,side):
    idStr = ('%f' % id).rstrip('0').rstrip('.')  # ลบ .0 หลัง หมายเลขไอดี
    fetchTrades = exchange.fetch_my_trades(symbol=whatsymbol, since=None, limit=2000, params={})

    fetchTrades = pd.json_normalize(data=fetchTrades)
    df_fetchTrades = pd.DataFrame(data=fetchTrades,columns=['info.id','info.side', 'info.fee'])
    #print(df_fetchTrades)
    #print(idStr)
    for i, row in df_fetchTrades.iterrows():
        if row['info.id'] == idStr and row['info.side'] == side:
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
    oderinfo = OHLC(whatsymbol,3)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr3 = oderinfo["Percent_Change"].mean()
    TimerTrigger = mean1hr3*0.6*100*60 #ความต่าง 1% เท่ากับ 1ชั่วโมง

    return TimerTrigger


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

###### ---------- Map   -----------###############
def Set_MapTrigger():
    NowPrice = getPrice(whatsymbol)
    df._set_value(whatsymbol, 'NowPrice', NowPrice)
    DifPrice = float(NowPrice) - float(MaxZone)
    if DifPrice < 0: # BUY
        for i, row in dfMap.iterrows():
            if NowPrice < row['Zone']:
                row['MapTrigger'] = 1
            if NowPrice > row['Zone']:
                row['MapTrigger'] = -1

### -------- find min zone as can sell ----------
def get_diff():
    difff = []
    for i, row in dfMap.iterrows():
        difff[i] = row['Zone']
        diffA = difff[i] - difff[i-1]
        return diffA


def get_V():
    priceList = []
    for i, row in dfMap.iterrows():
        if row['ExposureBuy'] > 0 :
            priceList[i] = row['ExposureBuy']
            if pd.isna(row['ExposureBuy']):
                return priceList[i-1]


###### ----------Position   -----------###############
def get_Expsoure():
    ExposureBuy = 0
    for i, row in dfMap.iterrows():
        if row['ExposureBuy'] > 0:
            count = row['ExposureBuy']
            ExposureBuy = ExposureBuy +count
    return ExposureBuy

def get_BulletHold():
    BulletHold = 0
    for i, row in dfMap.iterrows():
        if row['Stat'] == 1:
            BulletHold = BulletHold +1
    return BulletHold

def Update_NAV():
    for i, row in dfMap.iterrows():
        if row['FilledBuy'] !=0 and  pd.notna(row['FilledBuy']):
            Exposurediff = row['FilledBuy'] * getPrice(whatsymbol)
            NAV = Exposurediff - row['ExposureBuy'] #บัคเดิมคือ row['Exposure'] ทำให้มันไป ลบ exposure มาคอัพแทน exposure จริงที่เปิดได้
            row['NAV'] = NAV




### ----- ฟังก์ชั่นเก่าไม่ใช้งาน ไม่มีผลกับโปรแกรม XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
def LoadMap():
    # Load MapBuy
    Exposure = 1
    RangMap = 10
    dfMapBuy = pd.DataFrame({'Zone': [], 'Exposure': []})
    for i in range(RangMap):
        Price = difZone * i
        Zone = MaxZone + Price

    dfMapBuy = dfMapBuy.append({'Zone': Zone, 'Exposure': Exposure}, ignore_index=True)
    set_with_dataframe(gc.open("Data").worksheet('SetMap'), dfMapBuy)

def tradeFunction():
    ExposureRerate = df.loc[whatsymbol]['ExposureRerate']
    ExposureRerate = float(ExposureRerate)
    Price = getPrice(whatsymbol)
    DifPercent = abs(ExposureRerate - Price) / (ExposureRerate / 100)
    minPercent = 0.5
    oderinfo = OHLC(whatsymbol,168)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr168 = oderinfo["Percent_Change"].mean()
    minPercentToAdjust = (float(ExposureRerate) / 100) * float(minPercent)  # ตรวจดูว่า เกิน 0.5%ยัง
    if mean1hr168 > minPercentToAdjust:
        if DifPercent > mean1hr168:
            return True  # เข้าเงื่อนไขจริง
    else:
        return False #https://stackoverflow.com/questions/19498572/why-do-i-get-none-instead-of-true-false-in-python

def orderFilled(Multiply): #เช็คดว่า แมต ยังหรือยัง # ต้นทางเช็คมาแล้วว่า ID ไม่ว่าง แสดงว่ามีการตั้ง Pending ออเดอร์
    global df
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

        # ตั้งดีเลย์สำหรับการเทรดครั้งถัดไป
        BulletHold = df.loc[whatsymbol]['BulletHold']
        Trigger = df.loc[whatsymbol]['Trigger']
        if Trigger == BulletHold:
            df = TimeDelayForNextTrade()
            LineNotify('change')

    else:
        if orderMatched['type'] == 'limit':
            # ผ่านไป 10 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
            first_time = df.loc[whatsymbol]['Timer']
            start_time = first_time + 600  # นับถอยหลัง 10 นาที เพื่อยกเลิกออเดอร์
            target_time = time.time()
            timeElapsed = target_time - start_time
            if timeElapsed > 0:
                cancelOrder(id)