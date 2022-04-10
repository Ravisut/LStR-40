from client import FtxClient
import decimal
from settings import COINS


def auto_staking(client: FtxClient) -> None:
    for coin in COINS:
        stake_coin(client, coin)


def stake_coin(client: FtxClient, coin: str) -> None:
    balance_coin = client.get_balance_coin(coin)
    if balance_coin is None:
        return
    total_balance = balance_coin['total']
    available_balance = balance_coin['free']
    print(str(coin)+' ฝาก : '+str(round(total_balance,8)))
    if available_balance > 0:
        print('ทำการอัดดอกเบี้ย'+ str(format(float(available_balance), 'f')))
        client.stakes(coin=coin, size=available_balance)
    else:
        print('ยังไม่ได้รับตอบแทน')

