import ccxt
import requests
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
from statsmodels.tsa.stattools import adfuller
from datetime import datetime, timedelta

binance = ccxt.binanceusdm({'options': {'enableRateLimit': True}})

def initialize_dates():
    '''Funtion to fetch the past x number of days from the current day'''
    today = datetime.today().date()

    fivedays = today - timedelta(days=5)
    sevendays = today - timedelta(days=7)
    thirtydays = today - timedelta(days=30)
    threemonths = today - timedelta(days=91)
    year = today - timedelta(days=365)

    fivedays = fivedays.strftime("%Y-%m-%d")
    sevendays = sevendays.strftime("%Y-%m-%d")
    thirtydays = thirtydays.strftime("%Y-%m-%d")
    threemonths = threemonths.strftime("%Y-%m-%d")
    oneyear = year.strftime("%Y-%m-%d")
    return fivedays, sevendays, thirtydays, threemonths, oneyear

def initialize_symbols():
    symbols_url = "https://fapi.binance.com/fapi/v1/ticker/price"
    symbols_data = requests.get(symbols_url).json()
    symbols_df = pd.DataFrame(symbols_data)
    symbols_df = symbols_df[symbols_df["symbol"].str.contains("USDT")]
    symbols = list(symbols_df["symbol"])
    symbols = list(filter(lambda x: x.endswith(("USDT")), symbols))
    return symbols

def get_singleticker_data(ticker_symbol, t_interval, period):
    '''
    Function to fetch historical closing prices of futures ticker
    symbol: futures ticker symbol as string
    interval: timeframe as string '5m', '1h','1d'''
    symbol = ticker_symbol
    interval = t_interval
    dataperiod = period
    
    data = pd.DataFrame(binance.fetch_ohlcv( symbol, interval, limit=1500))
    data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    data['Date'] = pd.to_datetime(data['Date'], unit='ms') + pd.Timedelta(hours=2)
    data = data.set_index('Date')
    data = data.drop(['Open', 'High', 'Low', 'Volume'], axis=1)
    data.rename(columns={'Close': f'{symbol}'}, inplace=True)
    data = data.loc[dataperiod:]

    return data

def get_allticker_data(t_interval, period):
    timeinterval = t_interval
    dataperiod = period
    dfs=[]

    for symbol in symbols:
        dfs.append(get_singleticker_data(symbol, timeinterval, dataperiod))

    data = pd.concat(dfs, axis=1)
    data = data.loc[period:]
    return data

def get_redundant_pairs(df):
    '''Get diagonal and lower triangular pairs of correlation matrix'''
    pairs_to_drop = set()
    cols = df.columns
    for i in range(0, df.shape[1]):
        for j in range(0, i+1):
            pairs_to_drop.add((cols[i], cols[j]))
    return pairs_to_drop

def get_top_abs_correlations(df, n):
    au_corr = df.corr().abs().unstack()
    labels_to_drop = get_redundant_pairs(df)
    au_corr = au_corr.drop(labels=labels_to_drop).sort_values(ascending=False)
    return au_corr[0:n]

def perform_test(time,n):
    '''time: timeframe, 5m,1h,4h,1d
    n: number of pairs to scan'''
    t = time

    pair_data = pd.read_csv('tickers_'+t+'.csv')
    data = pair_data.copy()
    data = data.set_index('Date')

    pair_numbers = n #select number of pairs to scan

    logretdf = np.log(data.pct_change()+1)
    data_corr = logretdf.corr()
    data = pd.DataFrame(get_top_abs_correlations(data_corr, pair_numbers)).reset_index()
    data = data.rename(columns= {'level_0': 's1','level_1': 's2', 0:'correlation'})

    coin_res = []
    adf_res = []

    for i,j in zip(data.s1,data.s2):

        symbol1 = i
        symbol2 = j
        x = pair_data[symbol1]
        y = pair_data[symbol2]
        df = pd.concat([x,y],axis=1)
        df =  df.dropna()
       # taillength  = min(len(x),len(y))
        result  = ts.coint(df[f'{symbol1}'],df[f'{symbol2}'])[1]<0.05
        coin_res.append(result)
        model = sm.OLS(df[f'{symbol1}'],df[f'{symbol2}'])
        model = model.fit()
        spread = y - model.params[0]*x
        spread = spread.dropna()
        adf = adfuller(spread, maxlag =1)
        result = adf[0] < -3.504
        adf_res.append(result)

    data['cointegration_test'] = coin_res
    data['adf_test'] = adf_res
    return data


symbols = initialize_symbols()
fivedays, sevendays, thirtydays, threemonths, year = initialize_dates()