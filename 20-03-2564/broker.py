import ccxt
import pandas as pd
import numpy as np
import hashlib
import hmac
import json
import requests
import datetime
#import division as di
'''
คำสั่งพื้นฐาน
1.เปิดออเดอร์  สำหรับ ftx
1.2 ซื้อ สำหรับ bitkub
1.3 ขาย สำหรับ bitkub
2.ยกเลิกออเดอร์
3.เข้าถึงออเดอร์ที่ยังไม่ Filled ด้วยไอดี
4.ดูปริมาณสินทรัพย์ในพอร์ต
5.ดูค่าธรรมเนียม
6.ดูราคา
'''

"""logging.basicConfig(filename='brokerLog',
                        filemode='w',
                        format='%(levelname)s %(asctime)s - %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

logger = logging.getLogger()"""

class broker :
    def __init__(self=None, api_key=None, api_secret=None , subaccount=None,what_symbol=None,what_broker=None,ST=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.subaccount = subaccount
        self.what_broker = what_broker
        self.what_symbol = what_symbol
        self.ST = ST
        # FTX
        if self.what_broker == 'FTX':
            self.ftxObject = FTX(self.api_key,self.api_secret,self.subaccount,self.what_symbol)
        # BITKUB
        if self.what_broker == 'BITKUB':
            self.bitkubObject = BITKUB(self.api_key,self.api_secret,self.what_symbol)

    def open_close(self, types, side, amount, nowprice=None):

        if self.what_broker == 'FTX':
            order_info_FTX = self.ftxObject.OpenClose(types, side, amount, nowprice)

            if self.ST == 'Futures':
                df_order_info_FTX_Futures = pd.DataFrame.from_dict(order_info_FTX)
                order_info_FTX_Futures_dict = {
                    "id": df_order_info_FTX_Futures.loc['id']['info'],
                    "price": df_order_info_FTX_Futures.loc['price']['info'],
                    "amount": df_order_info_FTX_Futures.loc['amount']['info'],
                    'timestamp': datetime.datetime.timestamp(datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f'))

                }
                return order_info_FTX_Futures_dict
            if self.ST == 'Spot':
                df_order_info_FTX = pd.DataFrame.from_dict(order_info_FTX)
                order_info_FTX_dict = {
                    "id": df_order_info_FTX.loc['id']['info'],
                    "price": df_order_info_FTX.loc['price']['info'],
                    "amount": df_order_info_FTX.loc['size']['info'],
                    'timestamp': datetime.datetime.timestamp(datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f'))
                }

                return order_info_FTX_dict


        if self.what_broker == 'BITKUB':
            if side == 'buy':
                self.order_info_Bitkub = self.bitkubObject.createbuy(amount, nowprice, types)
            if side == 'sell':
                self.order_info_Bitkub = self.bitkubObject.createsell(amount, nowprice, types)

            self.df_order_info_Bitkub = pd.DataFrame.from_dict(self.order_info_Bitkub)
            self.order_info_Bitkub_dict = {
                "id": self.df_order_info_Bitkub.loc['id']["result"],
                "price": self.df_order_info_Bitkub.loc['rat']["result"],
                "amount": self.df_order_info_Bitkub.loc['amt']["result"],
                'timestamp': datetime.datetime.timestamp(datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f'))
            }
            return self.order_info_Bitkub_dict

    def get_price(self):
        if self.what_broker == 'FTX':
            self.price = self.ftxObject.getPrice()
        if self.what_broker == 'BITKUB':
            self.price = self.bitkubObject.getprice()
        return self.price


    def cancel_order(self,id_order,side):
        if self.what_broker == 'FTX':
            self.ftxObject.cancelOrder(id_order)
        if self.what_broker == 'BITKUB':
            self.bitkubObject.cancelOrder(id_order,side)

    # เก็บรวบรวมข้อมูลแล้วแพคกลับไป ป้องกันกรณี load server มากเกิน
    def get_info_order_byID(self,id_order,side):
        if self.what_broker == 'FTX':
            self.info_order_ftx = self.ftxObject.checkByIDoder(id_order)
            self.df_info_order_ftx = pd.DataFrame.from_dict(self.info_order_ftx)
            #print(self.df_info_order_ftx )

            if self.ST == 'Futures':
                self.info_order_ftx_dict = {
                    "amount": self.df_info_order_ftx.loc['amount']['info'],
                    "filled": self.df_info_order_ftx.loc['filled']['info'],
                    "price": self.df_info_order_ftx.loc['price']['info'],
                    'side': self.df_info_order_ftx.loc['side']['info'],
                    'fee': self.ftxObject.Getfee_ByIDoderinMyTrades(id_order, side)  # fee
                }
                return self.info_order_ftx_dict
            if self.ST == 'Spot':
                self.info_order_ftx_dict = {
                    "amount": self.df_info_order_ftx.loc['size']['info'],
                    "filled": self.df_info_order_ftx.loc['filledSize']['info'],
                    "price": self.df_info_order_ftx.loc['price']['info'],
                    'side': self.df_info_order_ftx.loc['side']['info'],
                    'fee': self.ftxObject.Getfee_ByIDoderinMyTrades(id_order, side)  # fee
                }
                return self.info_order_ftx_dict

        if self.what_broker == 'BITKUB':
            self.info_order_bitkub = self.bitkubObject.orderinfo(id_order,side)
            if self.info_order_bitkub != 'this_order_cancelled':
                #print(self.info_order_bitkub)
                try:
                    self.df_info_order_bitkub = pd.DataFrame.from_dict(self.info_order_bitkub)
                    #print(self.df_info_order_bitkub)
                    self.info_order_bitkub_dict = {
                        "amount": self.df_info_order_bitkub .loc['amount']["result"],
                        "filled": self.df_info_order_bitkub .loc['filled']["result"],
                        "price": self.df_info_order_bitkub .loc['rate']["result"],
                        'side': self.df_info_order_bitkub .loc['side']["result"],
                        'fee': self.df_info_order_bitkub.loc['fee']["result"]
                    }
                    #  'timestamp': datetime.datetime.timestamp(datetime.datetime.strptime(str(datetime.datetime.now()), '%Y-%m-%d %H:%M:%S.%f'))
                    #datetime.datetime.now()
                    return self.info_order_bitkub_dict

                except Exception as e:
                    print("ID : " + str(id_order) + " Cancelled order so don't worry if Get Error : " + str(e))
                    pass
                '''
                if typee_get == 'filled':
                    try:
                        self.filled_bitkub = pd.DataFrame.from_dict(self.info_order_bitkub)
                        self.filled_bitkub = self.filled_bitkub.loc['filled']["result"]
                        print(self.filled_bitkub)
                    except Exception as e:
                        print("ID : " + str(id_order) + " Cancelled order so don't worry if Get Error : " + str(e))
                        pass
            '''
    def call_bbands(self,timeframe,Period):
        if self.what_broker == 'FTX':
            data = self.ftxObject.bbands(timeframe,Period)
            return data



    def get_my_open_orders(self):
        if self.what_broker == 'BITKUB':
            my_open_orders = self.bitkubObject.my_open_orders()
            return my_open_orders

        if self.what_broker == 'FTX':
            my_open_orders_FTX = self.ftxObject.get_oepntrde()
            #print(my_open_orders_FTX)
            info_my_open_orders_FTX = pd.DataFrame(my_open_orders_FTX,columns=['id', 'symbol', 'side', 'price', 'amount'])
            #print(info_my_open_orders_FTX)
            if info_my_open_orders_FTX.empty:
                info_my_open_orders_FTX2 = pd.DataFrame({"id": np.arange(1, 2, 1), "symbol": 'empty', "side": np.nan,'price': np.nan,'amount': np.nan})
                return info_my_open_orders_FTX2
            else:
                my_trades = self.ftxObject.get_positions()
                #print("\n=============my_trades=============")
                my_trades = pd.json_normalize(data=my_trades['result'])
                #print(my_trades)
                if self.ST == 'Futures':
                    df_curr_trade = pd.DataFrame(my_trades,
                                                 columns=['future', 'side', 'entryPrice', 'estimatedLiquidationPrice',
                                                          'size', 'cost',
                                                          'collateralUsed', 'unrealizedPnl', 'realizedPnl'])
                    info_my_open_orders_FTX = info_my_open_orders_FTX.append(df_curr_trade, ignore_index=True)
                    #print(df_curr_trade)
                '''if self.ST == 'Spot':
                    dfTradeLog4 = pd.DataFrame({'id': np.arange(1, 2, 1)
                                                   , 'symbol': di.sector.mainAsset+' Hold'
                                                   , 'side': self.ftxObject.get_Collateral(di.sector.mainAsset, 'free')
                                                   , 'price': di.sector.asset+' Hold'
                                                   , 'amount': self.ftxObject.get_Collateral(di.sector.asset, 'free')
                                                })
                    #print(dfTradeLog3)
                    info_my_open_orders_FTX = info_my_open_orders_FTX.append(dfTradeLog4, ignore_index=True)'''

                return info_my_open_orders_FTX




    def get_asset(self,whatasset,type):
        if self.what_broker == 'FTX':
            asset = self.ftxObject.get_Collateral(whatasset,type)
            return asset
        if self.what_broker == 'BITKUB':
            asset = self.bitkubObject.balances(whatasset,type)
            return asset


    def get_order_history(self):
        if self.what_broker == 'BITKUB':
            info_history = self.bitkubObject.order_history()
            return info_history
        if self.what_broker == 'FTX':
            info_history = self.ftxObject.get_mytrade()
            return info_history

# ดูปริมาณสินทรัพย์หลัก เช่น THB USD
    def get_value_asset(self):
        if self.what_broker == 'FTX':
            value_asset = self.get_asset('USD', 'total')
            return value_asset
        # BITKUB
        if self.what_broker == 'BITKUB':
            value_asset = self.get_asset('THB', 'total')
            return value_asset

class FTX() :
    def __init__(self, api_key, api_secret,subaccount,what_symbol):
        self.what_symbol = what_symbol
        self.api_key = api_key
        self.api_secret = api_secret
        self.subaccount = subaccount
        self.exchange = ccxt.ftx({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
        })
        if self.subaccount == "":
            print("This is Main Account")
        else:
            self.exchange.headers = {
                'FTX-SUBACCOUNT': self.subaccount,
            }

    # ดึงข้อมูลราคา เครดิต คุณ Sippavit Kittirattanadul
    def OHLC(self,timeframe,Period, *args):  # นำขั้นตอนการเรียกข้อมุล ohlc มารวมเป็น function เพื่อเรียกใช้งานได้เรื่อยๆ
        #print(timeframe)
        #print(Period)
        count = Period
        tf = timeframe # 5m 1h 1d
        if args is not None:
            count = count * 2

        try:  # try/except ใช้แก้ error : Connection aborted https://github.com/ccxt/ccxt/wiki/Manual#error-handling
            ohlc = self.exchange.fetch_ohlcv(self.what_symbol, timeframe=tf, limit=count)
            # print(ohlc)
        except ccxt.NetworkError as e:
            print(self.exchange.id, 'fetch_ohlcv failed due to a network error:', str(e))
            ohlc = self.exchange.fetch_ohlcv(self.what_symbol, timeframe=tf, limit=count)
            # retry or whatever

        except ccxt.ExchangeError as e:
            print(self.exchange.id, 'fetch_ohlcv failed due to exchange error:', str(e))
            ohlc = self.exchange.fetch_ohlcv(self.what_symbol, timeframe=tf, limit=count)
            # retry or whatever

        except Exception as e:
            print(self.exchange.id, 'fetch_ohlcv failed with:', str(e))
            ohlc = self.exchange.fetch_ohlcv(self.what_symbol, timeframe=tf, limit=count)
            # retry or whatever

        ohlc_df = pd.DataFrame(ohlc, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
        ohlc_df['datetime'] = pd.to_datetime(ohlc_df['datetime'], unit='ms')

        return ohlc_df

    def bbands(self, timeframe,Period):
        numsd = 2
        # Get price
        datainfo = self.OHLC(timeframe,Period)
        # Get just the  close
        close = datainfo['close']
        """ returns average, upper band, and lower band"""
        ave = close.rolling(window=Period, center=False).mean()
        #print(ave)
        sd = close.rolling(window=Period, center=False).std()
        upband = ave + (sd * numsd)
        dnband = ave - (sd * numsd)
        datainfo['ave'] = np.round(ave, 6)
        datainfo['upper'] = np.round(upband, 6)
        datainfo['lower'] = np.round(dnband, 6)

        lastinfo = datainfo.tail(1)
        for i, row in lastinfo.iterrows():
            value = {
                "ave": row['ave'],
                "upper": row['upper'],
                "lower": row['lower']
            }

        #sp = datainfo[-200:]
        #lastinfo.plot()
        return value

    def RSI(self,timeframe, Period):
        # ที่มา https://stackoverflow.com/questions/20526414/relative-strength-index-in-python-pandas
        # Window length for moving average
        window_length = Period

        # Get price
        datainfo = self.OHLC(timeframe, Period)

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

    def OpenClose(self, types, side, amount, nowprice):
        # types = 'limit'  # 'limit' or 'market'
        if types == 'limit' :
            order = self.exchange.create_order(self.what_symbol, types, side, amount, nowprice)
            return order
        elif types == 'market' :
            order = self.exchange.create_order(self.what_symbol, types, side, amount)
            #logger.info(order)
            # print(order)
            return order

    def get_positions(self):
        my_trades = self.exchange.private_get_positions()
        return my_trades

    def checkByIDoder(self,id):
        idStr = ('%f' % id).rstrip('0').rstrip('.')  # ลบ .0 หลัง หมายเลขไอดี
        oderinfo = self.exchange.fetch_order(idStr)
        #logger.info(oderinfo)
        #print(oderinfo)
        return oderinfo

    def Getfee_ByIDoderinMyTrades(self,id, side):
        idStr = ('%f' % id).rstrip('0').rstrip('.')  # ลบ .0 หลัง หมายเลขไอดี
        fetchTrades = self.exchange.fetch_my_trades(symbol=self.what_symbol, since=None, limit=2000, params={})

        fetchTrades = pd.json_normalize(data=fetchTrades)
        df_fetchTrades = pd.DataFrame(data=fetchTrades, columns=['order', 'info.side', 'info.fee'])
        for i, row in df_fetchTrades.iterrows():
            if row['order'] == idStr and row['info.side'] == side:
                return df_fetchTrades.at[i, 'info.fee']

    def get_mytrade(self):
        fetchTrades = self.exchange.fetch_my_trades(symbol=self.what_symbol, since=None, limit=2000, params={})
        return fetchTrades

    def get_oepntrde(self):
        print(self.what_symbol)
        fetchOpenTrades = self.exchange.fetch_open_orders(symbol=self.what_symbol, since=None, limit=2000, params={})
        return fetchOpenTrades

    def cancelOrder(self,id):
        orderMatched = self.checkByIDoder(id)
        #logger.info(orderMatched)
        #print(orderMatched)
        if orderMatched['status'] == 'closed' or orderMatched['status'] == 'canceled':  # ถ้ามัน closed ไปแล้ว แสดงว่าโดนปิดมือ
            print('mannual cancel')
        else:
            self.exchange.cancel_order(id)

    def get_Collateral(self,get_asset, typee):
        result = 'result'
        listAsset = 'coin'
        params = {'recvWindow': 50000}

        # typee = 'free' or 'total'

        balance = self.exchange.fetch_balance(params)
        df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
        df_balance['free'] = df_balance.free.astype(float)
        df_balance['total'] = df_balance.total.astype(float)
        free = df_balance.loc[get_asset]['free']
        total = df_balance.loc[get_asset]['total']
        reserved = total - free
        if typee == 'free':
            return free
        if typee == 'total':
            return total
        if typee == 'InOrder':
            return reserved

    def getPrice(self):
        pair = self.what_symbol
        r = json.dumps(self.exchange.fetch_ticker(pair))
        dataPrice = json.loads(r)
        sendBack = float(dataPrice['last'])
        return sendBack


# ตัวอย่างเบื้องต้น https://github.com/bitkub/bitkub-official-api-docs/blob/master/samples/python/sample_balances.py
# ที่มา https://github.com/paowongsakorn/bitkub/blob/master/bitkub.py
# คู่มือและรูปแบบคำสั่งอื่นๆ  https://github.com/bitkub/bitkub-official-api-docs/blob/master/restful-api.md#post-apimarketbalances
class BITKUB():
        def __init__(self,api_key,api_secret,what_symbol):
            self.what_symbol = what_symbol
            self.api_key = api_key
            self.api_secret = bytes(api_secret, encoding='utf-8')
            self.API_HOST = 'https://api.bitkub.com'
            self.header = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'X-BTK-APIKEY': self.api_key}

        def timeserver(self):
            response = requests.get(self.API_HOST + '/api/servertime')
            ts = int(response.text)
            print('Server time: ' + response.text)
            return ts

        def sign(self,data):
            j = self.json_encode(data)
            # print('Signing payload: ' + self.j)
            h = hmac.new(self.api_secret, msg=j.encode(), digestmod=hashlib.sha256)
            return h.hexdigest()

        def json_encode(self,datajson):
            return json.dumps(datajson, separators=(',', ':'), sort_keys=True)

        def addresses(self):
            address = {
            'ts': self.timeserver(),}

            signature = self.sign(address)
            address['sig'] = signature
            #print('Payload with signature: ' + json_encode(order_info))
            response = requests.post(self.API_HOST + '/api/crypto/addresses', headers=self.header, data=self.json_encode(address))
            x = response.json()
            #print(x)
            return x

        def getprice(self):
            rticker = requests.get(self.API_HOST + '/api/market/ticker')
            rticker = rticker.json()
            price = float(rticker[self.what_symbol]['last'])
            return price

        def my_open_orders(self):
            open_orders = {
            'sym': self.what_symbol,
            'ts': self.timeserver()}

            signature = self.sign(open_orders)
            open_orders['sig'] = signature
            r = requests.post(self.API_HOST + '/api/market/my-open-orders', headers=self.header, data=self.json_encode(open_orders))
            r = r.json()

            return r

        def orderinfo(self,orderid,side):

            order_info = {
            'sym': self.what_symbol,
            'id': orderid,
            'sd': side,
            'ts': self.timeserver(),}

            signature = self.sign(order_info)
            order_info['sig'] = signature
            #print('Payload with signature: ' + json_encode(order_info))
            response = requests.post(self.API_HOST + '/api/market/order-info', headers=self.header, data=self.json_encode(order_info))
            x = response.json()
            #print(x)
            if x['error'] == 24 :
                print('this order cancelled ')
                y = 'this_order_cancelled'
                return y
            return x

        def cancelOrder(self, orderid,side):

            order_info = {
            'sym': self.what_symbol,
            'id': orderid,
            'sd': side,
            'ts': self.timeserver(),}

            self.signature = self.sign(order_info)
            order_info['sig'] = self.signature
            #print('Payload with signature: ' + json_encode(order_info))
            response = requests.post(self.API_HOST + '/api/market/cancel-order', headers=self.header, data=self.json_encode(order_info))
            x = response.json()
            if x['error'] == 21 :
                print('This '+str(orderid)+' Cancelled by hand Get Invalid order for cancellation')
            elif x['error'] == 0 :
                print('ID order : ' + str(orderid) + ' canceled success')

        def wallets(self):
            address = {
            'ts': self.timeserver(),
            }

            signature = self.sign(address)
            address['sig'] = signature
            #print('Payload with signature: ' + json_encode(order_info))
            response = requests.post(self.API_HOST + '/api/market/wallet', headers=self.header, data=self.json_encode(address))
            x = response.json()
            #print(x)
            return x

        def balances(self,get_asset,typee):
            result = 'result'
            listAsset = 'coin'

            address = {
            'ts': self.timeserver(),
            }

            signature = self.sign(address)
            address['sig'] = signature
            #print('Payload with signature: ' + json_encode(order_info))
            response = requests.post(self.API_HOST + '/api/market/balances', headers=self.header, data=self.json_encode(address))
            x = response.json()
            print(x)
            df_balance = pd.DataFrame.from_dict(x[result])
            pd.set_option('display.width', 1000)
            pd.set_option('display.max_columns', 1000)
            #print(self.df_balance)
            #self.df_balance['available'] = self.df_balance.available.astype(float)
            #self.df_balance['reserved'] = self.df_balance.reserved.astype(float)
            free = df_balance.loc['available'][get_asset]
            reserved = df_balance.loc['reserved'][get_asset]
            toal = free + reserved

            if typee == 'free':
                return free
            if typee == 'total':
                return toal
            if typee == 'InOrder':
                return reserved

        def order_history(self):

            data = {
                'sym': self.what_symbol,
                'ts': self.timeserver(),
            }
            signature = self.sign(data)
            data['sig'] = signature

            #print('Payload with signature: ' + json_encode(data))
            r = requests.post(self.API_HOST + '/api/market/my-order-history', headers=self.header, data=self.json_encode(data))
            #print('Response: ' + self.r.text)
            return r.json()

        def createbuy(self,amount,rate,ordertype):

            data = {
            'sym': self.what_symbol, # ETH_THB
            'amt': amount, # THB amount you want to spend จำวนเงิน
            'rat': rate, # ราคา
            'typ': ordertype, # limit
            'ts': self.timeserver(),}

            signature = self.sign(data)
            data['sig'] = signature

            #print('Payload with signature: ' + json_encode(data))
            r = requests.post(self.API_HOST + '/api/market/place-bid', headers=self.header, data=self.json_encode(data))
            print('Response: ' + r.text)
            return r

        def createsell(self,amount,rate,ordertype):

            data = {
            'sym': self.what_symbol,
            'amt': amount, # THB amount you want to spend
            'rat': rate,
            'typ': ordertype,
            'ts': self.timeserver(),}

            signature = self.sign(data)
            data['sig'] = signature

            #print('Payload with signature: ' + json_encode(data))
            r = requests.post(self.API_HOST + '/api/market/place-ask', headers=self.header, data=self.json_encode(data))
            #print('Response: ' + r.text)
            x = r.json()
            return x
