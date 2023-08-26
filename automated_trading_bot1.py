import pandas as pd
from binance import Client
from binance.enums import *
import sqlalchemy

apikey = 'key'
apise = 'se'
client = Client(apikey,apise)

client.get_system_status()
#checking system status. If 1, then maintenance

#General info about cross-margin account
info = client.get_margin_account()
#info
#pd.DataFrame(info)

#fund transfer
transaction = client.transfer_spot_to_margin(asset='BUSD', amount='20')
transaction

# is it borrowable?
client.get_margin_asset(asset='BTC')
#client.get_margin_symbol(symbol='BTCBUSD')

client.get_margin_price_index(symbol='BNBBUSD')

#Transactions DB
engine = sqlalchemy.create_engine('sqlite:///Transactions.db')

def transform(order):
    orddb = {'Pair':order['symbol'],
            'OrderID':order['orderId'],
            'Time':order['transactTime'],
             'Asset_1':order['executedQty'],
             'Asset_2':order['cummulativeQuoteQty'],
             'Type':order['type']+' - '+order['side'],
             'Price':order['fills'][0]['price'],
             'Fee':order['fills'][0]['commission'],
             'Fee-asset':order['fills'][0]['commissionAsset'], 
             'Fee-BUSD':''
            }

    if orddb['Fee-asset'] == 'BNB':
        bnb = client.get_margin_price_index(symbol='BNBBUSD')
        orddb['Fee-BUSD'] = "{:.5f}".format(float(orddb['Fee'])*float(bnb['price']))
    elif orddb['Fee-asset'] == 'BUSD':
        orddb['Fee-BUSD'] =orddb['Fee']

    df = pd.DataFrame([orddb])
    df.Time = pd.to_datetime(df.Time, unit='ms')
    return df

#funkcja do dodawania transakcji do bazy danych
def addtodb(df):
    if order['status'] == 'FILLED':
        df.to_sql('Transactions', engine, if_exists='append', index=False)

  #setting amount
def set_amount(x):
    amount = x
    precision = 5
    amt_str = "{:0.0{}}".format(amount, precision)
    return amt_str

set_amount(0.00099)

#margin order

order = client.create_margin_order(
    symbol='BTCBUSD',
    side=SIDE_SELL,
    type=ORDER_TYPE_MARKET,
    #type=ORDER_TYPE_LIMIT,
    #timeInForce=TIME_IN_FORCE_GTC,
    #price='0.00001',
    quantity='0.00099')

#format danych
#df = transform(order)
#dodanie transakcji do bazy danych
#addtodb(df)
#df = df.assign(Status=order['status'])
#df

client.get_open_margin_orders(symbol='BTCBUSD')

client.get_max_margin_transfer(asset='BUSD')

#Borrow
client.create_margin_loan(asset='BTC', amount='0.00099')

#Repay
#client.repay_margin_loan(asset='BTC', amount='0.0001')

#get loan details
client.get_margin_loan_details(asset='BTC', txId='108589377396')

#get repay details
#client.get_margin_repay_details(asset='BTC', txId='100001')

def getminutedata(symbol,interval,lookback):
    #https://python-binance.readthedocs.io/en/latest/market_data.html#id7
    frame = pd.DataFrame(client.get_historical_klines(symbol,interval,lookback+' ago UTC'))
    frame = frame.iloc[:,[0,1,2,3,4,5,8]]
    frame.columns = ['Time','Open','High','Low','Close','Volume','Trades']
    frame = frame.set_index('Time')
    frame.index = pd.to_datetime(frame.index, unit = 'ms')
    frame = frame.astype(float)
    return frame

Pricegrid = getminutedata('BTCBUSD','1m','30m')

Pricegrid.Close.plot()

#strategy:
#buy if asset fell by more than 0.2% within the last 30 mins
#sell if asset rises by more than 0.15% of falls by 0.15%

def strategytest(symbol, qty, entried=False):
    df = getminutedata(symbol, '1m', '30m')
    cumulret = (df.Open.pct_change() +1).cumprod() - 1
    if not entried:
        if cumulret[-1] < -0.002:
            order = client.create_order(symbol=symbol,
                                       side='BUY',
                                       type='MARKET',
                                       quantity=qty)
            print(order)
            entried=True
        else:
            print('No trade has been executed')
    if entried:
      while True:
        df = getminutedata(symbol,'1m','30m')
        sincebuy = df.loc[df.index > pd.to_datetime(order['transactTime'], unit='ms')]
        if len(sincebuy) > 0:
            sincebuyret = (sincebuy.Open.pct_change() +1).cumprod() - 1
            if sincebuyret[-1] > 0.0015 or sincebuyret[-1] < 0.0015:
                order = client.create_order(symbol=symbol,
                                           side='SELL',
                                           type='MARKET',
                                           quantity=qty)
                print(order)
                break

strategytest('BTCBUSD',0.0004)

