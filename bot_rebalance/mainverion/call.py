import ccxt
import time
import datetime
import rebalance as re
from gspread_dataframe import set_with_dataframe


re.bot.create_sectorObject_list()
# Update while Loop
timeBegin = 0
checkError = 0
sleeptime = 60  # ถ่วงเวลา 30-60  วินาที
while True:
        try:
                timeBegin = time.time()

                ###### run ###################################
                re.bot.runbot()

                checkError = 0
                ###############################################

                timeEnd = time.time()
                timeElapsed = timeEnd - timeBegin
                print('เวลา' + str(datetime.datetime.now().strftime('%H:%M')) + ' กระบวนการ 1 รอบใช้เวลา: ' + str(int(timeElapsed)) + ' วินาที')
                #print('time ' + str(datetime.datetime.now().strftime('%H:%M')) + ' processing time per round : ' + str(int(timeElapsed)) + ' Secound')  # กระบวนการ 1 รอบใช้เวลา
                # จบกระบวนการทั้งหมดใน callFuntionFutures ใช้ 37-51 วิ แล้วเอา 60 - 37 = 23วิ ที่เหลือในการถ่วงเวลา
                # ทำให้ หน่วงเวลา 30 วิไม่ได้ เพราะ 1รอบใช้เวลา 37วิ และ กระบวนการห้ามนานเกิน 60วิ
                time.sleep(sleeptime - timeElapsed)  # ถ่วงเวลา 30-60  วินาที

                #if sleeptime == 300:
                #    sleeptime = 30

        # เครดิตพี่นัท LazyTrader
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
            #logger.exception(e)
            # panic and halt the execution in case of any other error
            if 'sleep length must be non-negative' == str(e) or 'ExchangeError' == str(type(e).__name__) or 'APIError' == str(type(e).__name__) or 'ConnectionError' == str(type(e).__name__) or 'ReadTimeout' == str(type(e).__name__):
                #sleeptime = 300  # 5 นาที
                #print('except sleeptime : ' + str(sleeptime))
                print('Got error')
                time.sleep(30)  # 30 sec.
            else:
                print('stop bot')
                print(e)
                print(type(e).__name__,str(e) )
                print('-------ERROR--------------')
                break
                # sys.exit()'''