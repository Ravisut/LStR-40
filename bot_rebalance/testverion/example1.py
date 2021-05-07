import ccxt       # Import lib ccxt เพื่อติดต่อกับ API ของโบรก
import pandas as pd       # จะต้องมีการเรียกใช้ Lib Pandas
import datetime
from datetime import datetime,timedelta



ftx = ccxt.ftx({
            'apiKey': 'xxxx',           # apiKey
            'secret': 'yyyy' })         # API Secret



# =======================================================
# Section 2 :  load data มาเก็บไว้ กรณีนี้จะเก็บเป็นระดับ 5 นาที เพื่อที่เวลาทดสอบจะได้ไม่ต้องโหลดใหม่บ่อยๆ
# =======================================================
symbol = 'XRP/USD'
timeframe = '5m'        # ประกาศตัวแปร timeframe
dataset = 5000                  # dataset กำหนดจำนวนชุดข้อมูลที่จะดึง
response = ftx.fetch_ohlcv(symbol,timeframe,None,dataset)       # ดึงราคา XRP/USDT ย้อนหลัง ที่ TF(1H) , จำนวนตาม dataset ค่า
#response
hisdata= pd.DataFrame(response,columns=['datex', 'open', 'high', 'low','close','volume'])
#savetocsv
hisdata.to_csv(r'xrp_20210320.csv', index=False)



# =======================================================
# Section 3 :function ที่ต้องใช้
# =======================================================

# ใช้ขยายตัว ชุดลำดับตัวเลขให้มีจำนวนที่เพียงพอ
def xgrowseed(seed):
    growseed = []
    i = 0
    cycle = 0
    for x in range(2016):
        growseed.append(seed[i] + cycle)
        i = i + 1
        if i >= len(seed):
            cycle = growseed[-1]
            i = 0
    # print(len(growseed), growseed[-1], growseed[0:15])
    return growseed


# ใช้สำหรับตัดข้อมลของราคา เพื่อเอามาทำ backtest
def crop_histdata(hisdata, start_date, end_date):
    # hisdata must have column name datex
    his_week = hisdata.loc[(hisdata['datex'] >= datetime.timestamp(start_date) * 1000) & (
                hisdata['datex'] < datetime.timestamp(end_date) * 1000)]
    return his_week


# ใช้สำหรับคำนวน performance ของการทำ rebalance
def getPerformance(closeprice, openprice, start_position, balanceusd, nmagic, nround):
    minpct = 1

    pos = start_position
    pre_valueusd = balanceusd # 100
    accu_sell_USD = 0
    accu_sell_XRP = 0
    accu_buy_USD = 0
    accu_buy_XRP = 0
    # print('start POS:',pos, 'start price:', openprice[0])
    i = 0
    itran = 0
    avg_buy_price = 0
    avg_sell_price = 0
    for x in closeprice:
        valueusd = round(x * pos, 1)
        diffUSD = round(valueusd - pre_valueusd, 1)
        perDiff = round(100 * diffUSD / pre_valueusd, 2)
        i = i + 1
        if i in nmagic:
            fg_rebalance = True
        else:
            fg_rebalance = False

        if perDiff > minpct and fg_rebalance:
            itran = itran + 1
            sell_USD = diffUSD
            accu_sell_USD = round(sell_USD + accu_sell_USD, 1)
            accu_sell_XRP = round(round(diffUSD / x, nround) + accu_sell_XRP, nround)
            pos = round(pre_valueusd / x, nround)
            # print(i,'price:',x,' :value:', valueusd, '== DiffUS:',diffUSD, ' %pct:', perDiff, 'acce Sell:', accu_sell_USD, 'pos:',pos,'accu_sell_XRP:',accu_sell_XRP)
            avg_sell_price = round(accu_sell_USD / accu_sell_XRP, 4)
        elif perDiff < -1 * minpct and fg_rebalance:
            itran = itran + 1
            buy_USD = diffUSD
            accu_buy_USD = round(buy_USD + accu_buy_USD, 1)
            accu_buy_XRP = round(round(diffUSD / x, nround) + accu_buy_XRP, nround)
            pos = round(pre_valueusd / x, nround)
            # print(i,'price:',x,' :value:', valueusd, '== DiffUS:',diffUSD, ' %pct:', perDiff, 'acce Buy:', accu_buy_USD, 'pos:',pos,'accu_buy_XRP:',accu_buy_XRP)
            avg_buy_price = round(accu_buy_USD / accu_buy_XRP, 4)

        match_XRP_amt = min(-accu_buy_XRP, accu_sell_XRP)
        # print ('match XRP amt',match_XRP_amt,'avg_buy_price',avg_buy_price,avg_sell_price,avg_sell_price-avg_buy_price )

    avg_buy_price = round(accu_buy_USD / accu_buy_XRP, 4)
    avg_sell_price = round(accu_sell_USD / accu_sell_XRP, 4)
    match_XRP_amt = min(-accu_buy_XRP, accu_sell_XRP)
    # print ('match XRP amt',match_XRP_amt)
    # print('avg_buy_price',avg_buy_price,avg_sell_price)
    # print('n transaction',itran)
    Cash_gen = (avg_sell_price - avg_buy_price) * match_XRP_amt
    print('Cash Gen:', round(Cash_gen, 1))  # , 'n tran',itran )
    return Cash_gen



# =======================================================
# Section 4 :โหลดข้อมูลที่เรา save เก็บเอาไว้
# =======================================================
hisdata = pd.read_csv(r'xrp_20210320.csv')
hisdata.tail(10)


# =======================================================
# Section 5 : ชุดตัวเลขที่ ต้องการเอามาทำ backtest
# =======================================================
base = [1,2,3,4,5,6,7,8,9]
catalan=[1,2,5,7,14,21,42,56]

majornote=[1,3,5,6,8,10,12]
Fibo=[1,2,3,5,18,23,41,56]

Taksa_sun =[1,3,6,10,17,22,30,36]
Taksa_sun1 =[1,3,6,10,17,22,30,31,33,36]
Taksa_sun2 =[1,3,6,10,17,22,30]
Taksa_mon =[2,5,9,16,21,29,35,36]
Taksa_tue =[3,7,14,19,27,33,34,36]
Taksa_wed =[4,11,16,24,30,31,33,36]
Taksa_thu =[5,13,19,20,22,25,29,36]
Taksa_fri =[6,7,9,12,16,23,28,36]
cannabis = [1,2,3,4,5,24,26,28,30,32,34,36,54,56,58,60]
music =[1,5, 14, 18, 24, 27, 27, 36, 40, 43, 48]
music1 =[1,6, 15, 19, 25, 28, 28, 37, 41, 44, 49]
kaset=[1,3,7,13,16,21,29,36,41]
electron = [1,9,16,24,25,29,34,42]
f_mod = [1,3,6,11,19,23,26,33,34,42,51]
p_mod = [1,3,6,11,18,20,24,32,33,38,40,44,45,50]
euler =[2, 9, 10, 18, 20, 28, 29, 37, 39, 47, 51, 56]
pi = [7,14,21,27,34,41,46,53,60,64,71,78,81,88,95,97,104,111,112,119,126,148]
pix=[7,12,15,24,28,30,35,38,39,43,45,54,57,67,75,77,86,93,95,103,109,113]


# =======================================================
# Section 6: เริ่มทำการ backtest
# =======================================================
# เลือกช่วงเวลาที่เราจะทำการ backtest
z_start_date = datetime(2021,3,8,0,0)
z_end_date = datetime(2021,3,15,0,0)
roundamt=1

day_shift_range = 3  #เอาไว้ทดสอบผลของการเลื่อนวันเริ่ม backtest

for d in range(0,day_shift_range,1):
    start_date = z_start_date + timedelta(d)
    end_date = z_end_date + timedelta(d)

    hisdata1=crop_histdata(hisdata,start_date,end_date)
    print("cnt rows:",len(hisdata1.index))

    startt=hisdata1['open']
    closep=hisdata1['close']
    openprice=list(startt)
    closeprice=list(closep)

    start_position = round(2500/openprice[0],roundamt)
    print('open price first',openprice[0], 'with xrm amt:',start_position)
    #seedlist=[base,catalan,Fibo,Taksa_sun, Taksa_sun1,Taksa_wed,majornote,music,music1,cannabis,electron,f_mod,p_mod,euler,pix]
    seedlist=[base,Taksa_sun1,Taksa_wed,electron,f_mod,p_mod,euler,pix]

    for seed in seedlist:
        growseed = xgrowseed(seed)
        gaincash = getPerformance(closeprice,openprice,start_position,2500,growseed,roundamt)


