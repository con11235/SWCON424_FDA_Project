import pandas as pd



NASDAQ_LIST = pd.read_csv('NasdaqList.csv')

NASDAQ_DICT = {}
for i, v in NASDAQ_LIST.iterrows():
    NASDAQ_DICT[v[1]] = v[2]+" ("+v[1]+")"
