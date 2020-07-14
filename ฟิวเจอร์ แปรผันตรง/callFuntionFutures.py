import ccxt
import json
import time
import requests
import pandas as pd
import numpy as np

#### รายละเอียด ก่อนเทรด -------------------------------------------------------
Balance = 'USD'
whatsymbol = "XRP-PERP"
###########  ตั้งค่า API -------------------------------------------------------
subaccount = '-------'  # ถ้ามี ซับแอคเคอร์ของ FTX
exchange = ccxt.ftx({
        'apiKey': '----------------',
        'secret': '-----------------',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }

########### ----------------------------------------------------------------------------

def updatee(df,AroundIndex):
    if df.loc[AroundIndex]['Stat'] == 'Cooldown':
        first_time = df.loc[AroundIndex]['Timer']
        target_time = time.time()
        timeElapsed = target_time - first_time
        if timeElapsed > 0:
            df._set_value(AroundIndex, 'Stat', '')
            df._set_value(AroundIndex, 'Timer', '')
    else:
        Multiply = df.loc['Around']['Multiply']
        if pd.notna(df.loc[AroundIndex, 'IDorder']):  # ช่องไอดี ว่างไหม ถ้าไม่ว่างแสดงว่า ตั้ง pending อยู่
            df = orderFilled(df, AroundIndex, Multiply)  # เช็ค ว่าลิมิตออเดอร์ ว่า fill ยัง
        else:
            df._set_value(AroundIndex, 'Balance', get_balance(Balance))
            df._set_value(AroundIndex, 'Multiply', Multiply)

            ExposurePointer = df.loc['Around']['ExposureReal']
            price = getPrice(whatsymbol)
            ExposurePointer = float(ExposurePointer)

            if ExposurePointer == 0:  # รันบอทครั้งแรก ยิง position size = ราคา
                difValue = 0 - price
                amount = abs(difValue) / price  # ปริมาณสินค้าที่จะตั้งออเดอร์
                conditionToAdjust = True

            if ExposurePointer > 0:
                exposurePointer = df.loc['Around']['ExposureRerate']
                df._set_value(AroundIndex, 'ExposureRerate', exposurePointer)
                df._set_value(AroundIndex, 'ExposureReal', ExposurePointer)
                df._set_value(AroundIndex, 'Price', getPrice(whatsymbol))
                difValue = float(exposurePointer) - float(price)
                amount = abs(difValue) / price  # ปริมาณสินค้าที่จะตั้งออเดอร์
                # ฟังก์ชั่นเช็ค ทุกๆ x% ทุกๆ 1 นาที
                conditionToAdjust = tradeFunction(df, AroundIndex, whatsymbol)

                #### ปัญหาาา ******************* เกิด ไอตัวคูณซ้ำๆ แล้วมันมากกว่า ราคา เลย ออกออเดอร์ buy
            if conditionToAdjust == True:  # ถ้าส่วนต่าง (dif) มากกว่า เงื่อนไข%(conditionToAdjust) ที่ตั้งไว้ บอกสถานะว่า ได้เข้าเงื่อนไขรีบาลานซ์
                if pd.isna(df.loc[AroundIndex, 'IDorder']):  # ถ้าช่อง ไอดีออเดอร์ยังว่าง แสดงว่าเป็นเงื่อนไขแรก ไม่มีการตั้งลิมิต
                    df._set_value(AroundIndex, 'Stat', 'Action')
                    if difValue > 0:  # ถ้าส่วนต่าง เป็นบวกแสดงว่า ราคา ต่ำกว่า exposure
                        df._set_value(AroundIndex, 'Side',"BUY")  # ต้อง set ค่าเริ่มต้นในชีทให้เป็น สติง ก่อน ไม่นั้นมันจะคิดว่า ช่องว่างๆ คือ ค่า float error ValueError: could not convert string to float
                        df = re(df, AroundIndex, whatsymbol, 'buy', amount, Multiply, price)  # ยิงออเดอร์
                    if difValue < 0:  # ถ้าส่วนต่าง ติดลบแสดงว่า ราคา สูงกว่า exposure
                        df._set_value(AroundIndex, 'Side', "SELL")
                        df = re(df, AroundIndex, whatsymbol, 'sell', amount, Multiply, price)  # ยิงออเดอร์
            else:  # ยังไม่เข้าเงื่อนไข รอไปก่อน
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

def getPrice(pair):
    r = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r)
    sendBack = float(dataPrice['last'])
    return sendBack

def re(df,Around,symbol,side,amount,Multiply,price):
    types = 'limit'  # 'limit' or 'market'
    _amount = amount* Multiply
    order = exchange.create_order(symbol, types, side, _amount, price)

    df._set_value(Around, 'Amount',_amount)
    df._set_value(Around, 'IDorder', order['id'])  # รับไอดี
    df._set_value(Around, 'Date', order['datetime'])
    df._set_value(Around, 'Timer', time.time())
    return df

def orderFilled(df,Around,Multiply): #เช็คดว่า แมต ยังหรือยัง # ต้นทางเช็คมาแล้วว่า ID ไม่ว่าง แสดงว่ามีการตั้ง Pending ออเดอร์
    id = df.loc[Around]['IDorder']
    orderMatched = checkByIDoder(id)
    if orderMatched['filled'] > 0:  # เช็ค Matched ไหม # ถ้ามากกว่า 0 แสดงว่า ลิมิตออเดอร์ แมต แล้ว..
        if orderMatched['filled'] == orderMatched['amount']:  # ถ้าแมตแล้ว จำนวนตรงกัน
            # เติมข้อมูล ออเดอร์ที่แมตแล้ว พร้อมคำนวณ exposure
            df._set_value(Around, 'Filled', orderMatched['filled'])
            PositionSize = orderMatched['filled'] * orderMatched['price']
            if orderMatched['side'] == 'buy':
                PositionSize = PositionSize * (-1)

            df._set_value(Around, 'PositionSize', PositionSize)
            df._set_value(Around, 'Fee', orderMatched['fee'])
            df._set_value(Around, 'Cost', orderMatched['cost'])

            ExposurePointer = df.loc['Around']['ExposureReal'] + PositionSize
            exposurePointer = ExposurePointer / float(Multiply)
            df._set_value('Around', 'ExposureReal', ExposurePointer)
            df._set_value('Around', 'ExposureRerate', exposurePointer)

        df._set_value(Around, 'Filled', orderMatched['filled'])
        df._set_value(Around, 'Fee', orderMatched['fee'])
        df = newrow_index(df, Around)  # ขึนรอบใหม่ บรรทัดใหม่
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
    orderMatched = checkByIDoder(id)
    if orderMatched['status'] == 'closed':
        print('mannual cancel')
    else:
        exchange.cancel_order(id)
        # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
    df._set_value(Around, 'Amount', '')
    df._set_value(Around, 'IDorder', '')
    df._set_value(Around, 'Date', '')
    df._set_value(Around, 'Timer', '')



def newrow_index(df,Around):
    Around = Around+1
    # ขึ้นบรรทัดใหม่ ด้วย รอบ ที่เพิ่มขึ้น
    df1 = df[~df.index.isna()].append(pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns, index=[Around]))
    df = df1.append(df[df.index.isna()])
    df = df.rename_axis("indexAround")

    df._set_value('Around', 'Balance', Around) #ตัวบอกรอบ !!! ไม่เกี่ยวอะไรกับ Balace แค่ช่องมันว่างเฉยๆ

    #หลังจาก รีบาลานซ์ครั้งก่อนให้ นับถอยหลัง ถึงจะมีสิทธิ์ยิงนัดถัดไปได้
    # 1% เท่ากับ 1 ชั่วโมง
    oderinfo = OHLC(whatsymbol,3)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr3 = oderinfo["Percent_Change"].mean()
    cooldownTime = 0.6*mean1hr3*100*60


    df._set_value(Around, 'Timer', time.time()+cooldownTime)
    df._set_value(Around, 'Stat', 'Cooldown')
    return df

def tradeFunction(df,Around,symbol):
    ExposureRerate = df.loc['Around']['ExposureRerate']
    ExposureRerate = float(ExposureRerate)
    Price = getPrice(symbol)
    dif = abs(ExposureRerate - Price) / (ExposureRerate / 100)
    minPercent = 0.5

    oderinfo = OHLC(symbol,168)
    oderinfo['Percent_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))
    mean1hr168 = oderinfo["Percent_Change"].mean()

    df._set_value(Around, 'Dif', ExposureRerate - Price)
    df._set_value(Around, 'DifPercent', dif)
    df._set_value(Around, 'Condition', mean1hr168)

    minPercentToAdjust = (float(ExposureRerate) / 100) * float(minPercent)  # ตรวจดูว่า เกิน 0.5%ยัง

    if mean1hr168 > minPercentToAdjust:
        if dif > mean1hr168:
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

def LineNotify(df,Around,typee) :
    # แจ้งเตือนผ่านไลน์เมื ่่อเกิดการรีบาลานซ์
    # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549
    url = 'https://notify-api.line.me/api/notify'
    token = 'MQaK3NTRG0gtC4PS2pQYiJvKC44J4prFY3hAcgzZ8EE'
    headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

    if typee == 'change':
        PositionSize = df.loc[Around]['PositionSize']
        Exposure = df.loc['Around']['ExposureReal']
        msg = PositionSize
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)
    if typee == 'error' :
        msg = '\nแจ้งคนเขียน\n'
        r = requests.post(url, headers=headers, data={'message': msg})
        print(r.text)