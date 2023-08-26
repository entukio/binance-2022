from tradingview_ta import TA_Handler, Interval, Exchange
#doc https://python-tradingview-ta.readthedocs.io/en/latest/usage.html

# BOT PLAN #

### part I ###   

# 1. CHECK BTC RECOMMENDATION #
# IF RECOMMENDATION IS STRONG ENOUGH: #
# 2. ENTER POSITION WITH X% STOP LOSS #
# 3. CHECK PRICE EVERY 5 SECONDS #
# 4. IF PRICE IS MOVING X% TO THE RIGHT DIRECTION -> MOVE STOP LOSS TO MINIMAL PROFIT TO COVER FEES #
# 5. IF STOP-LOSS NOT TRIGGERED, AND PRICE MOVES ANOTHER X% -> MOVE STOP LOSS. REPEAT UNTIL TRIGGERED


### part II ###

#Repeat the process after closed trade. 
#If position not opened, wait 5-10 minutes and repeat.


#getting TradingView Recommendation sygnal

btc = TA_Handler(
symbol="BTCBUSD",
screener="Crypto",
exchange="Binance",
interval=Interval.INTERVAL_1_MINUTE)

reco = btc.get_analysis().summary

#Setting the Trade Amount
def set_amount(x):
    amount = x
    precision = 5
    amt_str = "{:0.0{}f}".format(amount, precision)
    return amt_str

Trade_Amount = '' #<<<Fill in here

if reco['RECOMMENDATION'] == 'SELL':
    try: #Short()
    except: Exception as e:
        print(e)
        
elif reco['RECOMMENDATION'] == 'BUY':
    #Long()
else:
    print('No trade - NEUTRAL recommendation')

#funkcja do dodawania transakcji do bazy danych
def addtodb(df):
    if order['status'] == 'FILLED':
        df.to_sql('TV_transactions', engine, if_exists='append', index=False)

#Send order Function
def create_order(sidem,amount):
    order = client.create_margin_order(
        symbol='BTCBUSD',
        side=sidem,
        type=ORDER_TYPE_MARKET,
        #type=ORDER_TYPE_LIMIT,
        #timeInForce=TIME_IN_FORCE_GTC,
        #price='0.00001',
        quantity=amount

    #format danych
    df = transform(order)
    #dodanie transakcji do bazy danych
    addtodb(df)
    df = df.assign(Status=order['status'])
    df

#def Short():
    #1. borrow - NOTE: Funds must be moved priorly to the margin account!
    try:
        client.create_margin_loan(asset='BTC', amount=set_amount(Trade_Amount))
    except: Exception as e:
        print(e)
    
    #2. sell 
    try:
        create_order(SIDE_SELL,set_amount(Trade_Amount))
    except: Exception as e:
        print(e)
        
        #3. set stop-loss
        #4. monitor price
        #5. adjust stop loss
        #6. buy
        #7. repay

#def Long()
        #1. Buy
        #2. set stop-loss
        #3. monitor price
        #4. adjust stop loss
        #5. Sell

# # # #

symbols = ['ETHBUSD','XMRBUSD','BTCBUSD']

for symbol in symbols:
    output = TA_Handler(
        symbol=symbol,
        screener="Crypto",
        exchange="Binance",
        interval=Interval.INTERVAL_1_MINUTE)
    print('Symbol: '+symbol)
    print(output.get_analysis().summary)
