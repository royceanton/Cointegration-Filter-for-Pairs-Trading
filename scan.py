import pairpy as pp

def scan(t,n):
  '''t: time example: 1h 4h 1d
  n: numper of pairs to scan'''
  data = pp.perform_test(t,n)
  data = data[(data['cointegration_test']==True) & (data['adf_test']== True)]
  return print(data)
