#pip3 install --upgrade pip --user
import ccxt
import json
import time
import requests
import pandas as pd
import numpy as np

#### รายละเอียด ก่อนเทรด -------------------------------------------------------
Balance = 'USD'
Asset = 'TRX'
###########  ตั้งค่า API -------------------------------------------------------
subaccount = 'ForTest'  # ถ้ามี ซับแอคเคอร์ของ FTX
exchange = ccxt.ftx({
        'apiKey': '-----------',
        'secret': '-----------',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }
########### ตั้งค่า สินค้าที่จะเทรด ---------------------------------------------------
if Asset == "BTC":
    whatsymbol = "BTC-PERP"
if Asset == "XRP":
    whatsymbol = "XRP-PERP"
if Asset == 'TRX':
    whatsymbol = "TRX-PERP"
########### ----------------------------------------------------------------------------

def updatee(df,AroundIndex):
    if pd.notna(df.loc[AroundIndex, 'IDorder']):  # ช่องไอดี ว่างไหม ถ้าไม่ว่างแสดงว่า ตั้ง pending อยู่
        df = orderFilled(df, AroundIndex,'','Filled')  # เช็ค ว่าลิมิตออเดอร์ ว่า fill ยัง
    else:
        Multiply = df.loc['Around']['Multiply']
        ExposurePointer = df.loc['Around']['ExposureReal']
        exposurePointer = df.loc['Around']['ExposureRerate']

        df._set_value(AroundIndex, 'Balance', get_balance(Balance))
        df._set_value(AroundIndex, 'Multiply', Multiply)
        df._set_value(AroundIndex, 'ExposureReal', ExposurePointer)
        df._set_value(AroundIndex, 'ExposureRerate', exposurePointer)
        df._set_value(AroundIndex, 'Price', getPrice(whatsymbol))

        price = getPrice(whatsymbol)
        difValue = float(exposurePointer) - float(price)
        difToAmount = abs(difValue)
        df._set_value(AroundIndex, 'Dif', difValue)

        if exposurePointer == 0 :
            df._set_value('Around', 'ExposureRerate', getPrice(whatsymbol))
            return df

        # ฟังก์ชั่นเช็ค ทุกๆ x% ทุกๆ 1 นาที
        conditionToAdjust = tradeFunction(df, AroundIndex,whatsymbol)
        df._set_value(AroundIndex, 'Condition', conditionToAdjust)

        if  conditionToAdjust == True  :  # ถ้าส่วนต่าง (dif) มากกว่า เงื่อนไข%(conditionToAdjust) ที่ตั้งไว้ บอกสถานะว่า ได้เข้าเงื่อนไขรีบาลานซ์
            df._set_value(AroundIndex, 'Stat', 'Action')
            _Amount = difToAmount / price # ปริมาณสินค้าที่จะตั้งออเดอร์
            df._set_value(AroundIndex, 'Amount', _Amount)
            amount = df.loc[AroundIndex]['Amount']
            price = df.loc[AroundIndex]['Price']

            if pd.isna(df.loc[AroundIndex, 'IDorder']):  # ถ้าช่อง ไอดีออเดอร์ยังว่าง แสดงว่าเป็นเงื่อนไขแรก ไม่มีการตั้งลิมิต

                if difValue < 0:  # ส่วนต่าง ถ้าขาด ให้เติมโดย ซื้อเข้า
                    df._set_value(AroundIndex, 'Side',"BUY")  # ต้อง set ค่าเริ่มต้นในชีทให้เป็น สติง ก่อน ไม่นั้นมันจะคิดว่า ช่องว่างๆ คือ ค่า float error ValueError: could not convert string to float
                    orderrr = re(whatsymbol, 'buy',Balance ,amount,Multiply, price)  # ยิงออเดอร์
                    df = orderFilled(df, AroundIndex, orderrr,'SetOrder',Multiply)  # ส่งข้อมูล ไอดีออเดอร์และวันที่ # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

                if difValue > 0:  # ส่วนต่าง ถ้าเกิน ให้ ขายออก
                    df._set_value(AroundIndex, 'Side', "SELL")
                    orderrr = re(whatsymbol, 'sell',Balance ,amount,Multiply, price)  # ยิงออเดอร์
                    df = orderFilled(df, AroundIndex, orderrr,'SetOrder',Multiply)  # ส่งข้อมูล ไอดีออเดอร์และวันที่ และ # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

        else:  # ยังไม่เข้าเงื่อนไข รอไปก่อน
            print(conditionToAdjust)
            df._set_value(AroundIndex, 'Condition', conditionToAdjust)
            df._set_value(AroundIndex, 'Stat', 'Wait')  # 'Stat ' กับ 'Stat' ถ้ามีช่องว่าง คือไม่ใช่คำเดียวกัน
    return df


def get_balance(get_asset):
    result = 'result'
    listAsset = 'coin'
    params = {'recvWindow': 50000}

    balance = exchange.fetch_balance(params)
    df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
    df_balance['free'] = df_balance.free.astype(float)
    return df_balance.loc[get_asset]['free']


#def getfreeCol(): #Get Free Collatoral
    #freeCol = exchange.private_get_wallet_balances()['result'][0]['free']
#    return freeCol


def getPrice(pair):
    r = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r)
    sendBack = float(dataPrice['last'])
    return sendBack

def re(symbol,side,_mainAsset,amount,Multiply,price):
    types = 'limit'  # 'limit' or 'market'
    order = exchange.create_order(symbol, types, side, amount * Multiply, price)
    return order

def orderFilled(df,Around,order,typee,Multiply):

    if typee == 'SetOrder': # บันทึก ไอดีออเดอร์ และวันที่ ตั้งลิมิต
        df._set_value(Around, 'IDorder', order['id']) #รับไอดี
        df._set_value(Around, 'Date', order['datetime'])
        df._set_value(Around, 'Timer', time.time())

    if typee == 'Filled': #เช็คดว่า แมต ยังหรือยัง # ต้นทางเช็คมาแล้วว่า ID ไม่ว่าง แสดงว่ามีการตั้ง Pending ออเดอร์
        id = df.loc[Around]['IDorder']
        orderMatched = checkByIDoder(id)

        if orderMatched['filled'] > 0:  # เช็ค Matched ไหม # ถ้ามากกว่า 0 แสดงว่า ลิมิตออเดอร์ แมต แล้ว..
            if orderMatched['filled'] == orderMatched['amount']: # ถ้าแมตแล้ว จำนวนตรงกัน
                # เติมข้อมูล ออเดอร์ที่แมตแล้ว พร้อมคำนวณ exposure
                df._set_value(Around, 'Filled', orderMatched['filled'])
                PositionSize = orderMatched['filled'] * orderMatched['price']

                if orderMatched['side'] == 'buy':
                    PositionSizeAdjust = PositionSize * (-1)
                    df._set_value(Around, 'PositionSize', PositionSizeAdjust)
                    ExposurePointer = df.loc[Around]['ExposureReal'] + PositionSizeAdjust
                    exposurePointer = ExposurePointer/Multiply
                    df._set_value('Around', 'ExposureReal', ExposurePointer)
                    df._set_value('Around', 'ExposureRerate', exposurePointer)

                if orderMatched['side'] == 'sell':
                    PositionSizeAdjust = PositionSize
                    df._set_value(Around, 'PositionSize', PositionSizeAdjust)
                    ExposurePointer = df.loc[Around]['ExposureReal'] + PositionSizeAdjust
                    exposurePointer = ExposurePointer / Multiply
                    df._set_value('Around', 'ExposureReal', ExposurePointer)
                    df._set_value('Around', 'ExposureRerate', exposurePointer)

            df._set_value(Around, 'Filled', orderMatched['filled'])
            df._set_value(Around, 'Fee', orderMatched['fee'])
            df = newrow_index(df, Around) #ขึนรอบใหม่ บรรทัดใหม่
            LineNotify(df, Around, 'change')
        else:
            if orderMatched['type'] == 'limit':
                # ผ่านไป 10 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
                first_time = df.loc[Around]['Timer']
                start_time = first_time + 600  # นับถอยหลัง 10 นาที เพื่อยกเลิกออเดอร์
                target_time = time.time()
                timeElapsed = target_time - start_time
                if timeElapsed > 0:
                    cancelOrder(df, Around, id)
    return df


def checkByIDoder(id):
    oderinfo = exchange.fetch_order(id)
    return oderinfo

def cancelOrder(df,Around,id):
    exchange.cancel_order(id)
    # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
    df._set_value(Around, 'IDorder', '')
    df._set_value(Around, 'Amount', '')
    df._set_value(Around, 'Date', '')
    df._set_value(Around, 'Timer', '')


def newrow_index(df,Around):
    Around = Around+1
    # ขึ้นบรรทัดใหม่ ด้วย รอบ ที่เพิ่มขึ้น
    df1 = df[~df.index.isna()].append(pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns, index=[Around]))
    df = df1.append(df[df.index.isna()])
    df = df.rename_axis("indexAround")

    df._set_value('Around', 'Balance', Around) #ตัวบอกรอบ !!! ไม่เกี่ยวอะไรกับ Balace แค่ช่องมันว่างเฉยๆ
    return df

def tradeFunction(df,Around,whatsymbol):
    ExposureRerate = df.loc['Around']['ExposureRerate']
    Price = df.loc[Around]['Price']
    dif = abs(ExposureRerate - Price) / (ExposureRerate / 100)
    minPercent = 0.5

    oderinfo = OHLC(whatsymbol)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean4hr180 = oderinfo["Percent_Change"].mean()
    print(dif)
    print(mean4hr180)
    minPercentToAdjust = (float(ExposureRerate) / 100) * float(minPercent)  # ตรวจดูว่า เกิน 0.5%ยัง

    if mean4hr180 > minPercentToAdjust:
        if dif > mean4hr180:
            return True #เข้าเงื่อนไขจริง
    else:
        return False


#ดึงข้อมูลราคา เครดิต คุณ Sippavit Kittirattanadul
def OHLC(pair):  # นำขั้นตอนการเรียกข้อมุล ohlc มารวมเป็น function เพื่อเรียกใช้งานได้เรื่อยๆ

    try:  # try/except ใช้แก้ error : Connection aborted https://github.com/ccxt/ccxt/wiki/Manual#error-handling
        ohlc = exchange.fetch_ohlcv(pair, timeframe='4h', limit=180)
        # print(ohlc)
    except ccxt.NetworkError as e:
        print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1d', limit=30)
        # retry or whatever

    except ccxt.ExchangeError as e:
        print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1d', limit=30)
        # retry or whatever

    except Exception as e:
        print(exchange.id, 'fetch_ohlcv failed with:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='1d', limit=30)
        # retry or whatever

    ohlc_df = pd.DataFrame(ohlc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['datetime'], unit='ms')

    return ohlc_df

def LineNotify(df,Around,typee) :
    # แจ้งเตือนผ่านไลน์เมื ่่อเกิดการรีบาลานซ์
    # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549
    url = 'https://notify-api.line.me/api/notify'
    token = 'MQaK3NTRG0gtC4PS2pQYiJvKC44J4prFY3hAcgzZ8EE'
    headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

    if typee == 'change':
        PositionSize = df.loc[Around]['PositionSize']
        Exposure = df.loc['Around']['ExposureReal']
        msg = Exposure+PositionSize
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)
    if typee == 'error' :
        msg = '\nแจ้งคนเขียน\n'
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)