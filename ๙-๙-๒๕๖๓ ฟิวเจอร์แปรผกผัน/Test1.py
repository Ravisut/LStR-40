import callFuntionFutures
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe, set_with_dataframe

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("API.json", scope)
gc = gspread.authorize(creds)

dftest1 = get_as_dataframe(gc.open("Data").worksheet('Test'))
dftest2 = get_as_dataframe(gc.open("Data").worksheet('Test2'))

def check():

    for i, row in dfMap.iterrows():
        iStr =  '123456'
        row['Stat'] = iStr
        print(row['Stat'])
        if i == 5:

            dfMapp = dfMap.drop(columns=[c for c in dfMap.columns if "Unnamed" in c]).dropna(how="all")  # ลบคอลัม์ที่ไม่ต้องการ และ row ที่ว่าง
            #set_with_dataframe(gc.open("Data").worksheet('Test'), dfMapp)  # บันทึกลง ชีทหน้า
            print(dfMapp)
            return

def check2():
    df2 = pd.DataFrame({'Number':[str(2)]})

    dfMapp = dfMap.append(df2)
    dfMapp = dfMapp.drop(columns=[c for c in dfMapp.columns if "Unnamed" in c]).dropna(how="all")
    set_with_dataframe(gc.open("Data").worksheet('dfMap'), dfMapp)  # บันทึกชีทหน้า TradeLog
    print(dfMapp)

def check3():
    print(callFuntionFutures.checkByIDoder(7778172502))

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

df1 = dftest1.tail(5)
df2 = dftest2.tail(5)
df1 = df1.drop(columns=[c for c in df1.columns if "Unnamed" in c]).dropna(how="all")
df2 = df2.drop(columns=[c for c in df2.columns if "Unnamed" in c]).dropna(how="all")
print(df1)
print(df2)

df3 = pd.concat([df1,df2]).drop_duplicates(keep=False)
df4 = df3.drop_duplicates(subset=['id'], keep='last')
print(df4)

df5 = pd.concat([df1,df4]).drop_duplicates(keep=False)
df5 = df5.drop_duplicates(subset=['id'], keep='last')
df5 = df5.reset_index(drop=True)
print(df5)


print("\n\n=============fetchHistoryTrades=============")
fetchTrades = exchange.fetchMyTrades(symbol=symbol, since=None, limit=2000, params={})
print('Total '+ str(len(fetchTrades))+' rows.')
fetchTrades = pd.json_normalize(data=fetchTrades)
#print(fetchTrades)
df_fetchTrades = pd.DataFrame(data=fetchTrades, columns=['info.time', 'info.future', 'info.id', 'info.price', 'info.side', 'info.size','info.fee'])
df_fetchTrades.to_csv('history.csv',index=False)
print(df_fetchTrades)

my_trades = exchange.private_get_positions()
print("\n=============my_trades=============")
# print(my_trades)
my_trades = pd.json_normalize(data=my_trades['result'])

# cost = USD
#size = BTC
df_curr_trade = pd.DataFrame(my_trades, columns=['future', 'side', 'entryPrice', 'estimatedLiquidationPrice', 'size', 'cost', 'unrealizedPnl', 'realizedPnl'])
print(df_curr_trade)
r1 = json.dumps(exchange.fetch_ticker(symbol))
market_price = json.loads(r1)
print("market_price: " + str(market_price['last']))