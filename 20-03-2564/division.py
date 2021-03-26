""" อธิบาย
คำนวณ อัตราส่วน exposure ต่อ พื้นที่
เช่น
class deck{
    MainZone 0.75
    MainExposre 1800 usd
    Ratio = 100
    DiffOfMainZone = 0.75/100 = 0.0075
    ExposurePerDiff = 1800/100 = 18

    MaxSupZone = 0.6
    MinSupZone = 0.5
    RangSupZone = 0.6 - 0.5 > 0.1
    DiffExposureSupZone = 0.1/0.0075 >  0.1 คือ 13 % ของพื้นที่ 0.75
    ExposureSupZone = ExposurePerDiff * DiffExposureSupZone ( 18*13) > 234 usd คือ 13% ของ 1800 usd
    DiffOfSupZone = 0.01
    UnitsInSupZone = RangSupZone / DiffOfSupZone ( 0.1 / 0.01) > 10 คือ กระสุน 10 นัด ระยะห่าง 0.01
    ExposurePerUnit = ExposureSupZone / UnitsSupZone (234 / 10) > 23.4 คือ กระสุน 10 นัด จะใช้ ต้นทุนนัดล่ะ 23.4 usd
}
"""
import requests
import pandas as pd
import numpy as np
import time
import datetime
import GoogleSheet as gs

'''logging.basicConfig(filename='divisionLog',
                        filemode='w',
                        format='%(levelname)s %(asctime)s - %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)

logger = logging.getLogger()'''

# index_name_scetor = ['A','B','C','D','E']

'''
MainZone 0.75
MainExposre 1800 usd
Ratio = 100
ExposurePerDiff = 1800/100 = 18
DiffOfMainZone = 0.75/100 = 0.0075  diff ขั้นต่ำของ MainZone

# โซนหลัก เช่น ราคา 100 บาท นับลงไปถึง 0
self.MainZone = MainZone
# ทุนทั้งหมด
self.MainExposure = MainExposure
# สัดส่วนที่จะเอามาแบ่ง
self.Ratio = 100
# ระยะระหว่าง Gap (หาพื้นที่ โดยการแบ่งสัดส่วน)
self.ExposurePerDiff = self.MainExposure / self.Ratio
# หาต้นทุนต่อพื้นที่
self.DiffOfMainZone = self.MainZone / self.Ratio
'''

'''
def flowlog(self):
    df.at[whatsymbol, 'TotalCollateral'] = get_Collateral(Balance, 'total')
    df.at[whatsymbol, 'FreeCollateral'] = get_Collateral(Balance, 'free')
    if pd.isna(df.loc[whatsymbol]['EntryPrice']):
        df.at[whatsymbol, 'EntryPrice'] = NowPrice
    # อัพเดท ความเคลื่อนไหวของพอร์ต ทุกๆ 4 ชั่วโมง
    if pd.isna(df.loc[whatsymbol]['TimeToUpdateFlowLog']):
        df.at[whatsymbol, 'TimeToUpdateFlowLog'] = time.time()
    start_time = df.loc[whatsymbol]['TimeToUpdateFlowLog']
    target_time = start_time + 14400  # 14400 วินาที คือ 4 ชั่วโมง
    nowtime = time.time()
    timeElapsed = nowtime - target_time
    if timeElapsed > 0:
        UpdateFlow(NowPrice)
        df.at[whatsymbol, 'TimeToUpdateFlowLog'] = time.time()
 '''

class sector:

    # staticVariable
    # https://www.tutorialspoint.com/class-or-static-variables-in-python

    NowPrice = None
    # ออบเจ็ต sector
    sectorObject = []

    # https://stackoverflow.com/questions/21598872/how-to-create-multiple-class-objects-with-a-loop-in-python

    runbot = None
    EditMode = None

    exchangeObject = None
    index_name_scetor = ['A', 'B', 'C', 'D', 'E']


    # ฟังก์ชั่นสร้างโซนเทรดจะไม่เกี่ยวข้องกับ ฟังก์ชั่นภายใน ที่ทำงานอยู่ในฟังก์ชั่นหลักชื่อ run แต่เป็นฟังก์ชั่นแยก เรียกใช้เฉพาะ ที่ต้องเรียกใช้จากภายนอก
    def __init__(self,indexsector):

        # ชื่อที่อยู่อ้างอิง ตัวตั้งค่าออบเจ็ต
        self.indexsector = indexsector
        self.dfInventory = None


    # Call from outside --------------------------------------
    @staticmethod
    def create_sectorObject_list():

        # getting length of list
        length = len(sector.index_name_scetor)

        # Iterating the index
        # same as 'for i in range(len(list))'
        for i in range(length):
            print(sector.index_name_scetor[i])
            sector.sectorObject.append(sector(sector.index_name_scetor[i]))

    @staticmethod
    def runDeck():

        gs.sheet.Command_frontEnd('Settingbot','Setup_api')
        gs.sheet.getsave_to_sheet('Monitor','Get')
        gs.sheet.getsave_to_sheet('TradeLog','Get')
        gs.sheet.getsave_to_sheet('FlowLog','Get')


        #set_with_dataframe(sector.gc.open(sector.sheetName).worksheet('Openorder'),sector.exchangeObject.get_my_open_orders())

        if gs.sheet.Settingbot_df.empty != True and sector.sectorObject != None:

            if sector.runbot == 'PlayMode':

                sector.NowPrice = sector.exchangeObject.get_price()
                gs.sheet.Monitor_df.at['Main', 'NowPrice'] = sector.NowPrice
                #print('Price '+ sector.symbol+ ': '+ str(sector.NowPrice))
                # อัพเดท ความเคลื่อนไหวพอร์ต
                gs.sheet.flowlog()

                # สั่ง run ทุก sector ที่สร้างออบเข็ต และรุบะ index ไว้ # for i in rang len():
                # getting length of list
                length = len(sector.sectorObject)

                for i in range(length):
                    if sector.sectorObject[i].indexsector != 0:
                        #print(sector.sectorObject[i].indexsector)
                        sector.sectorObject[i].runSector()

                gs.sheet.getsave_to_sheet('Monitor', 'Set')

                ### ยกเลิกด้วยมือ ####################
                gs.sheet.Command_frontEnd('Settingbot','cancel')
                ### เปิดออเดอร์ด้วยมือ ##
                gs.sheet.Command_frontEnd('Settingbot', 'Openorder')

            if sector.runbot == 'StopMode':
                gs.sheet.Command_frontEnd('Settingbot', 'SetupMap')
                gs.sheet.Command_frontEnd('Settingbot', 'CreateMap')
                gs.sheet.Command_frontEnd('Settingbot', 'Edited')


    @staticmethod
    def LineNotify(mse, typee):
        # แจ้งเตือนผ่านไลน์เมื อเกิดการรีบาลานซ์
        # ที่มา https://jackrobotics.me/line-notify-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2-python-fbab52d1549
        url = 'https://notify-api.line.me/api/notify'
        token = gs.sheet.lineAPI
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

    def getsave_to_map(self,typeGS):
        if typeGS == 'Get':
            # ดึงข้อมูลจาก csv
            self.dfInventory = pd.read_csv('csv_db/' + self.indexsector + 'Map.csv')

        if typeGS == 'Set':
            # บันทึกลง csv
            self.dfInventory.to_csv(str('csv_db/' + self.indexsector + 'Map.csv'), index=False)
        if typeGS == 'SetGoogleSheet':
            # บันทึก ชีทหน้า Map
            gs.sheet.Set_Map_toGoogleSheet(self.dfInventory,self.indexsector)

    def runSector(self):

        #print(self.indexsector)
        #print(sector.static_df)

        self.sector_info_dict = {
            "SectorName": self.indexsector,
            "Capital": gs.sheet.Monitor_df.loc[self.indexsector]['Capital'],  # ทุนต่อ Sector
            "MaxZone": gs.sheet.Monitor_df.loc[self.indexsector]['MaxZone'],  # โซนบน
            "MinZone": gs.sheet.Monitor_df.loc[self.indexsector]['MinZone'],  # โซนล่าง
            "DifZone": gs.sheet.Monitor_df.loc[self.indexsector]['DifZone'],  # ระยะห่าง ระหว่าง ยูนิต
            "Mode": gs.sheet.Monitor_df.loc[self.indexsector]['Mode'],  # ใช้สำหรับกรณี ฟิวเจอร์
            "Play": gs.sheet.Monitor_df.loc[self.indexsector]['Play'],  # อยู่เฉยๆ , เล่น , ยกเลิกออเดอร์ , สร้างไฟล์ Map.csv
            "setup_before_trade": gs.sheet.Monitor_df.loc[self.indexsector]['SectorCSV_Check'], # ตั้งค่าก่อนเทรดหรือยัง เช่น วางซน ระยะห่าง Gap
            "tradeFuntion": gs.sheet.Monitor_df.loc[self.indexsector]['TradeFuntion'],  # ฟังก์ชั่นเทรด
            'timeframe': gs.sheet.Monitor_df.loc[self.indexsector]['timeframe'],  # ค่าฟังก์ชั่นเทรด ตัวแรก เช่น ทามเฟทรม
            'period': gs.sheet.Monitor_df.loc[self.indexsector]['period'],  # ค่าฟังก์ชั่นเทรด ตัวสอง เช่น ระยะ
            'exposure': gs.sheet.Monitor_df.loc[self.indexsector]['ExposurePerBullet']
        }
        self.getsave_to_map('Get')



        # ตรวจสอบดูว่า ออบเจ็ต โดนสร้างขึ้นมาจริงๆไหม โดยการบอกชื่อ
        #print(self.sector_info_dict["SectorName"])
        # คำนวณ สัดส่วน ทุนต่อ Sector ว่าเป็นเท่าไรต่อ ทุนหลัก
        CapitalMain = gs.sheet.Monitor_df.loc['Main']['Capital'] # ทุนหลัก 1700 บาท
        CapitalSector = self.sector_info_dict["Capital"]  # ทุนต่อSector 360 บาท
        minRatio = CapitalMain/100          # 1 % ของทุนหลักคือ เท่าไร ....17 บาท
        gs.sheet.Monitor_df.at[self.indexsector, 'RatioCapital'] = CapitalSector/minRatio # 360/17 = 21 %

        # ถ้า ติดตั้งโซนแล้ว ทั้งสร้าง Map ใน Google sheet และไฟล์ฐานข้อมูลแบบ CSV ให้ไปเปลี่ยนเป็น 2  ## setup_before_trade = SetupSector if 2 can trade and other wait
        if self.sector_info_dict['setup_before_trade'] == 'Yes':

            # ทุน
            Capital = gs.sheet.Monitor_df.loc[self.indexsector]['Capital']

            # พื้นที่โซนเทรด
            MaxZone = self.sector_info_dict["MaxZone"]
            MinZone = self.sector_info_dict["MinZone"]
            DifZone = self.sector_info_dict["DifZone"]

            zoneTrede = MaxZone - MinZone
            # ขนาดโซน ZoneTrede
            gs.sheet.Monitor_df.at[self.indexsector, 'ZoneTrede'] = zoneTrede

            # หาว่า โซนเทรดมีขนาดกี่ % ของ ราคาเต็ม
            ratioAreaTrade = 100 - (MinZone / (MaxZone / 100))
            # หาว่า พื้นที่โซนเทรด คิดเป็นสัดส่วนเท่าไร จาก 100 ส่วน เพื่อเอาไปคูณเลเวเรจ
            Leverage = 100 / ratioAreaTrade
            # ratioAreaTrade อัตราส่วนโซนเทรด ต่อโซนบน , Leverage ที่เกิดจากการบีบโซน
            gs.sheet.Monitor_df.at[self.indexsector, 'ratioAreaTrade'] = ratioAreaTrade
            gs.sheet.Monitor_df.at[self.indexsector, 'Leverage'] = Leverage

            # หาจำนวนกระสุน
            BulletLimit = zoneTrede / DifZone
            # ต้นทุน Exposure ต่อนัด
            ExposurePerBullet = Capital / BulletLimit
            gs.sheet.Monitor_df.at[self.indexsector, 'BulletLimit'] = BulletLimit
            gs.sheet.Monitor_df.at[self.indexsector, 'ExposurePerBullet'] = ExposurePerBullet

            # ต้นทุน Exposure แบบเลเวอเรจ ต่อนัด
            levExposurePerBullet = ExposurePerBullet * Leverage
            gs.sheet.Monitor_df.at[self.indexsector, 'levExposurePerBullet'] = levExposurePerBullet

            exposureType = ExposurePerBullet

            #print(self.sector_info_dict['Play'])

            if self.sector_info_dict['Play'] == 'Yes':
                value_fx = self.callfxTrade(self.sector_info_dict['tradeFuntion'],self.sector_info_dict['timeframe'],self.sector_info_dict['period'])
                self.Trigger_trade(value_fx)

                if gs.sheet.Monitor_df.loc[self.indexsector]['BulletHold'] > 0:
                    gs.sheet.Monitor_df.at[self.indexsector, 'Stack'] = 'Yes'

                # บันทึกลง csv
                self.getsave_to_map('Set')
                # บันทึก ชีทหน้า Map
                self.getsave_to_map('SetGoogleSheet')


            else:
                print('idle')

        elif gs.sheet.Monitor_df.loc[self.indexsector]['SectorCSV_Check'] != 'Wait':
            gs.sheet.Monitor_df.at[self.indexsector, 'SectorCSV_Check'] = 'No'



    def Trigger_trade(self,value_fx):
        #print(sector.NowPrice)
        #print(sector.NowPrice + (float(value_fx['upper']) - float(value_fx['ave'])))
        # ปัญหา iterrows ลูป row ไม่ยอม update
        # https://stackoverflow.com/questions/23330654/update-a-dataframe-in-pandas-while-iterating-row-by-row
        # Gap ขั้นต่ำ ระหว่างกระสุน
        DifZone = self.sector_info_dict["DifZone"]

        sumExposureBuy = 0
        sumPosition = 0
        sumBulletHold = 0
        sumUseZone = 0
        sumNAVsector = 0

        MaxZone = self.sector_info_dict["MaxZone"]
        MinZone = self.sector_info_dict["MinZone"]

        # maptrigger
        for i, row in self.dfInventory .iterrows():
            if pd.notna(row['Zone']) and row['Zone'] > 0:
                ###++++++ ขอบเขตโซนที่กำหนด ++++++####
                if row['Zone'] >= MinZone and row['Zone'] <= MaxZone:
                    self.dfInventory .at[i, 'UseZone'] = 1
                elif row['Zone'] < MinZone or row['Zone'] > MaxZone:
                    self.dfInventory .at[i, 'UseZone'] = -1

                if sector.NowPrice < row['Zone']:
                    self.dfInventory .at[i, 'MapTrigger'] = 1
                elif sector.NowPrice > row['Zone']:
                    self.dfInventory .at[i, 'MapTrigger'] = -1

                if pd.isna(row['TradeTrigger']):
                    # ---- เลือกว่าจะเทรดด้วยเงื่อนไขอะไรโดยการสุ่ม 3 ทามเฟรม 6 รูปแบบ
                    # dfMap.at[i, 'TradeTrigger'] = random.randint(1, 100)
                    whatF = self.sector_info_dict['tradeFuntion']
                    if whatF == 'Bollinger_band':
                        self.dfInventory .loc[i, 'TradeTrigger'] = 987
                    if whatF == 'Grid':
                        self.dfInventory.loc[i, 'TradeTrigger'] = 986


                # ---- ดู Exposure ที่ถือครองอยู่
                if row['ExposureBuy'] > 0:
                    countExposure = row['ExposureBuy']
                    sumExposureBuy = sumExposureBuy + countExposure
                    gs.sheet.Monitor_df.at[self.indexsector, 'ExposureSize'] = sumExposureBuy

                # ---- ดู จำนวนกระสุนที่สามารถใช้ได้ในโซนที่กำหนด
                if row['UseZone'] == 1:
                    sumUseZone = sumUseZone + 1
                    gs.sheet.Monitor_df.at[self.indexsector, 'BulletLimit'] = sumUseZone
                if row['FilledBuy'] > 0 and row['FilledBuy'] != 0 and pd.notna(row['FilledBuy']):
                    # ---- ดู ขนาด Position ที่ถือครองอยู่
                    countPosition = row['FilledBuy']
                    sumPosition = sumPosition + countPosition
                    gs.sheet.Monitor_df.at[self.indexsector, 'PositionSize'] = sumPosition
                    # ---- ดู จำนวนกระสุน ที่ถือครองอยู่
                    sumBulletHold = sumBulletHold + 1
                    gs.sheet.Monitor_df.at[self.indexsector, 'BulletHold'] = sumBulletHold
                    # ---- ดู NAV กระสุนแต่ล่ะนัด # ถ้าซื้อถูก แล้ว ราคาปัจจุบันแพงกว่า Exposure ปัจจุบัน มันจะมากกว่า Exposure ที่เคยซื้อต่ำในอดีต
                    Exposurediff = row['FilledBuy'] * sector.NowPrice
                    NAV = Exposurediff - row['ExposureBuy']
                    self.dfInventory .at[i, 'NAV'] = NAV
                    # --- นับ NAV ทั้งหมดใน sector
                    sumNAVsector = sumNAVsector + NAV
                    gs.sheet.Monitor_df.at[self.indexsector, 'NAV'] = sumNAVsector

                self.getsave_to_map('Set')

                # กระสุนนัดนี้ไม่ว่าง
                if pd.notna(row['IDorderBuy']):

                    #print(value_fx['upper'])
                    #print(value_fx['ave'])
                    #print(value_fx['lower'])

                    # ส่งคำสั่งซื้อไปแล้ว ดูว่ารับของมาหรือยัง
                    if pd.isna(row['FilledBuy']):
                        # ไอดีออเดอร์
                        idOrderbuy = row['IDorderBuy']
                        # เรียกจาก โมดุล Broker
                        orderMatchedBUY = sector.exchangeObject.get_info_order_byID(idOrderbuy,'buy')
                        if orderMatchedBUY['filled'] == orderMatchedBUY['amount']:
                            self.dfInventory .at[i, 'FilledBuy'] = orderMatchedBUY['filled']
                            self.dfInventory .at[i, 'ExposureBuy'] = float(orderMatchedBUY['filled']) * float(orderMatchedBUY['price'])
                            self.dfInventory .at[i, 'feeBuy'] = orderMatchedBUY['fee']  # fee
                            # บันทึกลง csv
                            self.getsave_to_map('Set')
                            '''
                            t = datetime.datetime.strptime(OpenTime, '%Y-%m-%dT%H:%M:%S.%fz')
                            timestamp = datetime.datetime.timestamp(t)
                            self.dfInventory.at[i, 'OpenTime'] = timestamp
                            '''
                            # แจ้งว่าเปิดออเดอร์ Buy
                            print('OpenOrder Price : ' + str(orderMatchedBUY['price']))
                            print('Amount : ' + str(orderMatchedBUY['filled']))
                        '''if row['IDorderBuy'] == 26527731436 :
                            start_time = row['OpenTime']
                            target_time = start_time + 3600  # นับถอยหลัง 60 นาที เพื่อยกเลิกออเดอร์
                            now_time = time.time()
                            timeElapsed = now_time - target_time
                            print(orderMatchedBUY['filled'])
                            if orderMatchedBUY['filled'] == 0:
                                print(self.dfInventory.loc[i, 'FilledBuy'])
                                print(orderMatchedBUY['amount'])
                                print(row['OpenTime'])

                                if 0 < orderMatchedBUY['amount'] and pd.notna(row['OpenTime']):
                                    print('WWWWWWW')'''

                            #print(26527731436)
                        if 0 < orderMatchedBUY['amount'] and pd.notna(row['OpenTime']):
                            # ผ่านไป 60 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
                            start_time = row['OpenTime']
                            target_time = start_time + 3600  # นับถอยหลัง 60 นาที เพื่อยกเลิกออเดอร์
                            now_time = time.time()
                            timeElapsed = now_time - target_time
                            #print(timeElapsed)
                            if timeElapsed > 0:
                                if orderMatchedBUY['filled'] == 0:  # ถ้าหมดเวลา cooldown แล้วไม่ได้เปิดสักทีให้ ยกเลิกออเดอร์ลิมิต Buy
                                    #ยกเลิกออเดอร์
                                    sector.exchangeObject.cancel_order(idOrderbuy, 'buy')

                                    df_check_cancel = pd.DataFrame(sector.exchangeObject.get_my_open_orders()).set_index('id')
                                    check_cancel = row['IDorderBuy'] in df_check_cancel.index

                                    if check_cancel == False:

                                        # ลบ ข้อมูลกระสุนนัดนี้ เมื่อยกเลิกออเดอร์
                                        # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                                        self.dfInventory .loc[i, 'IDorderBuy'] = np.nan
                                        self.dfInventory .loc[i, 'OpenPrice'] = np.nan
                                        self.dfInventory .loc[i, 'AmountBuy'] = np.nan
                                        self.dfInventory .loc[i, 'FilledBuy'] = np.nan
                                        self.dfInventory .loc[i, 'ExposureBuy'] = np.nan
                                        self.dfInventory .loc[i, 'OpenTime'] = np.nan
                                        # บันทึกลง csv
                                        self.getsave_to_map('Set')

                                # ถ้าผ่านไป 60 นาทีแล้วได้ของบางส่วน ก็ตัดที่เหลือทิ้ง เอาแค่นี้พอ...
                                if orderMatchedBUY['filled'] > 0 and orderMatchedBUY['filled'] < orderMatchedBUY['amount'] :
                                    # ยกเลิกออเดอร์
                                    sector.exchangeObject.cancel_order(idOrderbuy, 'buy')
                                    df_check_cancel = pd.DataFrame(sector.exchangeObject.get_my_open_orders()).set_index('id')
                                    check_cancel = row['IDorderBuy'] in df_check_cancel.index

                                    if check_cancel == False:

                                        #บันทึกข้อมูล ออเดอร์ลง pandas
                                        self.dfInventory .at[i, 'FilledBuy'] = orderMatchedBUY['filled']
                                        self.dfInventory .at[i, 'ExposureBuy'] = float(orderMatchedBUY['filled']) * float(orderMatchedBUY['price'])
                                        self.dfInventory .at[i, 'feeBuy'] = orderMatchedBUY['fee']  # fee

                                        # แจ้งว่า เปิดออเดอร์ Buy
                                        print('OpenOrder Price : ' + str(orderMatchedBUY['price']))
                                        print('Amount : ' + str(orderMatchedBUY['filled']))

                    # ถ้ารับของมาแล้ว
                    elif pd.notna(row['FilledBuy']):

                        # ถ้าไอดีออเดอร์ sell ไม่ว่าง แสดงกำลังรอ ขาย
                        if pd.notna(row['IDorderSell']):
                            idOrdersell = row['IDorderSell']
                            orderMatchedSELL = sector.exchangeObject.get_info_order_byID(idOrdersell,'sell')
                            # sell filled ทั้งหมด แสดงว่าปิด กำไร ได้
                            if orderMatchedSELL['filled'] == orderMatchedSELL['amount']:
                                self.dfInventory .at[i, 'LastClosePrice'] = orderMatchedSELL['price']
                                self.dfInventory .at[i, 'feeSell'] = orderMatchedSELL['fee']

                                ExposureBuy = float(row['ExposureBuy'])
                                ExposureSell = float(orderMatchedSELL['filled']) * float(orderMatchedSELL['price'])

                                feesell = row['feeSell']
                                feebuy = row['feeBuy']
                                if pd.isna(feesell):
                                    feesell = 0
                                if pd.isna(feebuy):
                                    feebuy = 0

                                profitshow = (ExposureSell - ExposureBuy) - (feesell + feebuy)

                                if pd.isna(row['Profit']):
                                    self.dfInventory .at[i, 'Profit'] = profitshow
                                elif pd.notna(row['Profit']):
                                    self.dfInventory .at[i, 'Profit'] = row['Profit'] + profitshow
                                if pd.isna(row['round']):
                                    self.dfInventory .at[i, 'round'] = 1
                                elif pd.notna(row['round']):
                                    self.dfInventory .at[i, 'round'] = row['round'] + 1


                                print('ราคาขาย : ' + str(orderMatchedSELL['price']))
                                print('กำไร : ' + str(profitshow))

                                profitshowLine = round(profitshow, 4)
                                sector.LineNotify('\n' + 'ราคาขาย : ' + str(orderMatchedSELL['price']) + '\n' + 'กำไร : ' + str(
                                    profitshowLine) + ' usd', 'change')
                                if pd.isna(profitshow):
                                    sector.LineNotify(
                                        'บัค nan ExposureSell : ' + str(ExposureSell) + '\n' +
                                        'บัค nan ExposureBuy : ' + str(ExposureBuy) + '\n' +
                                        'บัค nan feeSell : ' + str(row['feeSell']) + '\n' +
                                        'บัค nan feeBuy : ' + str(row['feeBuy'])
                                        , 'change')

                                # idOrderbuy = row['IDorderBuy']
                                # orderMatchedBUY = checkByIDoder(idOrderbuy)


                                # dfTradeLog = get_as_dataframe(gc.open(sheetname).worksheet('TradeLog'))
                                gs.sheet.getsave_to_sheet('TradeLog', 'Get')
                                # บันทึก TradeLog
                                # ต้องแปลงเป็น สติงทั้งหมดไม่งั้นบันทึกไม่ได้
                                # กำหนด PD ก่อน
                                dfTradeLog = pd.DataFrame({'IDorderOrderBuy': [str(row['IDorderBuy'])]
                                                               , 'IDorderOrderSell': [str(idOrdersell)]
                                                               , 'Open': [str(row['OpenPrice'])]
                                                               , 'Close': [str(row['ClosePrice'])]
                                                               , 'Amount': [str(row['AmountSell'])]
                                                               , 'TradeTrigger': [str(row['TradeTrigger'])]
                                                               , 'Zone': [str(row['Zone'])]
                                                               , 'OpenTime': [str(datetime.datetime.fromtimestamp(row['OpenTime']).isoformat())]
                                                               , 'CloseTime': [str(datetime.datetime.fromtimestamp(row['CloseTime']).isoformat())]
                                                               , 'Profit': [str(profitshow)]
                                                               , 'feeBuy': [str(row['feeBuy'])]
                                                               , 'feeSell': [str(row['feeSell'])]
                                                            })
                                gs.sheet.TradeLog_df = gs.sheet.TradeLog_df.append(dfTradeLog, ignore_index=True)
                                gs.sheet.getsave_to_sheet('TradeLog', 'Set')


                                # ลบ ข้อมูลกระสุน เมื่อจบครบรอบ ทำให้กระสุนว่าง
                                # ข้อมูลกระสุน buy
                                self.dfInventory .loc[i, 'IDorderBuy'] = np.nan
                                self.dfInventory .loc[i, 'OpenPrice'] = np.nan
                                self.dfInventory .loc[i, 'AmountBuy'] = np.nan
                                self.dfInventory .loc[i, 'FilledBuy'] = np.nan
                                self.dfInventory .loc[i, 'OpenTime'] = np.nan
                                self.dfInventory .loc[i, 'ExposureBuy'] = np.nan
                                self.dfInventory .loc[i, 'NAV'] = np.nan
                                self.dfInventory .loc[i, 'feeBuy'] = np.nan

                                # คืนสถานะ รูปแบบการเทรด เพื่อสุ่มใหม่
                                #self.dfInventory .loc[i, 'TradeTrigger'] = np.nan

                                # ข้อมูลกระสุน sell
                                self.dfInventory .loc[i, 'IDorderSell'] = np.nan
                                self.dfInventory .loc[i, 'ClosePrice'] = np.nan
                                self.dfInventory .loc[i, 'AmountSell'] = np.nan
                                self.dfInventory .loc[i, 'CloseTime'] = np.nan
                                self.dfInventory .loc[i, 'feeSell'] = np.nan

                                # บันทึกลง csv
                                self.getsave_to_map('Set')

                            # ถ้าหมดเวลา cooldown แล้วไม่ได้ขายสักที ให้ยกเลิกออเดอร์ลิมิต Sell
                            elif orderMatchedSELL['filled'] == 0 and pd.notna(row['CloseTime']):
                                # ผ่านไป 60 นาที หรือยัง ถ้าจริง ให้ ยกเลิกออเดอร์
                                start_time = row['CloseTime']
                                target_time = start_time + 86400  # นับถอยหลัง 24ชั่วโมง เพื่อยกเลิกออเดอร์ Sell
                                now_time = time.time()
                                timeElapsed = now_time - target_time
                                #print(timeElapsed)
                                if timeElapsed > 0:
                                    # ยกเลิกออเดอร์
                                    sector.exchangeObject.cancel_order(idOrdersell, 'sell')
                                    df_check_cancel = pd.DataFrame(sector.exchangeObject.get_my_open_orders()).set_index('id')
                                    check_cancel = row['IDorderSell'] in df_check_cancel.index

                                    if check_cancel == False :
                                        # ลบ ข้อมูลกระสุนนัดนี้ เพื่อยกเลิกออเดอร์
                                        # ถ้า cancel แล้วต้องเคลียร์ค่าเก่าออกให้หมด ไม่นั้นจะ error ccxt.base.errors.InvalidOrder: order_not_exist_or_not_allow_to_cancel
                                        self.dfInventory .loc[i, 'IDorderSell'] = np.nan
                                        self.dfInventory .loc[i, 'ClosePrice'] = np.nan
                                        self.dfInventory .loc[i, 'AmountSell'] = np.nan
                                        self.dfInventory .loc[i, 'CloseTime'] = np.nan

                                        # บันทึกลง csv
                                        self.getsave_to_map('Set')
                        # ดูว่าเข้าเงื่อนไข รีบาลานซ์ไหม
                        if row['MapTrigger'] == -1:
                            # จะเปิด ออเดอร์ sell ได้ต้องมี Position Szie ด้าน Buy ก่อน
                            # เงื่อนไข ยิงกระสุน sell
                            # (X*Y) + ((X*Y)/1000)  exposure add 0.5% value
                            ExposureStart = (row['FilledBuy'] * row['OpenPrice']) + ((row['FilledBuy'] * row['OpenPrice'])/200)
                            Exposurediff = row['FilledBuy'] * sector.NowPrice

                            if pd.isna(row['IDorderSell']) and pd.notna(row['OpenPrice']) and Exposurediff > ExposureStart:

                                # ลดของที่มีอยู่ โดยลด Buy Hold ที่ถือไว้ โดย เปิด Sell เท่ากับ จำนวน Position ของกระสุนนัดนั้นๆ
                                targetpirce = sector.NowPrice
                                checktradesell = False
                                if row['TradeTrigger'] == 986: # Grid
                                    if sector.NowPrice > (row['OpenPrice'] + (DifZone * 1)):
                                        checktradesell = True
                                if row['TradeTrigger'] == 987: # Bollinger_band
                                    if sector.NowPrice > value_fx['ave'] and sector.NowPrice < value_fx['upper']:
                                        checktradesell = True
                                    elif sector.NowPrice > value_fx['upper']:
                                        targetpirce = sector.NowPrice + (float(value_fx['upper']) - float(value_fx['ave']))
                                        checktradesell = True


                                '''
                                if tradeFuntion == 'RSI':
                                    if row['TradeTrigger'] >= 1 and row['TradeTrigger'] <= 40:
                                        getRSIvalue = RSI('5m')
                                        if getRSIvalue > 70:
                                            print(getRSIvalue)
                                            checktradesell = True
    
                                    if row['TradeTrigger'] >= 41 and row['TradeTrigger'] <= 70:
                                        getRSIvalue = RSI('15m')
                                        if getRSIvalue > 70:
                                            print(getRSIvalue)
                                            checktradesell = True
    
                                    if row['TradeTrigger'] >= 71 and row['TradeTrigger'] <= 90:
                                        getRSIvalue = RSI('1h')
                                        if getRSIvalue > 70:
                                            print(getRSIvalue)
                                            checktradesell = True
    
                                    if row['TradeTrigger'] >= 91 and row['TradeTrigger'] <= 100:
                                        getRSIvalue = RSI('4h')
                                        if getRSIvalue > 70:
                                            print(getRSIvalue)
                                            checktradesell = True
                                    if row['TradeTrigger'] == 101:
                                        getRSIvalue = RSI('1m')
                                        if getRSIvalue > 70:
                                            print(getRSIvalue)
                                            checktradesell = True
                                if tradeFuntion == 'SuperTrend':
                                    getvalue = SuperTrend2('1m')
                                    if getvalue == 2:
                                        print('Sell')
                                        checktradesell = True
    
                                if tradeFuntion == 'percent':
                                    Openprice_ = row['OpenPrice']
                                    minpercenttore = Openprice_ / 100
                                    Closeprice_ = Openprice_ + minpercenttore
                                    if NowPrice > Closeprice_:
                                        checktradesell = True
                                '''
                                if checktradesell == True:
                                    positionSizeClose = row['FilledBuy']
                                    #print(targetpirce)
                                    #print(sector.NowPrice)
                                    # เปิดออเดอร์ Sell เพื่อปิดออเดอร์ Buy
                                    orderSell = sector.exchangeObject.open_close('limit', 'sell', positionSizeClose, targetpirce)

                                    if orderSell['id'] != 0:
                                        self.dfInventory.at[i, 'IDorderSell'] = orderSell['id']
                                        self.dfInventory.at[i, 'ClosePrice'] = orderSell['price']
                                        self.dfInventory.at[i, 'AmountSell'] = orderSell['amount']
                                        self.dfInventory.at[i, 'CloseTime'] = orderSell['timestamp']

                                        # บันทึกลง csv
                                        self.getsave_to_map('Set')

                # ดูว่าเข้าเงื่อนไข รีบาลานซ์ไหม
                if row['MapTrigger'] == 1 :
                    # เงื่อนไข ยิงกระสุน buy ใช้งานกระสุนนัดนี้
                    if pd.isna(row['IDorderBuy'])  and row['UseZone'] == 1:

                        # MapTrigger = 1 คือ พื้นที่ๆ สามารถมีกระสุนได้ เพราะ ต่ำกว่า RP
                        checktradebuy = False
                        if row['TradeTrigger'] == 986: # Grid
                            checktradebuy = True

                        if row['TradeTrigger'] == 987: # Bollinger_band
                            if sector.NowPrice > value_fx['ave'] and sector.NowPrice < value_fx['upper']:
                                 checktradebuy = True


                        '''
                        if tradeFuntion == 'RSI':
                            if row['TradeTrigger'] >= 1 and row['TradeTrigger'] <= 40:
                                getRSIvalue = RSI('5m')
                                if getRSIvalue < 30:
                                    checktradebuy = True
                            if row['TradeTrigger'] >= 41 and row['TradeTrigger'] <= 70:
                                getRSIvalue = RSI('15m')
                                if getRSIvalue < 30:
                                    checktradebuy = True
    
                            if row['TradeTrigger'] >= 71 and row['TradeTrigger'] <= 90:
                                getRSIvalue = RSI('1h')
                                if getRSIvalue < 30:
                                    checktradebuy = True
    
                            if row['TradeTrigger'] >= 91 and row['TradeTrigger'] <= 100:
                                getRSIvalue = RSI('4h')
                                if getRSIvalue < 30:
                                    checktradebuy = True
    
                            if row['TradeTrigger'] == 101:
                                getRSIvalue = RSI('1m')
                                if getRSIvalue < 30:
                                    checktradebuy = True
                                    # ถ่วงเวลา ตอนโวเข้า
                                    # df._set_value(whatsymbol, 'TimerDelay', time.time())
                                    # df._set_value(whatsymbol, 'Stat', 'Cooldown')
                        if tradeFuntion == 'SuperTrend':
                            getvalue = SuperTrend2('1m')
                            if getvalue == 1:
                                print('Buy')
                                checktradebuy = True
    
                        if tradeFuntion == 'percent':
                            if NowPrice < row['Zone']:
                                checktradebuy = True
                        '''
                        if checktradebuy == True:
                            # ต้นทุนกระสุนต่อนัด
                            expousre = self.sector_info_dict["exposure"]
                            # ปริมาณสินค้าที่จะตั้งออเดอร์ ต่อ กระสุน 1นัด
                            amount = abs(expousre) / float(sector.NowPrice)

                            orderBuy = sector.exchangeObject.open_close('limit', 'buy', amount, sector.NowPrice)

                            if orderBuy['id'] != 0:

                                self.dfInventory .at[i, 'IDorderBuy'] = orderBuy['id']
                                self.dfInventory .at[i, 'OpenPrice'] = orderBuy['price']
                                self.dfInventory .at[i, 'AmountBuy'] = orderBuy['amount']
                                self.dfInventory .at[i, 'OpenTime'] = orderBuy['timestamp']

                                # บันทึกลง csv
                                self.getsave_to_map('Set')


    def callfxTrade(self,fxt,timeframe,period):
        if fxt == 'Bollinger_band' :
            value = self.exchangeObject.call_bbands(timeframe,int(period))
            #print(value)
            return value
