import ccxt
import json
import pandas as pd
import numpy as np

###########  ตั้งค่า API -------------------------------------------------------------------
whatbroker ='kucoin'
whatsymbol = 'BNB/USDT'
MainAsset = 'USDT'
SubAsset = 'BNB'

if whatbroker == "binance":
    result = 'balances'
    listAsset = 'asset'
    exchange = ccxt.binance({
        'apiKey': '**********************',
        'secret': '************************',
        'enableRateLimit': True,
    })

if whatbroker == "kucoin":
    result = 'data'
    listAsset = 'currency'
    typeaccount = 'type'
    exchange = ccxt.kucoin({
        'apiKey': '****************',
        'secret': '****************',
        'password': '************',
        'enableRateLimit': True,
    })

if whatbroker == "ftx":
    result = 'result'
    listAsset = 'coin'
    subaccount = 'ForTest'  # ถ้ามี ซับแอคเคอร์ของ FTX
    exchange = ccxt.ftx({
        'apiKey': '**********************',
        'secret': '************************t',
        'enableRateLimit': True,
    })
    if subaccount == "":
        print("This is Main Account")
    else:
        exchange.headers = {
            'FTX-SUBACCOUNT': subaccount,
        }

########### -------------------------------------------------------------

def updatee(df,AroundIndex):
    #ตัวกำหนด ว่าจะให้ รีบาลานซ ที่มูลค่าเท่าไร และกี่ % โดยอ้างอิงตัวเลขใน google sheet
    Value = df.loc['Around']['Value']
    condition_ = df.loc['Around']['Condition']

    a = int(AroundIndex) #แปลง index จากสติง เป็ร int เพราะ ไม่นั้นเด๊ว error

    df._set_value(AroundIndex, 'Value', Value)
    df._set_value(AroundIndex, 'Balance', get_balance(MainAsset,1))
    df._set_value(AroundIndex, 'Asset', get_balance(SubAsset,1))
    #df._set_value(AroundIndex, 'Asset', 50000)  #จำลอง สินค้า
    df._set_value(AroundIndex, 'Price', getPrice(whatsymbol))
    df._set_value(AroundIndex, 'Condition', condition_)

    Nav1 = df.loc[a]['Asset']
    Nav2 = df.loc[a]['Price']
    Nav3 = float(Nav1) * float(Nav2)
    df._set_value(AroundIndex, 'NAV', Nav3)

    difValue1 = df.loc[a]['Value']
    difValue2 = df.loc[a]['NAV']
    difValue3 = float(difValue2) - float(difValue1)

    df._set_value(AroundIndex, 'Dif', difValue3)
    dif = abs(df.loc[a]['Dif'])

    #ฟังก์ชั่นเช็ค ทุกๆ x% ทุกๆ 1 นาที

    conditionToAdjust = whatFunction(df,a,'percent')

    if conditionToAdjust < dif :     #ถ้าส่วนต่าง (dif) มากกว่า เงื่อนไข%(conditionToAdjust) ที่ตั้งไว้ บอกสถานะว่า ได้เข้าเงื่อนไขรีบาลานซ์
        Stat  = 'Action'
        df.loc[AroundIndex, 'Stat'] = Stat
        _Amount1 = abs(difValue3)
        _Amount2 = _Amount1 / Nav2
        df._set_value(AroundIndex, 'Amount', _Amount2)
        amount = df.loc[a]['Amount']
        price = df.loc[a]['Price']

        # ส่วนต่าง ถ้าขาด ให้เติมโดย ซื้อเข้า
        if difValue3 < 0:
            df._set_value(a, 'Side', "BUY")
            orderrr = re(whatsymbol, 'buy', amount, price)  #ยิงออเดอร์
            orderFilled(df,AroundIndex,orderrr) #ส่งข้อมูล ไอดีออเดอร์และวันที่
            df = newrow_index(df, AroundIndex)  # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ
            #if orderFilled != '': #ถ้าเปิดออเดอร์สำเร็จแล้ว สำเร็จ ลิมิต

        # ส่วนต่าง ถ้าเกิน ให้ ขายออก
        if difValue3 > 0:
            df._set_value(a, 'Side', "SELL")  # ทำไม ใส่ AroundIndex แล้ว error ValueError: could not convert string to float หว่าาา
            orderrr = re(whatsymbol, 'sell', amount, price)  #ยิงออเดอร์
            orderFilled(df,AroundIndex,orderrr)  # ส่งข้อมูล ไอดีออเดอร์และวันที่
            df = newrow_index(df, AroundIndex)  # ถ้ายิงออเดอร์ และแมตซ์ ให้ขึ้นบรรทัดใหม่และ +1 รอบ

    else:  #ยังไม่เข้าเงื่อนไข รอไปก่อน
        df._set_value(a, 'Stat', 'Wait') # 'Stat ' กับ 'Stat' ถ้ามีช่องว่าง คือไม่ใช่คำเดียวกัน
        #df.loc[AroundIndex, 'Stat'] = 'Wait' # แบบนี้จะสร้าง colum ใหม่
    return df

def newrow_index(df,AroundIndex):
    AroundIndex = AroundIndex+1
    # Adding the row
    df1 = df[~df.index.isna()].append(pd.DataFrame([[np.nan] * len(df.columns)], columns=df.columns, index=[AroundIndex]))
    df = df1.append(df[df.index.isna()])
    df = df.rename_axis("indexAround")

    df._set_value('Around', 'Balance', AroundIndex)
    return df


def get_balance(get_asset,typee):
    params = {
        'recvWindow': 50000
    }
    balance = exchange.fetch_balance(params)
    # df_balance['asset'] = df_balance.asset.astype(str)
    # return df_balance.loc[(df_balance.asset =='XRP') & (df_balance.free > 0)]

    if typee == 1: #เรียกดู จำนวน เหรียญชนิดนั้นๆ เหมือนคำสั่ง exchange.fetch_ticker
        if whatbroker == "kucoin":
             df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index([listAsset,typeaccount])
             #df_balance['balance'] = df_balance.balance.astype(float)
             return df_balance.loc[get_asset,'trade']['balance']
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
    type = 'market'  # 'limit' or 'market'
    #side = 'sell'  # or 'buy'
    #amount = 11.0
    #price = 0.0120  # or None #

    # extra params and overrides if needed
    params = {
        'test': True,  # ทดสอบโดยไม่ต้องเปิดออเดอร์จริงๆ สำหรับ Binance
        'recvWindow': 10000
    }
    #order = exchange.create_order(symbol, type, side, amount, price, params) #Limit
    order = exchange.create_order(symbol, type, side, amount, params)  # Market
    return order

def whatFunction(df,Around,whatfution):
    if whatfution == 'percent':
        conditionToAdjust1 = df.loc[Around]['Value']
        conditionToAdjust2 = df.loc[Around]['Condition'] # ดึงเลข 2 ในชีทมา
        conditionToAdjust3 = (conditionToAdjust1 / 100) * conditionToAdjust2 # ตรวจดูว่า เกิน 2%ยัง
        return  conditionToAdjust3

    #if whatfution ==2:

def orderFilled(df,Around,orderrr):

    df._set_value(Around, 'IDorder', orderrr['id'])
    df._set_value(Around, 'Date',  orderrr['datetime'])
    df._set_value(Around, 'AssetAdjust', get_balance(SubAsset,1))

    Nav1 = df.loc[Around]['AssetAdjust']
    Nav2 = df.loc[Around]['Price']
    Nav3 = float(Nav1) * float(Nav2)
    df._set_value(Around, 'ValueAdjust', Nav3)

    df._set_value(Around, 'BalanceAdjust', get_balance(MainAsset,1))

    #df._set_value(Around, 'Filled', orderrr['filled'])
    #return df.loc[Around]['filled']

