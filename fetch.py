import pairpy as pp

symbols = pp.initialize_symbols()
fivedays, sevendays, thirtydays, threemonths, year = pp.initialize_dates()

def fetch(t,d):
  '''t: timeframe 
  d: days to look back'''
  
  data = pp.get_allticker_data('1h',thirtydays)
  data.to_csv('tickers_1h.csv')
