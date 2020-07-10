import ccxt
import pandas as pd


subaccount = 'ForTest'  # ถ้ามี ซับแอคเคอร์ของ FTX
exchange = ccxt.ftx({
        'apiKey': '67ocpnDbgwgmRhYyVocUjuuHgvzUQIdMGgpavMsP',
        'secret': 'dSF5qS_E2t6iNgmBPC2DorSwwatMsM0blFf1zeQI',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }

#order = exchange.create_order("TRX-PERP", 'limit', 'sell', 2 ,0.01804)
#print(order['id'])

def checkByIDoder(id):
    oderinfo = exchange.fetch_order(id)
    return oderinfo

#print(checkByIDoder('6426263980'))
#print(checkByIDoder('6426425799'))

#1 datetime = datetime
#2 id = IDorder
#3 balance
#4 Multiply
#5 side = Side
#6 price = Price
#7 size =  Amount
#8 filledSize = Filled (ต้องเท่ากับ Amount)
#10 price x size = value
#11 exposure
# 'status': 'closed' = ยกเลิกออเดอร์

# https://www.youtube.com/watch?v=-e5opMP3TKo
df3 = pd.read_csv('TradeRecord.csv')
info = checkByIDoder('6426425799')
print(info)

datetime = info['datetime']
IDorder = info['id']
balance = 0
Multiply = 0
Side = info['side']
Price = info['price']
Amount = info['amount']
Filled = info['filled']
PositionSize  = Amount*Price
exposure = PositionSize

#if info['side'] == 'buy':
#    exposure = PositionSize*(-1)
#else:
#    row = pd.Series([datetime, IDorder, balance, Multiply, Side, Price, Amount, Filled, PositionSize, exposure],index=df3.columns)
#    df3 = df3.append(row, ignore_index=True)
#    #df3 = df3.reset_index()
#    df3.to_csv("TradeRecord.csv", index=False)



#เติมข้อมูล ออเดอร์ที่แมตแล้ว พร้อมคำนวณ exposure
