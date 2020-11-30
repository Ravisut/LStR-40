import callFuntionFutures
import ccxt
import time
import datetime

presskey = person = input('Press1 checklist or Press2 run Bot : ')

if presskey == '1':
    #เช็คค่าตัวแปรต่างๆก่อนรันบอทจริง
    callFuntionFutures.Setup_beforeTrade()

if presskey == '2':

    # Update while Loop
    timeBegin = 0
    checkError = 0
    sleeptime = 30  # ถ่วงเวลา 30-60  วินาที
    while True:
        try:
            timeBegin = time.time()

            callFuntionFutures.updatee()

            timeEnd = time.time()
            timeElapsed = timeEnd - timeBegin
            print('เวลา' + str(datetime.datetime.now().strftime('%H:%M')) + ' กระบวนการ 1 รอบใช้เวลา: ' + str(
                int(timeElapsed)) + ' วินาที')
            # จบกระบวนการทั้งหมดใน callFuntionFutures ใช้ 37-51 วิ แล้วเอา 60 - 37 = 23วิ ที่เหลือในการถ่วงเวลา
            # ทำให้ หน่วงเวลา 30 วิไม่ได้ เพราะ 1รอบใช้เวลา 37วิ และ กระบวนการห้ามนานเกิน 60วิ
            time.sleep(sleeptime - timeElapsed)  # ถ่วงเวลา 30-60  วินาที

            if sleeptime == 300:
                sleeptime = 30

        # """ เครดิตพี่นัท LazyTrader """
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

            if 'sleep length must be non-negative' == str(e):
                print('Normal: ' + str(sleeptime))
                sleeptime = 300  # 5 นาที
                print('except sleeptime : ' + str(sleeptime))
                checkError = checkError + 1
                time.sleep(30)  # 30 sec.
            else:
                # error เกิน 3 รอบให้หยุดโปรแกรม
                if checkError == 3:
                    print('stop bot')
                    callFuntionFutures.LineNotify(e, 'error')  # ถ้า error ที่แก้ไม่ได้ ไลน์ไป แจ้งคนเขียน
                    break
                    # sys.exit()








