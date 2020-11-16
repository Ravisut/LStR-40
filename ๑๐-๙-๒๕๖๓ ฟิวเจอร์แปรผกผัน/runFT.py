import callFuntionFutures
import ccxt
import time
import datetime

#Update while Loop
timeBegin = 0
checkError = 0
sleeptime = 30 # ถ่วงเวลา 30-60  วินาที
while True:
    try:
        timeBegin = time.time()

        callFuntionFutures.updatee()

        timeEnd = time.time()
        timeElapsed = timeEnd - timeBegin
        print('เวลา'+str(datetime.datetime.now().strftime('%H:%M'))+' กระบวนการ 1 รอบใช้เวลา: '+str(int(timeElapsed))+' วินาที')
        # จบกระบวนการทั้งหมดใน callFuntionFutures ใช้ 37-51 วิ แล้วเอา 60 - 37 = 23วิ ที่เหลือในการถ่วงเวลา
        # ทำให้ หน่วงเวลา 30 วิไม่ได้ เพราะ 1รอบใช้เวลา 37วิ และ กระบวนการห้ามนานเกิน 60วิ
        time.sleep(sleeptime - timeElapsed)  # ถ่วงเวลา 30-60  วินาที

        if sleeptime == 180:
            sleeptime = 30

    #""" เครดิตพี่นัท LazyTrader """
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
        #print(str(e))
        print('Normal: ' + str(sleeptime))
        if 'sleep length must be non-negative' == str(e):
            sleeptime = 180 # 3 นาที
            print('except: ' + str(sleeptime))
            #checkError = checkError + 1
            time.sleep(30)  # 30 sec.
        else:
            # error เกิน 3 รอบให้หยุดโปรแกรม
            #if checkError == 3:
            callFuntionFutures.LineNotify(e, 'error')  # ถ้า error ที่แก้ไม่ได้ ไลน์ไป แจ้งคนเขียน
            break
            # sys.exit()




