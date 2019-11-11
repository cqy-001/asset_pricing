from WindPy import *
import numpy as np
import pandas as pd
import statsmodels.api as sm

w.start()
days = w.tdays("2015-01-01", "2017-12-31", "Period=M")
day_list = [x.strftime('%Y-%m-%d') for x in days.Times]

# 求某月的因子值
def Areturn(i = 0):
    breakpoint = day_list[i]
    #取中证800
    stock = w.wset("sectorconstituent", "date=" + breakpoint + ";windcode=000906.SH")
    pool = stock.Data[1]  # list 可取行不可取列
    ##SMB股票选取市场规模因子
    ME = w.wss(pool, "ev","unit=1;tradeDate="+breakpoint)
    ME50 = np.percentile(ME.Data, 50)
    idx1 = np.where(ME.Data[0]<=ME50)[0].tolist()
    SM = [ME.Codes[x] for x in idx1]
    idx2 = np.where(ME.Data[0] > ME50)[0].tolist()
    BM = [ME.Codes[x] for x in idx2]
    ##HML股票选取市账率因子
    PB = w.wss(pool, "pb_lf", "unit=1;tradeDate="+breakpoint)
    BP = [1/x for x in PB.Data[0]]
    BP30 = np.percentile(BP, 30)
    BP70 = np.percentile(BP, 70)
    idx3 = np.where(BP <= BP30)[0].tolist()
    LM = [PB.Codes[x] for x in idx3]
    idx4 = np.where(BP > BP70)[0].tolist()
    HM = [PB.Codes[x] for x in idx4]

    tickerlist = [SM,BM,LM,HM]
    tickername = ['SM','BM','LM','HM']
    #取出选择股票计算收益率
    cfrm = pd.DataFrame()
    for n,j in zip(tickername,tickerlist):
        a = w.wss(j, "pre_close,close","tradeDate="+breakpoint+";priceAdj=F;cycle=M")
        a_pd = pd.DataFrame(a.Data,index=a.Fields,columns=a.Codes).T
        r = (np.log(a_pd['CLOSE'])-np.log(a_pd['PRE_CLOSE'])).mean()
        cfrm[n] = [r]
    return cfrm


Returnfrm = pd.DataFrame()
k = 0
for t in range(len(day_list)):
    x = Areturn(t)
    Returnfrm = pd.concat([Returnfrm,x])
    k = k+1
    print(k)
Returnfrm.index = day_list

##计算每月的因子大小
EME = Returnfrm['SM'] - Returnfrm['BM']
EBP = Returnfrm['HM'] - Returnfrm['LM']

##计算市场收益率
p_mkt = w.wsd("000906.SH", "pre_close,close", "2015-01-01", "2017-12-31", "Period=M;PriceAdj=F")
p_mkt_pd = pd.DataFrame(p_mkt.Data,index=p_mkt.Fields,columns=p_mkt.Times).T
r_mkt = (np.log(p_mkt_pd['CLOSE'])-np.log(p_mkt_pd['PRE_CLOSE']))
r_mkt.index = day_list

'''
rf = w.edb("M0041653", "2015-01-01", "2017-12-31","Fill=Previous")
rf_s = pd.Series(rf.Data[0], index=rf.Times) * 0.01/12
mkt_rf = pd.concat([r_mkt, rf_s], axis=1, join='inner')
mkt_rf.index = day_list # 很重要
r_mkt_ex = mkt_rf.iloc[:, 0] - mkt_rf.iloc[:, 1]
'''
r_mkt_ex = r_mkt

# 低市值组合超额收益
#r_ex = Returnfrm['SM'] - mkt_rf.iloc[:, 1]
r_ex = Returnfrm['SM']
choose = pd.concat([r_ex, r_mkt_ex, EME, EBP], axis=1)

X = choose.iloc[:, 1:]
Y = choose.iloc[:, 0]
X = sm.add_constant(X)
model = sm.OLS(Y, X)
results = model.fit()
print(results.summary())












