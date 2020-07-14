import ccxt
import pandas as pd
import callFuntionFutures

test = 1

if test == 1:
    oderinfo = callFuntionFutures.OHLC("XRP-PERP",3)
    oderinfo['Perc_Change'] = ((oderinfo['high']-oderinfo['low']) / (oderinfo['low']/100))

    mean1hr3 = oderinfo["Perc_Change"].mean()
    cooldownTime  = 0.6*mean1hr3*100*60

    pd.set_option('display.max_columns', None)
    print(mean1hr3)
    print(cooldownTime)
    print(oderinfo)

if test == 2:
    info = callFuntionFutures.checkByIDoder('6500462660')
    print(info)






