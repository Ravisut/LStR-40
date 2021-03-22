import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import division as di
import numpy as np
import pandas as pd
import broker as bk
import time
import datetime


class sheet:
    # Google sheet
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
    gc = gspread.authorize(creds)
    sheetName = 'Data2'

    # หน้าส่อง sector
    Monitor_df = None
    # หน้าตั้งค่าบอท
    Settingbot_df = None
    # หน้าบันทึกผลการเทรด
    TradeLog_df = None
    # หน้าดูความเคลื่อนไหวในพอร์ต
    FlowLog_df = None

    #### Exchange
    nameExchange = None
    apiKey = None
    secret = None
    subaccount = None
    lineAPI = None
    symbol = None
    asset = None
    mainAsset = None
    typeTrade = None


    @staticmethod
    def Command_frontEnd(page, command):
        # เรียกข้อมูลจากหน้า setting ว่าบันทึกอะไรไว้บ้าง
        sheet.getsave_to_sheet('Settingbot', 'Get')
        if page == 'Settingbot':
            if command == 'Setup_api':

                #### Exchange
                sheet.nameExchange = sheet.Settingbot_df.loc['index_6']['key_2']
                sheet.apiKey = sheet.Settingbot_df.loc['index_7']['key_2']
                sheet.secret = sheet.Settingbot_df.loc['index_8']['key_2']
                sheet.subaccount = sheet.Settingbot_df.loc['index_9']['key_2']
                sheet.lineAPI = sheet.Settingbot_df.loc['index_10']['key_2']
                sheet.symbol = sheet.Settingbot_df.loc['index_11']['key_2']
                sheet.asset = sheet.Settingbot_df.loc['index_12']['key_2']
                sheet.mainAsset = sheet.Settingbot_df.loc['index_13']['key_2']
                sheet.typeTrade = sheet.Settingbot_df.loc['index_14']['key_2']

                # ตั้งค่า Exchange
                di.sector.exchangeObject = bk.broker(sheet.apiKey, sheet.secret, sheet.subaccount, sheet.symbol, sheet.nameExchange, sheet.typeTrade)
                # ปุ่มหลัก
                di.sector.runbot = sheet.Settingbot_df.loc['index_12']['key_6']

            if command == 'Cancel':
                ### ยกเลิกด้วยมือ ####################
                if sheet.Settingbot_df.loc['index_24']['key_7'] == 'Cancel':
                    try:
                        idOrder = sheet.Settingbot_df.loc['index_24']['key_5']
                        sidee_cancel = sheet.Settingbot_df.loc['index_24']['key_6']
                        di.sector.exchangeObject.cancel_order(idOrder, sidee_cancel)

                        sheet.Settingbot_df.loc['index_24', 'key_5'] = np.nan  # ไอดี ออเดอร์
                        sheet.Settingbot_df.loc['index_24', 'key_6'] = np.nan  # ด้าน buy/sell
                        sheet.Settingbot_df.loc['index_24', 'key_7'] = 'No'  # คำสั่งยกเลิก
                        sheet.Settingbot_df.loc['index_24', 'key_8'] = 'Done !' # แสดงผล
                    except Exception as e:
                        sheet.Settingbot_df.loc['index_24', 'key_5'] = np.nan
                        sheet.Settingbot_df.loc['index_24', 'key_6'] = np.nan
                        sheet.Settingbot_df.loc['index_24', 'key_7'] = 'No'
                        sheet.Settingbot_df.loc['index_24', 'key_8'] = str(e)  # แสดงผล

                        pass
                    sheet.getsave_to_sheet('Settingbot', 'Set')

            if command == 'Openorder':
                ### เปิดออเดอร์ด้วยมือ #######
                sidee = sheet.Settingbot_df.loc['index_24']['key_7']
                if sidee == 'Buy' or sidee == 'Sell':

                    typee = sheet.Settingbot_df.loc['index_24']['key_2']  # ลิมิต หรือ ตามตลาด
                    pricee = sheet.Settingbot_df.loc['index_24']['key_3'] # ราคาสำหรับ ลิมิต
                    amontt = sheet.Settingbot_df.loc['index_24']['key_4'] # จำนวนเงิน

                    try:
                        orderreturn = di.sector.exchangeObject.open_close(typee, sidee, amontt, pricee)
                        if orderreturn['id'] != 0:
                            sheet.Settingbot_df.loc['index_24', 'key_1'] = 'No'  # buy/sell
                            sheet.Settingbot_df.loc['index_24', 'key_2'] = 'No'  # ประเถทลิมิตหรือ market
                            sheet.Settingbot_df.loc['index_24', 'key_3'] = np.nan  # ราคา
                            sheet.Settingbot_df.loc['index_24', 'key_4'] = np.nan  # จำนวน
                            sheet.Settingbot_df.loc['index_24', 'key_8'] = 'ID:' + str(orderreturn['id']) + ' Done'
                            print('Done')

                    except Exception as e:

                        sheet.Settingbot_df.loc['index_24', 'key_1'] = 'No'
                        sheet.Settingbot_df.loc['index_24', 'key_2'] = 'No'
                        sheet.Settingbot_df.loc['index_24', 'key_3'] = np.nan
                        sheet.Settingbot_df.loc['index_24', 'key_4'] = np.nan
                        sheet.Settingbot_df.loc['index_24', 'key_8'] = str(e)
                        pass
                    sheet.getsave_to_sheet('Settingbot', 'Set')

            if command == 'SetupMap':
                if sheet.Settingbot_df.loc['index_20']['key_7'] == 'SetupMap':
                    sheet.SetupZone_befreTrade()
                    sheet.Settingbot_df.loc['index_20', 'key_7'] = 'No'
                    sheet.getsave_to_sheet('Settingbot', 'Set')

            if command == 'CreateMap':
                if sheet.Settingbot_df.loc['index_20']['key_7'] == 'CreateMap':

                    sectorName = sheet.Settingbot_df.loc['index_20']['key_6']

                    if sheet.Monitor_df.loc[sectorName]['Stack'] != 'Yes':

                        Capital = sheet.Settingbot_df.loc['index_20']['key_1']
                        MaxZone = sheet.Settingbot_df.loc['index_20']['key_2']
                        MinZone = sheet.Settingbot_df.loc['index_20']['key_3']
                        DifZone = sheet.Settingbot_df.loc['index_20']['key_4']
                        #Mode = sheet.Settingbot_df.loc['index_20']['key_6']

                        if Capital != None and MaxZone != None and MinZone != None and DifZone != None:

                            sheet.Monitor_df.loc[sectorName, 'Capital'] = Capital
                            sheet.Monitor_df.loc[sectorName, 'MaxZone'] = MaxZone
                            sheet.Monitor_df.loc[sectorName, 'MinZone'] = MinZone
                            sheet.Monitor_df.loc[sectorName, 'DifZone'] = DifZone
                            #sheet.Monitor_df.loc[sectorName, 'Mode'] = Mode

                            df_reviewMap = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('reviewMap'))
                            set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet(sectorName + 'Map'),df_reviewMap)
                            df_reviewMap.to_csv('csv_db/' + sectorName + 'Map.csv', index=False)

                            sheet.Settingbot_df.loc['index_20', 'key_7'] = 'No'
                            sheet.Settingbot_df.loc['index_20', 'key_8'] = 'New Map !!'
                        elif Capital == None or MaxZone == None or MinZone == None or DifZone == None:
                            sheet.Settingbot_df.loc['index_20', 'key_8'] = 'Add attribute before Create'

                        sheet.getsave_to_sheet('Settingbot', 'Set')
                        sheet.getsave_to_sheet('Monitor', 'Set')

            if command == 'Edited':
                if sheet.Settingbot_df.loc['index_12']['key_7'] == 'Done':
                    # บันทึกสำเนาจากใน ชีท กลับเข้า csv
                    # ---- Flowlog ----
                    df_FlowLog = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('FlowLog'))
                    df_FlowLog.to_csv('csv_db/FlowLog.csv', index=False)
                    # ---- จบ Flowlog ---
                    # ---- TradeLog ----
                    df_TradeLog = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('TradeLog'))
                    df_TradeLog.to_csv('csv_db/TradeLog.csv', index=False)
                    # ---- จบ TradeLog ---

                    # AAAAAAAAAAAAAAA
                    df_AMap = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('AMap'))
                    df_AMap.to_csv('csv_db/AMap.csv', index=False)

                    # BBBBBBBBBBBBBBB
                    df_BMap = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('BMap'))
                    df_BMap.to_csv('csv_db/BMap.csv', index=False)

                    # CCCCCCCCCCCCCCC
                    df_CMap = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('CMap'))
                    df_CMap.to_csv('csv_db/CMap.csv', index=False)

                    # DDDDDDDDDDDDDD
                    df_DMap = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('DMap'))
                    df_DMap.to_csv('csv_db/DMap.csv', index=False)

                    # EEEEEEEEEEEEEE
                    df_EMap = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('EMap'))
                    df_EMap.to_csv('csv_db/EMap.csv', index=False)

                    sheet.Settingbot_df.loc['index_12', 'key_6'] = 'StopMode'
                    sheet.Settingbot_df.loc['index_12', 'key_7'] = 'No'
                    sheet.Settingbot_df.loc['index_12', 'key_8'] = 'Edited'

                    sheet.getsave_to_sheet('Settingbot', 'Set')
                    sheet.getsave_to_sheet('Monitor', 'Set')

    @staticmethod
    def getsave_to_sheet(page,typeGS):
        if page == 'Monitor':
            if typeGS == 'Get':
                sheet.Monitor_df = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('Monitor')).set_index('SectorName')
            if typeGS == 'Set':
                # บันทึกชีทหน้า Monitor
                dff = sheet.Monitor_df.drop(columns=[c for c in sheet.Monitor_df.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
                set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet('Monitor'), dff.reset_index())
        if page == 'Settingbot':
            if typeGS == 'Get':
                sheet.Settingbot_df = get_as_dataframe(sheet.gc.open(sheet.sheetName).worksheet('Settingbot')).set_index('index')
            if typeGS == 'Set':
                # บันทึกชีทหน้า Settingbot
                dfsSb = sheet.Settingbot_df.drop(columns=[c for c in sheet.Settingbot_df.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
                set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet('Settingbot'), dfsSb.reset_index())
        if page == 'TradeLog':
            if typeGS == 'Get':
                sheet.TradeLog_df = pd.read_csv('csv_db/TradeLog.csv')
            if typeGS == 'Set':
                # บันทึก CSV หน้า TradeLog
                sheet.TradeLog_df.to_csv('csv_db/TradeLog.csv', index=False)
                # บันทึกชีทหน้า TradeLog
                dfTradeLogg = sheet.TradeLog_df.drop(columns=[c for c in sheet.TradeLog_df.columns if "Unnamed" in c]).dropna(how="all")
                set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet('TradeLog'), dfTradeLogg)

        if page == 'FlowLog':
            if typeGS == 'Get':
                sheet.FlowLog_df = pd.read_csv('csv_db/FlowLog.csv')
            if typeGS == 'Set':
                # บันทึก CSV หน้า TradeLog
                sheet.FlowLog_df.to_csv('csv_db/FlowLog.csv', index=False)
                # บันทึกชีทหน้า TradeLog
                dfFlowLogg = sheet.FlowLog_df.drop(columns=[c for c in sheet.FlowLog_df.columns if "Unnamed" in c]).dropna(how="all")
                set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet('FlowLog'), dfFlowLogg)


    @staticmethod
    def Set_Map_toGoogleSheet(dfInventory,Map):
        _dfInventry = dfInventory.drop(columns=[c for c in dfInventory.columns if "Unnamed" in c]).dropna(how="all")
        set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet(str(Map + 'Map')), _dfInventry)



    @staticmethod
    def SetupZone_befreTrade():

        # ทุน
        Capital = sheet.Settingbot_df.loc['index_20']['key_1']

        # พื้นที่โซนเทรด
        MaxZone = sheet.Settingbot_df.loc['index_20']['key_2']
        MinZone = sheet.Settingbot_df.loc['index_20']['key_3']
        DifZone = sheet.Settingbot_df.loc['index_20']['key_4']
        # ติด drawdown หรือ ล้างพอร์ต
        #DDorLqd = sheet.Settingbot_df.loc['index_20']['key_6']

        # ขนาดโซน ZoneTrede
        zoneTrede = MaxZone - MinZone
        # ขนาดโซน ZoneTrede

        # หาจำนวนกระสุน
        BulletLimit = zoneTrede / DifZone
        # ต้นทุน Exposure ต่อนัด
        ExposurePerBullet = Capital / BulletLimit
        sheet.Settingbot_df.loc['index_20', 'key_5'] = ExposurePerBullet

        # if MaxZone == np.nan:

        # dfMapp = dfMap.drop(columns=[c for c in dfMap.columns if "Unnamed" in c]).dropna(how="all")
        # ส่งออกไฟล์ csv
        # dfMapp.to_csv('C:/Users/HOME/file_name.csv', index=False) #C:\Users\HOME

        # บันทึก Google shhet
        # dff = sector.static_df.drop(columns=[c for c in sector.static_df.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
        # set_with_dataframe(sector.gc.open(sector.sheetName).worksheet('Monitor'), dff.reset_index())  # บันทึกชีทหน้า Monitor

        if Capital != None and MaxZone != None and MinZone != None and DifZone != None:
            dfmapClone = pd.DataFrame({'Zone': np.arange(MinZone - (DifZone * 10), MaxZone + (DifZone * 10), DifZone)
                                          , 'UseZone': np.nan
                                          , 'Exposure': np.nan
                                          , 'MapTrigger': np.nan
                                          , 'IDorderBuy': np.nan
                                          , 'OpenPrice': np.nan
                                          , 'AmountBuy': np.nan
                                          , 'OpenTime': np.nan
                                          , 'FilledBuy': np.nan
                                          , 'feeBuy': np.nan
                                          , 'ExposureBuy': np.nan
                                          , 'NAV': np.nan
                                          , 'TradeTrigger': np.nan
                                          , 'IDorderSell': np.nan
                                          , 'ClosePrice': np.nan
                                          , 'AmountSell': np.nan
                                          , 'CloseTime': np.nan
                                          , 'feeSell': np.nan
                                          , 'LastClosePrice': np.nan
                                          , 'Profit': np.nan
                                          , 'round': np.nan
                                       })
            # dfmapClone.to_csv(str('csv_setup/'+indexsector+'Map.csv'), index=False)
            # บันทึก ชีทหน้า Map
            dfMapp = dfmapClone.drop(columns=[c for c in dfmapClone.columns if "Unnamed" in c]).dropna(how="all")
            set_with_dataframe(sheet.gc.open(sheet.sheetName).worksheet('reviewMap'), dfMapp)


            sheet.Settingbot_df.loc['index_20', 'key_8'] = 'Wait'
        else:
            sheet.Settingbot_df.loc['index_20', 'key_8'] = '!! Add attribute '

    @staticmethod
    def flowlog():

        # รวม ExposureSize ทั้งหมด ในแต่ล่ะ sector
        sheet.Monitor_df.at['Main', 'ExposureSize'] = 0
        sheet.Monitor_df.at['Main', 'ExposureSize'] = sheet.Monitor_df['ExposureSize'].sum()

        # รวม PositionSize ทั้งหมด ในแต่ล่ะ sector
        sheet.Monitor_df.at['Main', 'PositionSize'] = 0
        sheet.Monitor_df.at['Main', 'PositionSize'] = sheet.Monitor_df['PositionSize'].sum()

        # รวม BulletHold ทั้งหมด ในแต่ล่ะ sector
        sheet.Monitor_df.at['Main', 'BulletHold'] = 0
        sheet.Monitor_df.at['Main', 'BulletHold'] = sheet.Monitor_df['BulletHold'].sum()

        # รวม BulletLimit ทั้งหมด ในแต่ล่ะ sector
        sheet.Monitor_df.at['Main', 'BulletLimit'] = 0
        sheet.Monitor_df.at['Main', 'BulletLimit'] = sheet.Monitor_df['BulletLimit'].sum()

        # รวมสัดส่วนทุนทั้งหมด ที่ใช้ไปในแต่ล่ะ sector
        sheet.Monitor_df.at['Main', 'RatioCapital'] = 0
        sheet.Monitor_df.at['Main', 'RatioCapital'] = sheet.Monitor_df['RatioCapital'].sum()

        if pd.isna(sheet.Monitor_df.loc['Main']['EntryPrice']):
            sheet.Monitor_df.at['Main', 'EntryPrice'] = di.sector.NowPrice
        # อัพเดท ความเคลื่อนไหวของพอร์ต ทุกๆ 4 ชั่วโมง
        if pd.isna(sheet.Monitor_df.loc['Main']['TimeToUpdateFlowLog']):
            sheet.Monitor_df.at['Main', 'TimeToUpdateFlowLog'] = time.time()
        start_time = sheet.Monitor_df.loc['Main']['TimeToUpdateFlowLog']
        target_time = start_time + 14400  # 14400 วินาที คือ 4 ชั่วโมง
        nowtime = time.time()
        timeElapsed = nowtime - target_time
        if timeElapsed > 0:
            # ดูสินทรัพย์หลักและสินทรัพย์ที่เทรด ทั้งหมดและที่สามารถเทรดได้
            mainAssetTotal = di.sector.exchangeObject.get_asset(sheet.mainAsset, 'total')
            sheet.Monitor_df.at['Main', 'TotalMainAsset'] = mainAssetTotal
            mainAssetFree = di.sector.exchangeObject.get_asset(sheet.mainAsset, 'free')

            sheet.Monitor_df.at['Main', 'FreeMainAsset'] = mainAssetFree
            sheet.Monitor_df.at['Main', 'TotalAsset'] = di.sector.exchangeObject.get_asset(sheet.asset, 'total')
            sheet.Monitor_df.at['Main', 'FreeAsset'] = di.sector.exchangeObject.get_asset(sheet.asset, 'free')

            # ดู กำไร ว่าทั้งหมดเท่าไร
            profit = sheet.TradeLog_df['Profit'].sum()

            # ทุนหลัก
            mainCap = sheet.Monitor_df.loc['Main', 'Capital']
            EntryPrice = sheet.Monitor_df.loc['Main']['EntryPrice']
            sheet.Monitor_df.at['Main', 'Profit'] = profit

            # รวม NAV ทั้งหมด ในแต่ล่ะ sector
            sheet.Monitor_df.at['Main', 'NAV'] = 0
            sumNav = sheet.Monitor_df['NAV'].sum()
            sheet.Monitor_df.at['Main', 'NAV'] = sumNav

            # unrealizedMainAsset
            sheet.Monitor_df.at['Main', 'unrealizedMainAsset'] = 0
            unrealizedMainAsset = sumNav + mainCap + profit
            sheet.Monitor_df.at['Main', 'unrealizedMainAsset'] = unrealizedMainAsset

            percentPortValue = (unrealizedMainAsset - mainCap) / (mainCap / 100)
            percentPriceChange = (di.sector.NowPrice - EntryPrice) / (EntryPrice / 100)
            percentGrowth = percentPortValue - percentPriceChange

            sheet.getsave_to_sheet('FlowLog', 'Get')

            dfFlowLog2 = pd.DataFrame({'Datetime': [str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))]
                                          , 'TotalMainAsset': [str(mainAssetTotal)]
                                          , 'FreeMainAsset': [str(mainAssetFree)]
                                          , 'ProductPirce': [str(di.sector.NowPrice)]
                                          , 'percentPortValue': [str(percentPortValue)]
                                          , 'percentPriceChange': [str(percentPriceChange)]
                                          , 'percentGrowth': [str(percentGrowth)]
                                       })
            sheet.FlowLog_df = sheet.FlowLog_df.append(dfFlowLog2, ignore_index=True)
            sheet.Monitor_df.at['Main', 'TimeToUpdateFlowLog'] = time.time()
            sheet.getsave_to_sheet('FlowLog', 'Set')