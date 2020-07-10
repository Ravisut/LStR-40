import ccxt
import pandas as pd

exchange = ccxt.kucoin({
    'apiKey': '********',
    'secret': '************',
    'password': '********',
    'enableRateLimit': True,
})

symbol = 'BNB/USDT'
typee = 'limit'  # or 'market'
side = 'sell'  # or 'buy'
amount = 0.001
price = 20.00  # or None

params = {
    'recvWindow': 50000
}

#order = exchange.fetch_my_trades(symbol ='BNB/USDT', params = params)
#order = exchange.create_order(symbol, typee, side, amount, price, params)
#print(type(order))
#print(order['id'])
#print(order)


#balance = exchange.fetch_balance(params)
#df_balance = pd.DataFrame.from_dict(balance['info']['data']).set_index(['type', 'currency'])
#df_balance['balance'] = df_balance.balance.astype(float)
#print(df_balance.filter(like='trade', axis=0).loc[df_balance.balance > 0])




