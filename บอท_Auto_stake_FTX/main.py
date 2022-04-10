import time
import datetime
from client import FtxClient
from staking import auto_staking
from settings import API, SECRET, SUBACCOUNT

client = FtxClient(api_key=API,
                   api_secret=SECRET,
                   subaccount_name=SUBACCOUNT)

timeBegin = 0
sleeptime = 60  # ถ่วงเวลา 60  วินาที
while True:
        timeBegin = time.time()

        ###### run ###################################
        auto_staking(client)

        ###############################################

        timeEnd = time.time()
        timeElapsed = timeEnd - timeBegin
        print('เวลา' + str(datetime.datetime.now().strftime('%H:%M')) + ' กระบวนการ 1 รอบใช้เวลา: ' + str(
            int(timeElapsed)) + ' วินาที')
        # print('time ' + str(datetime.datetime.now().strftime('%H:%M')) + ' processing time per round : ' + str(int(timeElapsed)) + ' Secound')  # กระบวนการ 1 รอบใช้เวลา
        # จบกระบวนการทั้งหมดใน callFuntionFutures ใช้ 37-51 วิ แล้วเอา 60 - 37 = 23วิ ที่เหลือในการถ่วงเวลา
        # ทำให้ หน่วงเวลา 30 วิไม่ได้ เพราะ 1รอบใช้เวลา 37วิ และ กระบวนการห้ามนานเกิน 60วิ
        time.sleep(sleeptime - timeElapsed)  # ถ่วงเวลา 30-60  วินาที
