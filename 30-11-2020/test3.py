import numpy as np
import pandas as pd

#df = pd.DataFrame({'B': np.nan, 'C': [4, 5, 6]})

#df = pd.DataFrame({'B': np.arange(1,10,0.1), 'C': np.nan})


df3 = pd.DataFrame({'Zone': np.arange(0.2,0.6,0.001)
                   , 'UseZone': np.nan
                   , 'Exposure': 3
                   , 'MapTrigger': np.nan
                   , 'IDorderBuy': np.nan
                   , 'OpenPrice': np.nan
                   , 'AmountBuy': np.nan
                   , 'timecancelbuy': np.nan
                   , 'FilledBuy': np.nan
                   , 'feeBuy': np.nan
                   , 'ExposureBuy': np.nan
                   , 'NAV': np.nan
                   , 'TradeTrigger': np.nan
                   , 'IDorderSell': np.nan
                   , 'ClosePrice': np.nan
                   , 'AmountSell': np.nan
                   , 'timecancelsell': np.nan
                   , 'feeSell': np.nan
                   , 'LastClosePrice': np.nan
                   , 'Profit': np.nan
                   , 'round': np.nan
                })

#df.insert(loc=0, column='A', value=np.arange(len(df)))
#df['B'] = pd.Series(np.arange(1,10,0.1))

#df3.to_csv('C:/Users/HOME/file_name2.csv', index=False)
print(df3.to_string(index=False))