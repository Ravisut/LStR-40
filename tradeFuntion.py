import pandas as pd
import matplotlib.pyplot as plt

def whatFunction(df,Around,whatfution):
    if whatfution == 'percent':
        conditionToAdjust1 = df.loc[Around]['Value']
        conditionToAdjust2 = df.loc[Around]['Condition'] # ดึงเลข 2 ในชีทมา

        # Add dynamic % follow up ATR voltility
        atr30hours = conditionToAdjust2
        conditionToAdjust3 = (conditionToAdjust1 / 100) * conditionToAdjust2 # ตรวจดูว่า เกิน 2%ยัง
        return  conditionToAdjust3