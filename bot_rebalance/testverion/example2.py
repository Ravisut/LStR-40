import ccxt
import pandas as pd
import time


##############
def runTrade():
    ##############
    # @markdown เซตค่า API
    apiKey = ""  # @param {type:"string"}
    secret = ""  # @param {type:"string"}
    password = ""  # @param {type:"string"}
    Account_name_01 = ""  # @param {type:"string"}
    print("\n""#############################")
    # exchange detail
    exchange_01 = ccxt.ftx({
        'apiKey': apiKey, 'secret': secret, 'password': password, 'enableRateLimit': True
    })
    # Sub Account Check
    if Account_name_01 == "0":
        print("\n""Account 01 - This is Main Account", ': Broker - ', exchange_01)
    else:
        print("\n"'Account 01 - ', Account_name_01, ': Broker - ', exchange_01)
        exchange_01.headers = {
            'ftx-SUBACCOUNT': Account_name_01,
        }
    ##############
    # @markdown เซตค่า Asset
    Asset_Rebalance_01 = 'ETH/USDT'  # @param {type:"string"}
    currency_left_01 = 'ETH'  # @param {type:"string"}
    currency_right_01 = 'USDT'  # @param {type:"string"}
    # @markdown เซตค่า Rebalance
    Mark_Asset_Rebalance_Value = 400  # @param
    Mark_Cash_Rebalance_Value = 900  # @param
    Minimum_percent_diff = 2  # @param
    types = 'market'
    side_buy = 'buy'
    side_sell = 'sell'

    # @markdown เซตค่า ATR
    Indicator_TF = '1hn'  # @param {type:"string"}
    Indicator_Period = 13  # @param
    ATR_Multiple = 1  # @param

    ##############

    ohlcatr = exchange_01.fetch_ohlcv(Asset_Rebalance_01, timeframe=Indicator_TF, limit=Indicator_Period)
    ohlcatr_df = pd.DataFrame(ohlcatr, columns=['datetime', 'open', 'high', 'low', 'close', 'volume'])
    ohlcatr_df['datetime'] = pd.to_datetime(ohlcatr_df['datetime'], unit='ms')
    ohlcatr_df['HL'] = ohlcatr_df['high'] - ohlcatr_df['low']
    ohlcatr_df['HC'] = abs(ohlcatr_df['high'] - ohlcatr_df['close'].shift())
    ohlcatr_df['LC'] = abs(ohlcatr_df['low'] - ohlcatr_df['close'].shift())
    ohlcatr_df['TR'] = ohlcatr_df[['HL', 'HC', 'LC']].max(axis=1)
    ohlcatr_df['ATR'] = ohlcatr_df['TR'].rolling(Indicator_Period).mean()
    ohlcatr_df['SMA'] = ohlcatr_df['close'].rolling(Indicator_Period).mean()

    ##################
    get_ticker_asset_01 = exchange_01.fetch_ticker(Asset_Rebalance_01)
    Average_price_01 = (get_ticker_asset_01['bid'] + get_ticker_asset_01['ask']) / 2
    ATR_last_value_01 = ohlcatr_df['ATR'].sum()
    Volatility = ((ATR_last_value_01 * ATR_Multiple) / Average_price_01) * 100  # Volatility = 1ATR

    print('Asset Rebalance   = ', Asset_Rebalance_01)
    print('Average_price_01  = ', Average_price_01)
    print('ATR               = ', ATR_last_value_01)
    print('Volatility        = ', Volatility)
    ########################################
    Get_balance_01 = exchange_01.fetch_balance()
    USD_Value_01 = Get_balance_01[currency_right_01]['total']
    Asset_01_Value = Get_balance_01[currency_left_01]['total'] * Average_price_01
    Portfolio_Value = USD_Value_01 + Asset_01_Value
    Auto_Rebalance_Value = Mark_Asset_Rebalance_Value
    # asset ขั้นต่ำ ที่แปรผันตาม % ขั้นต่ำ เช่น 2% 400 คือ 8
    Minimum_Asset_01_Value_Diff = (Auto_Rebalance_Value * Minimum_percent_diff) / 100
    Volatility_Asset_01_Value_Diff = (Auto_Rebalance_Value * Volatility) / 100

    print("\n"'Auto_Rebalance_Value           = ', Auto_Rebalance_Value, currency_right_01)
    print('Minimum_Asset_01_Value_Diff    = ', Minimum_Asset_01_Value_Diff, currency_right_01, '/',Minimum_percent_diff, '%')
    print('Volatility_Asset_01_Value_Diff = ', Volatility_Asset_01_Value_Diff, currency_right_01, '/', Volatility, '%')

    Value_Buy_Asset_01 = Get_balance_01[currency_left_01]['total'] * get_ticker_asset_01['ask']
    Value_Sell_Asset_01 = Get_balance_01[currency_left_01]['total'] * get_ticker_asset_01['bid']
    Asset_01_Diff = Asset_01_Value - Auto_Rebalance_Value  # 1000-950 = 50
    Size_Order_Buy_01 = (Auto_Rebalance_Value - Value_Buy_Asset_01) / get_ticker_asset_01['ask']
    Size_Order_Sell_01 = (Value_Sell_Asset_01 - Auto_Rebalance_Value) / get_ticker_asset_01['bid']

    print("\n"'SUM_Portfolio_Value    = ', Portfolio_Value, currency_right_01)
    print('USD_Value_01           = ', USD_Value_01, currency_right_01)
    print("\n"'Auto_Rebalance_Value   = ', Auto_Rebalance_Value, currency_right_01)
    print('Asset_01_Value         = ', Asset_01_Value, currency_right_01)
    print('Asset_01_Diff          = ', Asset_01_Diff, currency_right_01)

    from datetime import datetime
    import pytz
    now = datetime.now()
    UTC_time = now.strftime("%H:%M:%S")
    tz_NY = pytz.timezone('Asia/Bangkok')
    datetime_NY = datetime.now(tz_NY)

    print("\n""UTC Time      = ", UTC_time)
    print("Bangkok Time  = ", datetime_NY.strftime("%H:%M:%S"))
    print("\n""#############################")
    ########################################
    if ATR_last_value_01 > 0 and Value_Buy_Asset_01 <= (Auto_Rebalance_Value - Minimum_Asset_01_Value_Diff) and Value_Buy_Asset_01 <= (
            Auto_Rebalance_Value - Volatility_Asset_01_Value_Diff):
        exchange_01.create_order(Asset_Rebalance_01, types, side_buy, Size_Order_Buy_01), print(
            "!!!!! rebalance BUY  Account 01 !!!!")
    elif ATR_last_value_01 > 0 and Value_Sell_Asset_01 >= (
            Auto_Rebalance_Value + Minimum_Asset_01_Value_Diff) and Value_Sell_Asset_01 >= (
            Auto_Rebalance_Value + Volatility_Asset_01_Value_Diff):
        exchange_01.create_order(Asset_Rebalance_01, types, side_sell, Size_Order_Sell_01), print(
            "!!!!! rebalance SELL Account 01 !!!!")
    else:
        print("\n" "!!!!!! not time to rebalance !!!!!")


# @markdown เซตค่า Delay_a_Time
Delay_a_Time = 5  # @param # Delay for 1 minute (60 seconds).

while True:
    print("Delay a Time.")
    time.sleep(Delay_a_Time)  # Delay for 1 minute (60 seconds).
    runTrade()


