import datetime
import requests
import pandas as pd
import gspread
import numpy as np
import broker as bk
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

class bot:
    # Google sheet
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
    gc = gspread.authorize(creds)
    sheetName = 'Data3'
    settingbot_df = None
    Monitor_df = None
    data_df = None
    tradelog_df = None
    FlowLog_df = None


    portObject = []
    index_name_scetor = ['A', 'B', 'C','D','E','F','G','H']

    def __init__(self, name):
        self.namePort = name
        self.tradeObject = []


    @staticmethod
    def create_sectorObject_list():

        # getting length of list
        length = len(bot.index_name_scetor)

        # Iterating the index
        # same as 'for i in range(len(list))'
        for i in range(length):
            print(bot.index_name_scetor[i])
            bot.portObject.append(bot(bot.index_name_scetor[i]))

    @staticmethod
    def LineNotify(mse, typee,token):
        # แจ้งเตือนผ่านไลน์เมื อเกิดการรีบาลานซ์
        # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549
        url = 'https://notify-api.line.me/api/notify'
        token = token
        headers = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}

        if typee == 'change':
            mse = str(mse)
            msg = mse
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)
        if typee == 'error':
            mse = str(mse)
            msg = '\nแจ้งคนเขียน\n' + mse
            r = requests.post(url, headers=headers, data={'message': msg})
            print(r.text)

    @staticmethod
    def runbot():
        bot.getset_GS('Get')
        length = len(bot.portObject)
        for i in range(length):
            if bot.portObject[i].namePort != 0 or bot.portObject[i].namePort != np.nan:
                bot.portObject[i].runPort()

    @staticmethod
    def checkmatch(tradeFX):

        x = datetime.datetime.now().strftime("%H:%M:%S")
        h, m, s = map(int, x.split(':'))
        sec = h * 3600 + m * 60 + s
        five_min = int(round(sec/300,2))

        print('เวลา : '+str(x))
        print('ลำดับ : '+str(five_min))

        df_checkmatch = pd.DataFrame(bot.data_df).set_index(tradeFX[4])
        check = five_min in df_checkmatch.index

        return check

    @staticmethod
    def inde(tradeFX):

        if tradeFX[6] == 'Bollinger_band':
            value = tradeFX[5].call_bbands(tradeFX[7], int(tradeFX[8]))
            # print(value)
            if tradeFX[5].get_price() > float(value['ave']):
                return True
            else:
                return False
        elif tradeFX[6] == 'Atr':
            value = tradeFX[5].call_atr(tradeFX[7], int(tradeFX[8]))
            fixvalue = tradeFX[2]

            price = tradeFX[5].get_price()
            ATR = value
            Volatility_per = (ATR / price) * 100  # atr เทียบกับราคาคิดเป็นกี่ %
            Volatility_Diff = (fixvalue * Volatility_per) / 100 # โว % เท่านั้นคิดเป็นปริมาณเท่าไร ในของทั้งหทด
            positionsize = tradeFX[5].get_asset(tradeFX[1], 'free')
            valueusd = round(price * positionsize, 1)
            buy_val_diff = fixvalue - Volatility_Diff
            sell_val_diff = fixvalue + Volatility_Diff
            print('art:'+str(ATR))
            print('value:'+str(valueusd))
            print(str(buy_val_diff))
            print(str(sell_val_diff))

            # print(value)
            if ATR > 0 and (valueusd <= buy_val_diff or valueusd >= sell_val_diff):
                return True
            else:
                return False
        elif tradeFX[6] == 'None':
            return True

    @staticmethod
    def getset_GS(typee):
        if typee == 'Get':
            bot.settingbot_df = get_as_dataframe(bot.gc.open(bot.sheetName).worksheet('Settingbot')).set_index('port')
            bot.Monitor_df = get_as_dataframe(bot.gc.open(bot.sheetName).worksheet('Monitor')).set_index('port')
            bot.data_df = get_as_dataframe(bot.gc.open(bot.sheetName).worksheet('data'))
            bot.tradelog_df = get_as_dataframe(bot.gc.open(bot.sheetName).worksheet('TradeLog'))
            bot.FlowLog_df = get_as_dataframe(bot.gc.open(bot.sheetName).worksheet('FlowLog'))

        if typee == 'Set':
            # บันทึกชีทหน้า Monitor
            dff_m = bot.Monitor_df.drop(columns=[c for c in bot.Monitor_df.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
            set_with_dataframe(bot.gc.open(bot.sheetName).worksheet('Monitor'), dff_m.reset_index())
            # บันทึกชีทหน้า tradelog
            dff_t = bot.tradelog_df.drop(columns=[c for c in bot.Monitor_df.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
            set_with_dataframe(bot.gc.open(bot.sheetName).worksheet('TradeLog'), dff_t)
            # บันทึกชีทหน้า FlowLog
            dff_f = bot.FlowLog_df.drop(columns=[c for c in bot.FlowLog_df.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
            set_with_dataframe(bot.gc.open(bot.sheetName).worksheet('FlowLog'), dff_f)


    def setup_api(self):
        self.tradeObject = []
        self.nameExchange = bot.settingbot_df.loc[self.namePort]['nameExchange']
        self.apiKey = bot.settingbot_df.loc[self.namePort]['API_Key']
        self.secret = bot.settingbot_df.loc[self.namePort]['secret_Key']
        self.subaccount = bot.settingbot_df.loc[self.namePort]['subaccount']
        self.lineAPI = bot.settingbot_df.loc[self.namePort]['Line_API']
        self.mode = bot.settingbot_df.loc[self.namePort]['Mode']
        self.mainAsset = bot.settingbot_df.loc[self.namePort]['mainAsset']
        self.TradeFuntion = bot.settingbot_df.loc[self.namePort]['TradeFuntion']
        self.timeframe = bot.settingbot_df.loc[self.namePort]['timeframe']
        self.period = bot.settingbot_df.loc[self.namePort]['period']

        self.symbol_A = bot.settingbot_df.loc[self.namePort]['symbol_A']
        self.asset_A = bot.settingbot_df.loc[self.namePort]['asset_A']
        self.fixvalue_A = bot.settingbot_df.loc[self.namePort]['fixvalue_A']
        self.typeTrade_A = bot.settingbot_df.loc[self.namePort]['typeTrade_A']
        self.tradeFX_A = bot.settingbot_df.loc[self.namePort]['tradeFX_A']
        self.exchangeObject_A = bk.broker(self.apiKey, self.secret, self.subaccount, self.symbol_A, self.nameExchange,self.typeTrade_A)
        self.tradeObject_A = [self.symbol_A, self.asset_A, self.fixvalue_A, self.typeTrade_A, self.tradeFX_A,self.exchangeObject_A,self.TradeFuntion,self.timeframe,self.period,'a']
        self.tradeObject.append(self.tradeObject_A)

        self.symbol_B = bot.settingbot_df.loc[self.namePort]['symbol_B']
        self.asset_B = bot.settingbot_df.loc[self.namePort]['asset_B']
        self.fixvalue_B = bot.settingbot_df.loc[self.namePort]['fixvalue_B']
        self.typeTrade_B = bot.settingbot_df.loc[self.namePort]['typeTrade_B']
        self.tradeFX_B = bot.settingbot_df.loc[self.namePort]['tradeFX_B']
        self.exchangeObject_B = bk.broker(self.apiKey, self.secret, self.subaccount, self.symbol_B, self.nameExchange,self.typeTrade_B)
        self.tradeObject_B = [self.symbol_B, self.asset_B, self.fixvalue_B, self.typeTrade_B, self.tradeFX_B,self.exchangeObject_B,self.TradeFuntion,self.timeframe,self.period,'b']
        self.tradeObject.append(self.tradeObject_B)

        self.symbol_C = bot.settingbot_df.loc[self.namePort]['symbol_C']
        self.asset_C = bot.settingbot_df.loc[self.namePort]['asset_C']
        self.fixvalue_C = bot.settingbot_df.loc[self.namePort]['fixvalue_C']
        self.typeTrade_C = bot.settingbot_df.loc[self.namePort]['typeTrade_C']
        self.tradeFX_C = bot.settingbot_df.loc[self.namePort]['tradeFX_C']
        self.exchangeObject_C = bk.broker(self.apiKey, self.secret, self.subaccount, self.symbol_C, self.nameExchange,self.typeTrade_C)
        self.tradeObject_C = [self.symbol_C,self.asset_C,self.fixvalue_C,self.typeTrade_C,self.tradeFX_C,self.exchangeObject_C,self.TradeFuntion,self.timeframe,self.period,'c']
        self.tradeObject.append(self.tradeObject_C)


    def runPort(self):
        #try:
        if bot.Monitor_df.loc[self.namePort]['mode'] != 'error' and bot.settingbot_df.loc[self.namePort]['Mode'] == 'Play':
            self.setup_api()
            # พอร์ต 1,2,3
            length = len(self.tradeObject)
            for i in range(length):
                # ตัวที่จะเทรดไม่ error
                if str(self.tradeObject[i][0]) != 'nan' :
                        print(str(self.tradeObject[i][0]))
                        # เงื่อนไขการเทรด
                        match = bot.checkmatch(self.tradeObject[i])
                        if match:
                                # เทรดได้
                                self.rebalance(self.tradeObject[i])

                elif bot.Monitor_df.loc[self.namePort]['mode'] == 'error':
                    if self.mode == 'Reset':
                        bot.Monitor_df.loc[self.namePort, 'mode'] = 'stop'
            mainAsset = self.exchangeObject_A.get_asset(self.mainAsset,'free')
            print('ทุนเหลือ : ' +str(mainAsset)+str(self.mainAsset))
            bot.Monitor_df.loc[self.namePort, 'stat'] = 'Run'
            bot.Monitor_df.loc[self.namePort, 'capital'] = mainAsset

        '''except Exception as e:
                if str(e) == 'ftx {"success":false,"error":"Not enough balances"}':
                    bot.Monitor_df.loc[self.namePort, 'stat'] = 'ตังไม่พอ'
                    bot.Monitor_df.loc[self.namePort, 'mode'] = 'error'
                    pass
                else:
                    print('stop this port')
                    print(e)
                    print(type(e).__name__, str(e))
                    print('-------ERROR inside--------------')
                    pass'''


        bot.getset_GS('Set')


    # rebalance
    def rebalance(self,tradeobject):

        min_percen_to_re = 1
        pointt = 1
        accu_sell_USD = 0
        accu_sell_Asset = 0
        accu_buy_USD = 0
        accu_buy_Asset = 0

        fixvalue = tradeobject[2]
        closeprice = tradeobject[5].get_price()
        positionsize = tradeobject[5].get_asset(tradeobject[1],'free')
        valueusd = round(closeprice * positionsize, 1)
        usdDiff = round(valueusd - fixvalue, 1) # ส่วนต่าง มูลค่า ที่ขาดๆเกินๆ
        perDiff = round(100 * usdDiff / fixvalue, 2) # ส่วนต่าง % ของ มูลค่า ที่ขาดๆเกินๆ
        print('ปริมาณ : '+str(positionsize)+str(tradeobject[1]))
        print('ส่วนต่างมูลค่า : '+str(perDiff)+ '%')

        check = bot.inde(tradeobject)

        if check:
            if perDiff > min_percen_to_re :

                sell_USD = abs(usdDiff) #จะขายออก มูลค่าเท่าไร
                amountSell = float(abs(sell_USD)) / float(closeprice)
                orderSell = tradeobject[5].open_close('market', 'sell', amountSell, 0)

                bot.LineNotify('\n' + 'ราคาขาย : ' + str(closeprice) + '\n' + 'มูลค่า : ' + str(sell_USD) + ' usd', 'change',self.lineAPI)

                print(orderSell)

                accu_sell_USD = round(sell_USD + accu_sell_USD, 1) # มูลค่าที่ขาย สะสม
                accu_sell_Asset = round(round(usdDiff / closeprice, pointt) + accu_sell_Asset, pointt) # usdDiff / closeprice ปริมาณของที่ขาย และ accu_sell_XRP คือปริมาณของที่ขายสะสม

            elif perDiff < -1 * min_percen_to_re :

                buy_USD = abs(usdDiff) # จะซื้อเข้าเท่าไร
                amountBuy = float(abs(buy_USD)) / float(closeprice)
                orderBuy = tradeobject[5].open_close('market', 'buy', amountBuy, 0)

                print(orderBuy)

                accu_buy_USD = round(buy_USD + accu_buy_USD, 1)
                accu_buy_XRP = round(round(usdDiff / closeprice, pointt) + accu_buy_Asset, pointt)


        bot.Monitor_df.loc[self.namePort, 'price_'+str(tradeobject[9])] = closeprice
        bot.Monitor_df.loc[self.namePort, 'size_' + str(tradeobject[9])] = positionsize
        bot.Monitor_df.loc[self.namePort, 'value_' + str(tradeobject[9])] = valueusd


        '''pos = round(fixvalue / closeprice, pointt)  # มีเงินเท่านี้ และราคา เท่านี้ จะต้องมีของปริมาณเท่าไร
        avg_buy_price = round(accu_buy_USD / accu_buy_Asset, 4)
        avg_sell_price = round(accu_sell_USD / accu_sell_Asset, 4)
        match_XRP_amt = min(-accu_buy_Asset, accu_sell_Asset)
        Cash_gen = (avg_sell_price - avg_buy_price) * match_XRP_amt
        print('Cash Gen:', round(Cash_gen, 1))  # , 'n tran',itran )
        return Cash_gen'''

