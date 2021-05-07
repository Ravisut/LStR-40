import datetime
from datetime import datetime,timedelta
import pandas as pd



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
    his_week = hisdata.loc[(hisdata['datex'] >= datetime.timestamp(start_date) * 1000) & (hisdata['datex'] < datetime.timestamp(end_date) * 1000)]
    return his_week


# ใช้สำหรับคำนวน performance ของการทำ rebalance
def getPerformance(closeprice, openprice, start_position, balanceusd, nmagic, nround):
    minpct = 1

    pos = start_position
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
        usdDiff = round(valueusd - balanceusd, 1) # ส่วนต่าง มูลค่า ที่ขาดๆเกินๆ
        perDiff = round(100 * usdDiff / balanceusd, 2) # ส่วนต่าง % ของ มูลค่า ที่ขาดๆเกินๆ

        i = i + 1
        if i in nmagic:
            fg_rebalance = True
        else:
            fg_rebalance = False

        if perDiff > minpct and fg_rebalance:
            itran = itran + 1
            sell_USD = usdDiff
            accu_sell_USD = round(sell_USD + accu_sell_USD, 1)
            accu_sell_XRP = round(round(usdDiff / x, nround) + accu_sell_XRP, nround)
            pos = round(balanceusd / x, nround)
            # print(i,'price:',x,' :value:', valueusd, '== DiffUS:',diffUSD, ' %pct:', perDiff, 'acce Sell:', accu_sell_USD, 'pos:',pos,'accu_sell_XRP:',accu_sell_XRP)
            avg_sell_price = round(accu_sell_USD / accu_sell_XRP, 4)
            #print('position size :', pos)
            print(accu_sell_XRP)
        elif perDiff < -1 * minpct and fg_rebalance:
            itran = itran + 1
            buy_USD = usdDiff
            accu_buy_USD = round(buy_USD + accu_buy_USD, 1)
            accu_buy_XRP = round(round(usdDiff / x, nround) + accu_buy_XRP, nround)
            pos = round(balanceusd / x, nround)
            # print(i,'price:',x,' :value:', valueusd, '== DiffUS:',diffUSD, ' %pct:', perDiff, 'acce Buy:', accu_buy_USD, 'pos:',pos,'accu_buy_XRP:',accu_buy_XRP)
            avg_buy_price = round(accu_buy_USD / accu_buy_XRP, 4)
            #print('position size :', pos)
            #print('2position size :', accu_buy_XRP)



        # match_XRP_amt = min(-accu_buy_XRP, accu_sell_XRP)
        # print ('match XRP amt',match_XRP_amt,'avg_buy_price',avg_buy_price,avg_sell_price,avg_sell_price-avg_buy_price )

    avg_buy_price = round(accu_buy_USD / accu_buy_XRP, 4)
    avg_sell_price = round(accu_sell_USD / accu_sell_XRP, 4)
    match_XRP_amt = min(-accu_buy_XRP, accu_sell_XRP)
    print((match_XRP_amt))
    #print(-accu_buy_XRP)
    #print(accu_sell_XRP)
    #print(match_XRP_amt)
    # print ('match XRP amt',match_XRP_amt)
    # print('avg_buy_price',avg_buy_price,avg_sell_price)
    # print('n transaction',itran)
    Cash_gen = (avg_sell_price - avg_buy_price) * accu_sell_XRP
    print('Cash Gen:', round(Cash_gen, 1))  # , 'n tran',itran )
    return Cash_gen



# =======================================================
# Section 4 :โหลดข้อมูลที่เรา save เก็บเอาไว้
# =======================================================
hisdata = pd.read_csv('dataset.csv')
hisdata.tail(10)


# =======================================================
# Section 5 : ชุดตัวเลขที่ ต้องการเอามาทำ backtest
# =======================================================
pi = [7,14,21,27,34,41,46,53,60,64,71,78,81,88,95,97,104,111,112,119,126,148]

# =======================================================
# Section 6: เริ่มทำการ backtest
# =======================================================
# เลือกช่วงเวลาที่เราจะทำการ backtest
z_start_date = datetime(2021,3,8,0,0)
z_end_date = datetime(2021,3,15,0,0)
roundamt=1

day_shift_range = 1  #เอาไว้ทดสอบผลของการเลื่อนวันเริ่ม backtest

for d in range(0,day_shift_range,1):
    start_date = z_start_date + timedelta(d)
    end_date = z_end_date + timedelta(d)
    print(start_date)

    hisdata1=crop_histdata(hisdata,start_date,end_date)
    print("count rows:",len(hisdata1.index))

    startt=hisdata1['open']
    closep=hisdata1['close']
    openprice=list(startt)
    closeprice=list(closep)

    start_position = round(2500/openprice[0],roundamt) # ต้องมี XRP มูลค่าเทียบเท่า เงินทุน คือ 2500 : 2500

    print('open price first',openprice[0], 'with xrp amont:',start_position)
    #seedlist=[base,catalan,Fibo,Taksa_sun, Taksa_sun1,Taksa_wed,majornote,music,music1,cannabis,electron,f_mod,p_mod,euler,pix,pi]


    growseed = xgrowseed(pi)
    gaincash = getPerformance(closeprice,openprice,start_position,2500,growseed,roundamt)
