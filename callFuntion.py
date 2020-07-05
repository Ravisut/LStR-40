import tradeFuntion

import ccxt
import json
import time
import requests
import pandas as pd
import numpy as np

###########  ตั้งค่า API -------------------------------------------------------------------
whatbroker ='kucoin'
MainAsset = 'USDT'

if whatbroker == "binance":
    result = 'balances'
    listAsset = 'asset'
    exchange = ccxt.binance({
        'apiKey': '---------------',
        'secret': '----------------',
        'enableRateLimit': True,
    })

if whatbroker == "kucoin":
    result = 'data'
    listAsset = 'currency'
    typeaccount = 'type'
    exchange = ccxt.kucoin({
        'apiKey': '----------------',
        'secret': '----------------',
        'password': '-----------',
        'enableRateLimit': True,
    })

if whatbroker == "ftx":
    result = 'result'
    listAsset = 'coin'
    subaccount = 'ForTest'  # ถ้ามี ซับแอคเคอร์ของ FTX
    exchange = ccxt.ftx({
        'apiKey': '--------------------',
        'secret': '---------------------',
        'enableRateLimit': True,
    })
    if subaccount == "":
        print("This is Main Account")
    else:
        exchange.headers = {
            'FTX-SUBACCOUNT': subaccount,
        }

########### -------------------------------------------------------------

def updatee(df,AroundIndex,SubAsset):
    if SubAsset == 'BNB':
        whatsymbol = 'BNB/USDT'
    if SubAsset == 'XRP':
        whatsymbol = 'XRP/USDT'

    #ตัวกำหนด ว่าจะให้ รีบาลานซ ที่มูลค่าเท่าไร และกี่ % โดยอ้างอิงตัวเลขใน google sheet
    Value = df.loc['Around']['Value']
    condition_ = df.loc['Around']['Condition']

    #AroundIndex = int(_AroundIndex) #แปลง index จากสติง เป็น int เพราะ ไม่นั้นเด๊ว error ValueError: could not convert string to float

    df._set_value(AroundIndex, 'Value', Value)
    df._set_value(AroundIndex, 'Balance', get_balance(MainAsset,1))
    df._set_value(AroundIndex, 'Asset', get_balance(SubAsset,1)) # ต้องมี Asset ที่ต้องการรีมาสักนิด เพื่อไม่ให้ error KeyError: 'XRP'
    #df._set_value(AroundIndex, 'Asset', 50000)  #จำลอง สินค้า
    df._set_value(AroundIndex, 'Price', getPrice(whatsymbol))
    df._set_value(AroundIndex, 'Condition', condition_)

    Nav1 = df.loc[AroundIndex]['Asset']
    Nav2 = df.loc[AroundIndex]['Price']
    Nav3 = float(Nav1) * float(Nav2)
    df._set_value(AroundIndex, 'NAV', Nav3)

    difValue1 = df.loc[AroundIndex]['Value']
    difValue2 = df.loc[AroundIndex]['NAV']
    difValue3 = float(difValue2) - float(difValue1)

    df._set_value(AroundIndex, 'Dif', difValue3)
    dif = abs(df.loc[AroundIndex]['Dif'])


    if df.loc[AroundIndex, 'IDorder'] != 'x0':  # ช่องไอดี ว่างไหม ถ้าไม่ว่างแสดงว่า ตั้ง pending อยู่
        #print(df.loc[AroundIndex, 'IDorder'])
        df = orderFilled(df, AroundIndex, '', SubAsset, 2)  # เช็ค ว่าลิมิตออเดอร์ ว่า fill ยัง
    else:
        # ฟังก์ชั่นเช็ค ทุกๆ x% ทุกๆ 1 นาที
        conditionToAdjust = tradeFuntion.whatFunction(df, AroundIndex, 'percent')

        if conditionToAdjust < dif:  # ถ้าส่วนต่าง (dif) มากกว่า เงื่อนไข%(conditionToAdjust) ที่ตั้งไว้ บอกสถานะว่า ได้เข้าเงื่อนไขรีบาลานซ์
            Stat = 'Action'
            df.loc[AroundIndex, 'Stat'] = Stat
            _Amount1 = abs(difValue3)
            _Amount2 = _Amount1 / Nav2
            df._set_value(AroundIndex, 'Amount', _Amount2)
            amount = df.loc[AroundIndex]['Amount']
            price = df.loc[AroundIndex]['Price']

            if df.loc[
                AroundIndex, 'IDorder'] == 'x0':  # ถถ้าช่อง ไอดีออเดอร์ยังว่าง แสดงว่าเป็นเงื่อนไขแรก ไม่มีการตั้งลิมิต

                if difValue3 < 0:  # ส่วนต่าง ถ้าขาด ให้เติมโดย ซื้อเข้า
                    df._set_value(AroundIndex, 'Side',
                                  "ซื้อ")  # ต้อง set ค่าเริ่มต้นในชีทให้เป็น สติง ก่อน ไม่นั้นมันจะคิดว่า ช่องว่างๆ คือ ค่า float error ValueError: could not convert string to float
                    orderrr = re(whatsymbol, 'buy', amount, price)  # ยิงออเดอร์
                    df = orderFilled(df, AroundIndex, orderrr, SubAsset,
                                     1)  # ส่งข้อมูล ไอดีออเดอร์และวันที่ # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

                if difValue3 > 0:  # ส่วนต่าง ถ้าเกิน ให้ ขายออก
                    df._set_value(AroundIndex, 'Side', "ขาย")
                    orderrr = re(whatsymbol, 'sell', amount, price)  # ยิงออเดอร์
                    df = orderFilled(df, AroundIndex, orderrr, SubAsset,
                                     1)  # ส่งข้อมูล ไอดีออเดอร์และวันที่ และ # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

        else:  # ยังไม่เข้าเงื่อนไข รอไปก่อน
            df._set_value(AroundIndex, 'Stat', 'Wait')  # 'Stat ' กับ 'Stat' ถ้ามีช่องว่าง คือไม่ใช่คำเดียวกัน
            # df.loc[AroundIndex, 'Stat'] = 'Wait' # แบบนี้จะสร้าง colum ใหม่

    return df


def get_balance(get_asset,typee):
    params = {
        'recvWindow': 50000
    }
    balance = exchange.fetch_balance(params)
    # df_balance = pd.DataFrame.from_dict(balance['info']['balances'])
    # df_balance['asset'] = df_balance.asset.astype(str)
    # return df_balance.loc[df_balance.asset =='XRP'] // แสดงจำนวนของ XRP

    if typee == 1: #เรียกดู จำนวน เหรียญชนิดนั้นๆ เหมือนคำสั่ง exchange.fetch_ticker
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
    r1 = json.dumps(exchange.fetch_ticker(pair))
    dataPrice = json.loads(r1)
    sendBack = float(dataPrice['last'])
    return sendBack

def re(symbol,side,amount,price):
    #symbol = 'XRP/BNB'
    type = 'limit'  # 'limit' or 'market'
    #side = 'sell'  # or 'buy'
    #amount = 11.0
    #price = 0.0120  # or None #

    # extra params and overrides if needed
    params = {
        'test': True,  # ทดสอบโดยไม่ต้องเปิดออเดอร์จริงๆ สำหรับ Binance
        'recvWindow': 10000
    }
    order = exchange.create_order(symbol, type, side, amount, price, params) #Limit
    #order = exchange.create_order(symbol, type, side, amount, params)  # Market
    return order


def orderFilled(df,Around,orderrr,SubAsset,typee):

    if typee == 2: #เช็คดว่า แมต ยังหรือยัง # ต้นทางเช็คมาแล้วว่า ID ไม่ว่าง แสดงว่ามีการตั้ง Pending ออเดอร์
        id = df.loc[Around]['IDorder']
        checkTime = df.loc[Around]['Date']
        orderMatched = checkByIDoder(id)

        if orderMatched['filled'] > 0:  # เช็ค Matched ไหม # ถ้ามากกว่า 0 แสดงว่า ลิมิตออเดอร์ แมต แล้ว..
            df._set_value(Around, 'AssetAdjust', get_balance(SubAsset, 1))

            Nav1 = df.loc[Around]['AssetAdjust']
            Nav2 = df.loc[Around]['Price']
            Nav3 = float(Nav1) * float(Nav2)
            df._set_value(Around, 'ValueAdjust', Nav3)
            df._set_value(Around, 'Filled', orderMatched['filled'])

            df._set_value(Around, 'BalanceAdjust', get_balance(MainAsset, 1))

            df = newrow_index(df, Around) #ขึนรอบใหม่ บรรทัดใหม่
            LineNotify(df, Around, SubAsset, 'change')
        else:
            # ผ่านไป 3 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
            first_time = df.loc[Around]['Timer']
            start_time = first_time + 600 #นับถอยหลัง 10 นาที เพื่อยกเลิกออเดอร์
            target_time = time.time()
            timeElapsed = target_time - start_time
            if timeElapsed > 0 :
                cancelOrder(df,Around,id)

    if typee == 1: # บันทึก ไอดีออเดอร์ และวันที่ ตั้งลิมิต
        df._set_value(Around, 'IDorder', orderrr['id'])
        df._set_value(Around, 'Date', orderrr['datetime'])
        df._set_value(Around, 'Timer', time.time())

    return df

def checkByIDoder(id):
    oderinfo = exchange.fetch_order(id)
    return oderinfo

def cancelOrder(df,Around,id):
    exchange.cancel_order(id)
    # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
    df._set_value(Around, 'IDorder', 'x0')
    df._set_value(Around, 'Amount', '')
    df._set_value(Around, 'Date', '')
    df._set_value(Around, 'Timer', '')


def newrow_index(df,Around):
    Around = Around+1
    # Adding the row
    df1 = df[~df.index.isna()].append(pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns, index=[Around]))
    df = df1.append(df[df.index.isna()])
    df = df.rename_axis("indexAround")
    df._set_value(Around,'IDorder','x0')
    df._set_value('Around', 'Balance', Around)
    return df

def LineNotify(df,Around,subasset,typee) :
    # แจ้งเตือนผ่านไลน์เมื ่่อเกิดการรีบาลานซ์
    # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549

    url = 'https://notify-api.line.me/api/notify'
    token = 'MQaK3NTRG0gtC4PS2pQYiJvKC44J4prFY3hAcgzZ8EE'
    headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

    if typee == 'change':
        BalanceNotify = df.loc[Around]['BalanceAdjust']
        ValueNotify = df.loc[Around]['ValueAdjust']
        AsseteNotify = df.loc[Around]['AssetAdjust']

        msg = '\nขึ้นรอบใหม่แล้ว ' +str(Around)+ '\nจำนวนเงินในพอร์ตเหลือ =' + str(BalanceNotify)+'USDT \n' + 'มูลค่า =' + str(ValueNotify) +'USDT \n' + 'ปริมาณสินค้า =' + str(AsseteNotify)+' '+str(subasset)
    if typee == 'error' :
        msg = '\nแจ้งคนเขียน\n'+str(subasset)
    r = requests.post(url, headers=headers, data={'message': msg})
    print(r.text)

