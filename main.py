import pairpy as pp
import fetch
import scan

symbols = pp.initialize_symbols()
fivedays, sevendays, thirtydays, threemonths, year = pp.initialize_dates()

# timeinterval = '1h'
# lookback = thirtydays
# pair_numbers = 500

def run_nonagon(timeinterval,lookback,pair_numbers):
  fetch.fetch(timeinterval, lookback)
  scan.scan(timeinterval,pair_numbers)



run_nonagon('1h',thirtydays,500)