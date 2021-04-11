import ccxt
import time
import datetime
import division as di
import GoogleSheet as gs
import traceback
import sys

from gspread_dataframe import set_with_dataframe

"""presskey = person = input('Press1 checklist or Press2 run Bot : ')

if presskey == '1':
    #เช็คค่าตัวแปรต่างๆก่อนรันบอทจริง
    callFuntionFutures.Setup_beforeTrade()

if presskey == '2':
"""
'''logging.basicConfig(filename='MainCallLog',
                        filemode='w',
                        format='%(levelname)s %(asctime)s - %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.DEBUG)
logger = logging.getLogger()
'''

di.sector.create_sectorObject_list()
# Update while Loop
timeBegin = 0
#checkError = 0
sleeptime = 30  # ถ่วงเวลา 30 นาที
while True:
    try:
        timeBegin = time.time()

        ###### run ###################################
        di.sector.runDeck()
        #checkError = 0
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
            gs.sheet.Settingbot_df.loc['index_12','key_6'] = 'StopMode'
            gs.sheet.Settingbot_df.loc['index_12', 'key_8'] = str(type(e).__name__)
            # -----------บันทึก Google sheet--------------
            # บันทึกชีทหน้า Settingbot
            gs.sheet.getsave_to_sheet('Settingbot', 'Set')


            print(e)
            print(type(e).__name__,str(e) )
            print('-------ERROR--------------')
            error_class = e.__class__.__name__
            detail = e.args[0]
            tb = sys.exc_info()
            line_number = traceback.extract_tb(tb)[-1][1]
            info = '\n คลาส :' + str(error_class) +'\n' +'\n รายละเอียด :'+ str(detail) +'\n' +'\n บรรทัด :'+ str(line_number) +'\n' +'\n บรรทัด :'+ str(e) +'\n'

            di.sector.LineNotify(info, 'error')  # ถ้า error ที่แก้ไม่ได้ ไลน์ไป แจ้งคนเขียน
            # sys.exit()'''