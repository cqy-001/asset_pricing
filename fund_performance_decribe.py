from WindPy import *
import numpy as np
import statsmodels.api as sm

w.start()
start_date, end_date = "2018-11-01", "2019-10-31"
fund = w.wsd("110022.OF", "NAV_adj_return1", start_date, end_date, "Fill=Previous;PriceAdj=F")   #易方达消费行业
r_fund = np.array(fund.Data[0])/100
# r_fund = np.log(np.array(fund.Data[0])/np.array(fund.Data[1])) # 基金收益率序列
hs300 = w.wsd('000001.SH', "close,pre_close", start_date, end_date , "")            # 沪深300指数-市场组合
r_m = np.log(np.array(hs300.Data[0])/np.array(hs300.Data[1]))   # 市场组合的净值收益率序列
rf = np.array(w.wsd("SHIBOR3M.IR", "close",start_date, end_date , "").Data[0])/100       #无风险利率用3个月的SHIBOR来近似

return_period = sum(r_fund)        #阶段收益率
x, y = r_m -rf, r_fund - rf
x = x.reshape(len(x), 1)
c = np.ones((len(x),1))
X = np.hstack((c,x))
res = (sm.OLS(y,X)).fit()
alpha, beta = res.params[0], res.params[1]  #詹森系数 beta值
vol = np.std(r_fund)   #波动率
loss_rate = len(r_fund[r_fund<0])/len(r_fund)  #亏损比例
loss_ave = r_fund[r_fund<0].mean()
sharpe_ratio = (return_period - rf.mean())/(vol*np.sqrt(250))
sotino_ratio = (return_period - rf.mean())/beta
IR = alpha/(res.resid.std())
performance_fund = {'阶段收益率:':return_period,'詹森系数(alpha):':alpha,'beta:':beta,'波动率:':vol,'亏损比例:':loss_rate,'平均亏损:':loss_ave,\
                    'Sharpe比率:':sharpe_ratio,'Sotino比率:':sotino_ratio,'信息比:':IR}
print(performance_fund)