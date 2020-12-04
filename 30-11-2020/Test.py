import ccxt
import pandas as pd
import math
import callFuntionFutures


subaccount = 'bot-test-bug'  # ถ้ามี ซับแอคเคอร์ของ FTX
exchange = ccxt.ftx({
        'apiKey': '**********',
        'secret': '**********',
        'enableRateLimit': True,
    })
if subaccount == "":
    print("This is Main Account")
else:
    exchange.headers = {
        'FTX-SUBACCOUNT': subaccount,
    }
test = 3

def distance(a, b):
    if (a == b):
        return 0
    elif (a < 0) and (b < 0) or (a > 0) and (b > 0):
        if (a < b):
            return (abs(abs(a) - abs(b)))
        else:
            return -(abs(abs(a) - abs(b)))
    else:
        return math.copysign((abs(a) + abs(b)),b)

if test == 1:
    info = callFuntionFutures.checkByIDoder(9468890183)
    print(info)

if test == 2:
    info = callFuntionFutures.re("XRP-PERP",'market','sell','xrp position to close')
    print(info)

if test == 3:
    my_trades = exchange.private_get_positions()
    print("\n=============my_trades=============")
    my_trades = pd.json_normalize(data=my_trades['result'])
    df_curr_trade = pd.DataFrame(my_trades,
                                 columns=['future', 'side', 'entryPrice', 'estimatedLiquidationPrice', 'size', 'cost',
                                          'unrealizedPnl', 'realizedPnl'])
    pd.set_option('display.width', 1000)
    pd.set_option('display.max_columns', 1000)
    print(df_curr_trade)
    print(my_trades)
    #1.274975


if test == 4:
    oderinfo = callFuntionFutures.OHLC("XRP-PERP", 3,'4h')
    oderinfo['Perc_Change'] = ((oderinfo['high'] - oderinfo['low']) / (oderinfo['low'] / 100))

    mean1hr3 = oderinfo["Perc_Change"].mean()
    cooldownTime = 0.6 * mean1hr3 * 100 * 60

    pd.set_option('display.max_columns', None)
    print(mean1hr3)
    print(cooldownTime)
    print(oderinfo)

if test == 5:
    balance = exchange.fetch_balance()
    Totalbtc = balance['BTC']['total']

    price = exchange.fetch_ticker('BTC/USD')
    last_price = price['last']
    average_price = price['bid']
    usdValue = last_price * Totalbtc
    usdValue3 = average_price * Totalbtc

    _usdValue2 = balance['info']['result'][0]
    df_balance = pd.DataFrame.from_dict(balance['info']['result']).set_index('coin')
    df_balance['free'] = df_balance.free.astype(float)
    usdValue2 = df_balance.loc['BTC']['usdValue']

    print(usdValue)
    print(usdValue2)
    print(price)

if test == 6:

    print(distance(-3,-6))  # -3
    print(distance(-3, 3))  #  6
    print(distance(-3, -1)) #  2
    print(distance(3,  1))  # -2
    print(distance(3, -3))  # -6
    print(distance(-2, 23))   #  25

def fetchTrades():
    fetchTrades = exchange.fetch_my_trades(symbol="XRP-PERP", since=None, limit=2000, params={})
    fetchTrades = pd.json_normalize(data=fetchTrades)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(fetchTrades)

#fetchTrades()


if test == 7:
    result = 'result'
    listAsset = 'coin'
    params = {'recvWindow': 50000}

    balance = exchange.fetch_balance(params)
    df_balance = pd.DataFrame.from_dict(balance['info'][result]).set_index(listAsset)
    df_balance['free'] = df_balance.free.astype(float)
    print(df_balance)
    print(df_balance.loc['USD']['free'])




