import ccxt       # Import lib ccxt เพื่อติดต่อกับ API ของโบรก
import pandas as pd       # จะต้องมีการเรียกใช้ Lib Pandas


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
hisdata.to_csv('dataset.csv', index=False)