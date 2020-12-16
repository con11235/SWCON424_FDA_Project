import pandas as pd
import numpy as np
import cvxpy as cp
from datetime import datetime, timedelta, date
import pandas_datareader.data as web
from dateutil.relativedelta import relativedelta
import statsmodels.api as sm
import os, random
from sklearn.preprocessing import MinMaxScaler

from data import *

np.set_printoptions(suppress = True)

today = datetime(2020,12,16)
allassetfilename = 'all_asset_'+today.strftime('%Y-%m-%d')+'.csv'
if not os.path.isfile(allassetfilename):
  print(allassetfilename)
  import FinanceDataReader as fdr
  df_spx = fdr.StockListing('NASDAQ')
  all_asset = df_spx['Symbol'].tolist()
  all_data = web.get_data_yahoo(all_asset,start='2000-01-01', end=today)['Adj Close']
  all_data.to_csv(allassetfilename) 

all_df = pd.read_csv(allassetfilename)
all_df['Date'] = all_df.Date.apply(lambda x: datetime.strptime(x, '%Y-%m-%d'))
all_df.set_index('Date',inplace=True)

if not os.path.isfile('beta.csv'):
  def cal_beta(asset_name):
    reg_df = ret_df.copy()[[asset_name, 'S&P500']].resample('M').last().pct_change().dropna(axis=0)
    Y = reg_df[asset_name]
    X = sm.add_constant(reg_df['S&P500'])
    model = sm.OLS(Y, X)
    results = model.fit()
    return results.params['S&P500']
  def time_varying_beta(asset_name, alpha):
    reg_df = ret_df.copy()[[asset_name, 'S&P500']].resample('M').last().pct_change().dropna(axis=0)
    lambdas = [alpha**(i-1) for i in range(len(reg_df), 0, -1)]
    var = np.sum(lambdas*(reg_df['S&P500']**2)) * (1-alpha)
    cov = np.sum(reg_df['S&P500']*reg_df[asset_name]*lambdas) * (1-alpha)

    return cov/var
  mpfo = web.get_data_yahoo(['^GSPC'], start='2010-01-01', end='2020-10-30')['Adj Close'].rename(columns={'^GSPC':'S&P500'})
  topn = NASDAQ_LIST.head(1000)['Symbol'].values
  ret_df = all_df.copy()
  ret_df['S&P500'] = mpfo['S&P500']
  ret_df = ret_df.loc['2015-01-01':]

  beta = dict()
  for col in topn:
    try:
      #beta[col] = cal_beta(col)
      beta[col] = time_varying_beta(col, 0.975)
    except:
      pass
  top_asset_beta = pd.DataFrame({'asset':beta.keys(),
                               'beta':beta.values()}).merge(NASDAQ_LIST[['Symbol', 'Name']], left_on='asset', right_on='Symbol', how='left')[['Symbol', 'Name', 'beta']]
  top_asset_beta.to_csv('beta.csv')
top_asset_beta = pd.read_csv('beta.csv')

# [dd,NASDAQ_DICT[dd],date,tra,trv,trt,STOCK_HAVE[dd]]
def get_total_profit(data):
  result = 0

  for trade in data:
    if trade[5] == 'buy':
      result += (all_df[trade[0]][today] - trade[4])*trade[3]
    else:
      result -= (all_df[trade[0]][today] - trade[4])*trade[3]
  return result

def get_monthly_return(data):
  monst = today - relativedelta(months=1)
  stock_have_st = dict()
  result = 0
  for trade in data:
    if datetime(int(trade[2][:4]),int(trade[2][5:7]),int(trade[2][8:])) < monst:
      stock_have_st[trade[0]] = trade[6]
    else:
      if trade[5] == 'buy':
        result += (all_df[trade[0]][today] - trade[4])*trade[3]
      else:
        result -= (all_df[trade[0]][today] - trade[4])*trade[3]
  for key in stock_have_st.keys():
    result += (all_df[key][today] - all_df[key][monst])*stock_have_st[key]
  return result

def get_donut_data(stock_have):
  return [stock_have[k]*all_df[k][today] for k in stock_have.keys()]
  

def get_realized_profit(data):
  stock_trade = dict()
  for trade in data:
    if trade[0] not in stock_trade:
      stock_trade[trade[0]] = [0,0,0,0]
    if trade[5] == "buy":
      stock_trade[trade[0]][0] = stock_trade[trade[0]][0]+trade[3]*trade[4]
      stock_trade[trade[0]][1] = stock_trade[trade[0]][1]+trade[3]
    else:
      stock_trade[trade[0]][2] = stock_trade[trade[0]][2]+trade[3]*trade[4]
      stock_trade[trade[0]][3] = stock_trade[trade[0]][3]+trade[3]
  result = 0
  for k in stock_trade:
    if stock_trade[k][1] == 0:
      A = 0
    else:
      A = (stock_trade[k][0]/stock_trade[k][1])
    if stock_trade[k][3] == 0:
      B = 0
    else:
      B = (stock_trade[k][2]/stock_trade[k][3])
    result+=(A-B)*(stock_trade[k][1]+stock_trade[k][3])
  return result

ff3 = web.DataReader('F-F_Research_Data_Factors_daily', 'famafrench', start='2010-01-01', end='2020-11-01')
ff3 = ff3[0]/100

def regression(df,symbols):
  temp = pd.DataFrame()
  for sym in symbols:
    Y = df[sym]-df['RF']
    X = sm.add_constant(df[['Mkt-RF', 'SMB', 'HML']])
    model = sm.OLS(Y, X)
    results = model.fit()
    temp[sym] = results.params
  
  return temp.iloc[1:,:]

def mv_opt(data,cons = 'none',nsh = False,ret_target = None,inputs=[]):
  print(inputs)
  n = len(data.T)   # asset number
  W = cp.Variable(n)  # weight of assets
  R = data.mean()*252
  C = data.cov()*252
  solver = cp.ECOS
  symbols = data.columns.tolist()
  constraints = [cp.sum(W) == 1]
  if ret_target != None:
    ret_gvm = np.dot(R.T, mv_opt(data)/100)
    ret_target = np.round(ret_gvm,2) + ret_target
  else:
    ret_target = 0
  constraints.append(W @ R >= ret_target)
  if 'cala' == cons:
    print('cala')
    objective = cp.Minimize(cp.quad_form(W, C)+inputs*cp.norm(W,1))
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS)
    return W.value.round(6)*100
  if 'cael' == cons:
    print('cael')
    objective = cp.Minimize(cp.quad_form(W, C)+inputs[0]*cp.norm(W,1)+inputs[1]*(cp.norm(W,2)**2))
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS)
    return W.value.round(6)*100
  if 'trco' == cons:
    if inputs[0] == None:
      inputs[0]=np.ones(n)/n
    if inputs[1] == None:
      inputs[1]=np.zeros(n) 
    objective = cp.Maximize((W@R*inputs[2])-cp.quad_form(W, C)-inputs[1]@cp.abs(W-inputs[0]))
    problem = cp.Problem(objective, constraints)
    problem.solve(solver=cp.ECOS)
    return W.value.round(6)*100
  if nsh:
    constraints.append(W >= 0)
  if 'alre' == cons:
    for line in inputs:
      Matrix = [0 for i in range(n)]
      temp = [symbols.index(i) for i in line[2]]
      for i in temp:
        Matrix[i] = 1 ## 제약 대상인 weight만 1로 남긴다. => sum(W @ Matrix)으로 H, L 바운드 설정
      L = line[0]
      H = line[1]
      if (L!= None) & (H!= None): # 둘 다 있다. 
        constraints.append(cp.sum(W @ Matrix) >= L)        
        constraints.append(cp.sum(W @ Matrix) <= H)
      elif L != None: # Low bound만 있다. 
        constraints.append(cp.sum(W @ Matrix) >= L)        
      elif H != None: # High bound만 있다. 
        constraints.append(cp.sum(W @ Matrix) <= H) 
  if 'card'==cons:
    DELTA = cp.Variable(n, boolean=True) # i번째 asset 선택할지 이진변수
    # 공통 제약
    constraints.append(cp.sum(DELTA) <= inputs) # 이진변수 다 더하면 max_asset보다 작거나 같다
    # case 제약
    if nsh:
      constraints.append(W <= DELTA) # 공매도 없는 경우
    else:
      M = 10**4
      constraints += [W >= -M*DELTA, # 공매도 있는 경우
                      W <= M*DELTA] # 공매도 있는 경우
    solver = 'ECOS_BB'
  if 'rifc' == cons:
    print('rifc')
    fama = data.copy()
    for a in ff3.columns:
      fama[a] = ff3[a]
    beta = regression(fama, symbols)
    constraints.append(beta.values @ W <= inputs)
  if 'trov-each' == cons:
    if inputs[0] is None:
      inputs[0] = np.ones(n)/n
    if inputs[1] is None:
      inputs[1] = np.zeros(n) 
    constraints.append(cp.abs(W-inputs[0]) <= inputs[1])
    # print('The last rebalanced weight :', W0)
  if 'trov-sum' == cons:
    if inputs[0] is None:
      inputs[0] = np.ones(n)/n
    if inputs[1] is None:
      inputs[1] = 0
    constraints.append(cp.sum(cp.abs(W-inputs[0])) <= inputs[1])   
  objective = cp.Minimize(cp.quad_form(W, C))
  problem = cp.Problem(objective, constraints)
  problem.solve(solver=solver)
  return W.value.round(6)*100

def timestr_to_datetime(i,b):
  if b == 'D':
    return timedelta(days=i)
  elif b == 'W':
    return timedelta(weeks=i)
  elif b == 'M':
    return relativedelta(months=i)
  elif b == 'Y':
    return relativedelta(years=i)


def data_for_mvopt(symbols,st,en):
    data = all_df[symbols]
    df = data[st:en]
    return df.pct_change().dropna()




def backtest(symbols, st, en, ut,lb, rb,dropna=True,cons = 'none',nsh = False,ret_target = None,inputs=[]):
  def data_by_dates():
    data = all_df[symbols]
    df = pd.DataFrame(columns = symbols)
    date = st-lb
    while date < en:
        df.loc[data[date:].index[0]] = data[date:].values[0]
        date += ut
    rb_date = []
    date = st
    while date < en:
        rb_date.append(data[date:].index[0])
        date += rb
    return df, rb_date
  df, rb_date = data_by_dates()
  df_ret = df.pct_change().dropna()
  
  col = [i+'_amt' for i in symbols]
  col.append('total_amt')
  col.append('portfolio_ret')
  col+= [i+'_weight' for i in symbols]
  result = pd.DataFrame(columns = col)
  T_amt = 100

  for index, row in df.iterrows():
    if st <= index:
      if index in rb_date:
        weight = mv_opt(df_ret[index-lb:index],cons = cons,nsh = nsh,ret_target = ret_target,inputs=inputs)
      amt = (df_ret[index:index]+1)*weight*T_amt/100
      for i in range(len(symbols)):
        s = symbols[i]
        result.loc[index,s+'_amt'] = amt[s].values[0]
        result.loc[index,s+'_weight'] = weight[i]
      T_amt_ = T_amt
      T_amt = amt.sum(axis = 1).values[0]
      result.loc[index,'total_amt'] = T_amt
      result.loc[index,'portfolio_ret'] = T_amt/T_amt_ - 1
  if dropna == True:
    return result.loc[:,result.eq(0).sum(axis=0) != len(result)]
  return result



def EWMA(df, asset):
  '''
  *input*
  df : asset 전체 다 있는 전체 데이터 
  asset : asset symbol 하나씩    
  *output*
  pred_price : 월 말일 price 값 딱 하나. 
                만약2020-10-30까지가 우리가 사용할 데이터이면, 11월 30일의 price 예측 값. 
  pred_ret : 한 달 return
              만약2020-10-30까지가 우리가 사용할 데이터이면, 1
              1월 30일의 price 예측 값과 10월 30일의 실제 price를 이용해서 구한 return     '''
  monthly_price = df[:today][asset].resample('M').mean() # 매달 평균 값
  mean = monthly_price.iloc[-1]    
  pred_price = monthly_price.ewm(0.9).mean().iloc[-1] # 파라미터 0.9는 대략 최근 10개 정도의 시계열 값을 평균낸 것에 근사함. 1/(1-0.9) 이런식으로 계산 가능.
  pred_ret = (pred_price - mean)/mean
    
  return pred_price, pred_ret


ret_list = []
for i,v in top_asset_beta.iterrows():
  try:
    amt,ret = EWMA(all_df,v[1])
    ret_list.append((ret*100).round(2))
  except:
    ret_list.append('Nan')
top_asset_beta['return'] = ret_list

EWMA_DATA = top_asset_beta

SNP500 = pd.read_csv('sp500_monthly.csv')
SNP500['sp_ret'] = SNP500['Adj Close'].pct_change()

def get_mdd(arr_v):
    """
    MDD(Maximum Draw-Down)
    :return: (mdd rate)
    """
#     arr_v = np.array(x)
    peak_lower = np.argmax(np.maximum.accumulate(arr_v) - arr_v)
    peak_upper = np.argmax(arr_v[:peak_lower])
    return (arr_v[peak_lower] - arr_v[peak_upper]) / arr_v[peak_upper]
