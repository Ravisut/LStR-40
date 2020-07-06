#pip3 install --upgrade pip --user
import ccxt
import json
import time
import requests
import pandas as pd
import numpy as np

###########  ตั้งค่า API -------------------------------------------------------------------
whatbroker ='ftx'

if whatbroker == "ftx":
    subaccount = 'ForTest'  # ถ้ามี ซับแอคเคอร์ของ FTX
    exchange = ccxt.ftx({
        'apiKey': '------------',
        'secret': '------------',
        'enableRateLimit': True,
    })
    if subaccount == "":
        print("This is Main Account")
    else:
        exchange.headers = {
            'FTX-SUBACCOUNT': subaccount,
        }

if whatbroker == "binance":
    exchange = ccxt.binance({
        'apiKey': '--------------',
        'secret': '--------------',
        'enableRateLimit': True,
    })

if whatbroker == "kucoin":
    exchange = ccxt.kucoin({
        'apiKey': '---------------',
        'secret': '---------------',
        'password': '---------',
        'enableRateLimit': True,
    })

########### -------------------------------------------------------------

def updatee(df,AroundIndex,SubAsset):
    if whatbroker == "binance" or whatbroker == "kucoin":
        MainAsset = 'USDT'
        if SubAsset == 'BNB':
            whatsymbol = 'BNB/USDT'
        if SubAsset == 'XRP':
            whatsymbol = 'XRP/USDT'
        if SubAsset == 'BTC':
            whatsymbol = 'BTC/USDT'

    if whatbroker == "ftx":
        MainAsset = 'USD'
        if SubAsset == 'BTC':
            whatsymbol = 'BTC/USD'
        if SubAsset == 'BNB':
            whatsymbol = 'BNB/USD'
        if SubAsset == "BTC-PERPETUAL":
            whatsymbol = "BTC-PERPETUAL"


    condition_ = df.loc['Around']['Condition']
    #AroundIndex = int(_AroundIndex) #แปลง index จากสติง เป็น int เพราะ ไม่นั้นเด๊ว error ValueError: could not convert string to float

    if pd.notna(df.loc[AroundIndex, 'IDorder']):  # ช่องไอดี ว่างไหม ถ้าไม่ว่างแสดงว่า ตั้ง pending อยู่
        df = orderFilled(df, AroundIndex, '', SubAsset, 2)  # เช็ค ว่าลิมิตออเดอร์ ว่า fill ยัง
    else:
        Multiply = df.loc['Around']['Multiply']
        df._set_value(AroundIndex, 'Multiply', Multiply)
        df._set_value(AroundIndex, 'Balance', get_balance(MainAsset, 1))
        df._set_value(AroundIndex, 'Asset',get_balance(SubAsset, 1))  # ต้องมี Asset ที่ต้องการรีมาสักนิด เพื่อไม่ให้ error KeyError: 'XRP','BTC'
        df._set_value(AroundIndex, 'PriceNow', getPrice(whatsymbol))
        df._set_value(AroundIndex, 'Condition', condition_)

        if (AroundIndex == 1):  # ถ้ารีครั้งแรก
            if pd.isna(df.loc[AroundIndex, 'PriceRe']):
                PriceRe = df.loc[AroundIndex]['PriceNow']
                df._set_value(AroundIndex, 'PriceRe', PriceRe)

        difValue1 = df.loc[AroundIndex]['PriceRe']
        difValue2 = df.loc[AroundIndex]['PriceNow']
        difValue3 = float(difValue2) - float(difValue1)

        df._set_value(AroundIndex, 'Dif', difValue3)
        dif = abs(df.loc[AroundIndex]['Dif'])

        # ฟังก์ชั่นเช็ค ทุกๆ x% ทุกๆ 1 นาที
        conditionToAdjust = whatFunction(df, AroundIndex, 'percent',whatsymbol)

        if conditionToAdjust < dif:  # ถ้าส่วนต่าง (dif) มากกว่า เงื่อนไข%(conditionToAdjust) ที่ตั้งไว้ บอกสถานะว่า ได้เข้าเงื่อนไขรีบาลานซ์
            df._set_value(AroundIndex, 'Stat', 'Action')
            _Amount2 = dif / difValue2 # ปริมาณสินค้าที่จะตั้งออเดอร์
            df._set_value(AroundIndex, 'Amount', _Amount2)
            amount = df.loc[AroundIndex]['Amount']
            price = df.loc[AroundIndex]['PriceNow']

            if pd.isna(df.loc[AroundIndex, 'IDorder']):  # ถ้าช่อง ไอดีออเดอร์ยังว่าง แสดงว่าเป็นเงื่อนไขแรก ไม่มีการตั้งลิมิต

                if difValue3 < 0:  # ส่วนต่าง ถ้าขาด ให้เติมโดย ซื้อเข้า
                    df._set_value(AroundIndex, 'Side',"BUY")  # ต้อง set ค่าเริ่มต้นในชีทให้เป็น สติง ก่อน ไม่นั้นมันจะคิดว่า ช่องว่างๆ คือ ค่า float error ValueError: could not convert string to float
                    orderrr = re(whatsymbol, 'buy',MainAsset ,amount,Multiply, price)  # ยิงออเดอร์
                    df = orderFilled(df, AroundIndex, orderrr, SubAsset,1)  # ส่งข้อมูล ไอดีออเดอร์และวันที่ # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

                if difValue3 > 0:  # ส่วนต่าง ถ้าเกิน ให้ ขายออก
                    df._set_value(AroundIndex, 'Side', "SELL")
                    orderrr = re(whatsymbol, 'sell',MainAsset ,amount,Multiply, price)  # ยิงออเดอร์
                    df = orderFilled(df, AroundIndex, orderrr, SubAsset,1)  # ส่งข้อมูล ไอดีออเดอร์และวันที่ และ # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

        else:  # ยังไม่เข้าเงื่อนไข รอไปก่อน
            df._set_value(AroundIndex, 'Stat', 'Wait')  # 'Stat ' กับ 'Stat' ถ้ามีช่องว่าง คือไม่ใช่คำเดียวกัน
            # df.loc[AroundIndex, 'Stat'] = 'Wait' # แบบนี้จะสร้าง colum ใหม่

    return df


def get_balance(get_asset, typee):
    if whatbroker == "ftx":
        result = 'result'
        listAsset = 'coin'
    if whatbroker == "binance":
        result = 'balances'
        listAsset = 'asset'
    if whatbroker == "kucoin":
        result = 'data'
        listAsset = 'currency'
        typeaccount = 'type'

    params = {'recvWindow': 50000}
    balance = exchange.fetch_balance(params)

    if typee == 1: #เรียกดู จำนวน เหรียญชนิดนั้นๆ
        if whatbroker == "kucoin":
             df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index([listAsset,typeaccount])
             #df_balance['balance'] = df_balance.balance.astype(float)
             return df_balance.loc[get_asset,'trade']['balance']  # index asset index trade get ค่าจำนวน
        else:
             df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
             df_balance['free'] = df_balance.free.astype(float)
             return df_balance.loc[get_asset]['free']

    if typee == 2: #เรียกดูว่าในพอร์ตมีเหรียญอะไรบ้างเท่าไร
        if whatbroker == "kucoin":
            df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index([typeaccount,listAsset])
            df_balance['balance'] = df_balance.balance.astype(float)
            return df_balance.filter(like='trade',axis=0).loc[df_balance.balance > 0]

        else:
             df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
             df_balance['free'] = df_balance.free.astype(float)
             return df_balance.loc[df_balance.free > 0]

def getPrice(pair):
    r = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r)
    sendBack = float(dataPrice['last'])
    return sendBack

def re(symbol,side,_mainAsset,amount,Multiply,price):

    types = 'limit'  # 'limit' or 'market'
    if whatbroker == "ftx":
        order = exchange.create_order(symbol, types, side, amount*Multiply, price)
        return order

    if whatbroker == "kucoin" or whatbroker == "binance" :
        params = {
            'test': True,  # ทดสอบโดยไม่ต้องเปิดออเดอร์จริงๆ สำหรับ Binance
            'recvWindow': 10000
        }
        order = exchange.create_order(symbol, types, side, amount*Multiply, price, params)  # Limit
        #order = exchange.create_order(symbol, type, side, amount*Multiply, params)  # Market
        return order

def orderFilled(df,Around,orderrr,SubAsset,typee):

    if typee == 1: # บันทึก ไอดีออเดอร์ และวันที่ ตั้งลิมิต
        df._set_value(Around, 'IDorder', orderrr['id'])
        df._set_value(Around, 'Date', orderrr['datetime'])
        df._set_value(Around, 'Timer', time.time())

    if typee == 2: #เช็คดว่า แมต ยังหรือยัง # ต้นทางเช็คมาแล้วว่า ID ไม่ว่าง แสดงว่ามีการตั้ง Pending ออเดอร์
        id = df.loc[Around]['IDorder']
        orderMatched = checkByIDoder(id)

        if orderMatched['filled'] > 0:  # เช็ค Matched ไหม # ถ้ามากกว่า 0 แสดงว่า ลิมิตออเดอร์ แมต แล้ว..
            df._set_value(Around, 'Filled', orderMatched['filled'])

            Value1 = df.loc[Around]['Filled']
            Value2 = df.loc[Around]['PriceNow']
            Value3 = float(Value1) * float(Value2)
            df._set_value(Around, 'ValueAdjust', Value3)

            df = newrow_index(df, Around,Value2) #ขึนรอบใหม่ บรรทัดใหม่
            LineNotify(df, Around, SubAsset, 'change')
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


def newrow_index(df,Around,PriceRe):
    Around = Around+1
    # ขึ้นบรรทัดใหม่ ด้วย รอบ ที่เพิ่มขึ้น
    df1 = df[~df.index.isna()].append(pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns, index=[Around]))
    df = df1.append(df[df.index.isna()])
    df = df.rename_axis("indexAround")

    df._set_value(Around, 'PriceRe', PriceRe)
    df._set_value('Around', 'Balance', Around) #ตัวบอกรอบ
    return df

def LineNotify(df,Around,subasset,typee) :
    # แจ้งเตือนผ่านไลน์เมื ่่อเกิดการรีบาลานซ์
    # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549

    url = 'https://notify-api.line.me/api/notify'
    token = 'MQaK3NTRG0gtC4PS2pQYiJvKC44J4prFY3hAcgzZ8EE'
    headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

    if typee == 'change':
        BalanceNotify = df.loc[Around]['Balance']
        ValueNotify = df.loc[Around]['ValueAdjust']
        AsseteNotify = df.loc[Around]['Filled']

        msg = '\nขึ้นรอบใหม่แล้ว ' +str(Around)+ '\nจำนวนเงินในพอร์ตเหลือ =' + str(BalanceNotify)+'USDT \n' + 'มูลค่า =' + str(ValueNotify) +'USDT \n' + 'ปริมาณสินค้า =' + str(AsseteNotify)+' '+str(subasset)
    if typee == 'error' :
        msg = '\nแจ้งคนเขียน\n'+str(subasset)
    r = requests.post(url, headers=headers, data={'message': msg})
    print(r.text)


def whatFunction(df,Around,whatfution,whatsymbol):
    if whatfution == 'percent':
        conditionToAdjust1 = df.loc[Around]['PriceRe']
        conditionToAdjust2 = 1

        OHLC(whatsymbol)

        atr30hours = conditionToAdjust2
        conditionToAdjust3 = (float(conditionToAdjust1) / 100) * float(conditionToAdjust2) # ตรวจดูว่า เกิน 1%ยัง

        return  conditionToAdjust3

#เครดิต คุณ Sippavit Kittirattanadul
def OHLC(pair):  # นำขั้นตอนการเรียกข้อมุล ohlc มารวมเป็น function เพื่อเรียกใช้งานได้เรื่อยๆ

    try:  # try/except ใช้แก้ error : Connection aborted https://github.com/ccxt/ccxt/wiki/Manual#error-handling
        ohlc = exchange.fetch_ohlcv(pair, timeframe='5m', limit=300)
        # print(ohlc)
    except ccxt.NetworkError as e:
        print(exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='5m', limit=300)
        # retry or whatever

    except ccxt.ExchangeError as e:
        print(exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='5m', limit=300)
        # retry or whatever

    except Exception as e:
        print(exchange.id, 'fetch_ohlcv failed with:', str(e))
        ohlc = exchange.fetch_ohlcv(pair, timeframe='5m', limit=300)
        # retry or whatever

    ohlc_df = pd.DataFrame(ohlc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    ohlc_df['datetime'] = pd.to_datetime(ohlc_df['datetime'], unit='ms')
    return ohlc_df

