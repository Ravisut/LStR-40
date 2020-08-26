import callFuntionFutures
import ccxt

import time
import datetime

#Update while Loop
timeBegin = 0
while True:
    try:
        timeBegin = time.time()
        print(datetime.datetime.now().strftime('%H:%M'))

        callFuntionFutures.updatee()

        timeEnd = time.time()
        timeElapsed = timeEnd - timeBegin
        print(timeElapsed)
        # จบกระบวนการทั้งหมด 37 วิ แล้วเอา 60 - 37 = 23วิ ที่เหลือในการถ่วงเวลา
        # ทำให้ หน่วงเวลา 30 วิไม่ได้ เพราะ 1รอบใช้เวลา 37วิ
        time.sleep(60 - timeElapsed)  # ถ่วงเวลา 60  วินาที

    #เครดิตพี่นัท LazyTrader
    except ccxt.RequestTimeout as e:
        # recoverable error, do nothing and retry later
        print(type(e).__name__, str(e))
        time.sleep(30)  # 30 sec.
    except ccxt.DDoSProtection as e:
        # recoverable error, you might want to sleep a bit here and retry later
        print(type(e).__name__, str(e))
        time.sleep(30)  # 30 sec.
    except ccxt.ExchangeNotAvailable as e:
        # recoverable error, do nothing and retry later
        print(type(e).__name__, str(e))
        time.sleep(30)  # 30 sec.
    except ccxt.NetworkError as e:
        # do nothing and retry later...
        print(type(e).__name__, str(e))
        time.sleep(30)  # 30 sec.
    except Exception as e:
        # panic and halt the execution in case of any other error
        print(type(e).__name__, str(e))
        callFuntionFutures.LineNotify(e, 'error')  # ถ้า error ที่แก้ไม่ได้ ไลน์ไป แจ้งคนเขียน
        break
        # sys.exit()

