import callFuntionFutures

import time
import datetime

#Update while Loop
timeBegin = 0
while True:
    #try:
        timeBegin = time.time()
        print(datetime.datetime.now().strftime('%H:%M'))

        callFuntionFutures.updatee()

        timeEnd = time.time()
        timeElapsed = timeEnd - timeBegin
        time.sleep(60 - timeElapsed)  # ถ่วงเวลา 60  วินาที
    #except Exception as e:
    #    callFuntionFutures.LineNotify(e, 'error')  # ถ้า error ไลน์ไป แจ้งคนเขียน
    #    break