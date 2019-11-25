from WindPy import *
import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
w.start()

start_date, end_date = "2018-11-01", "2019-10-31"
fund = w.wsd("110022.OF", "NAV_adj_return1", start_date, end_date, "Fill=Previous;PriceAdj=F")   #易方达消费行业
r_fund = np.array(fund.Data[0])/100
# fund = w.wsd('110022.OF', 'close,pre_close', start_date, end_date )
# r_fund = np.log(np.array(fund.Data[0])/np.array(fund.Data[1])) #基金收益率序列
rf = np.array(w.wsd("SHIBOR3M.IR", "close",start_date, end_date , "").Data[0])/100       #无风险利率用3个月的SHIBOR来近似

list_style = ['801863.SI','801822.SI','801813.SI','801831.SI','801812.SI','801821.SI','801852.SI','801842.SI','801843.SI','801832.SI','801851.SI',\
              '801853.SI','801841.SI','801833.SI','801823.SI','801811.SI']
label_style = ['新股指数','中市盈率指数','小盘指数','高市净率指数','中盘指数','高市盈率指数','微利股指数','中价股指数','低价股指数','中市净率指数','亏损股指数',\
               '绩优股指数','高价股指数','低市净率指数','低市盈率指数','大盘指数']
list_r2, list_beta, list_tr = [], [], []
for code in list_style:
    style = w.wsd(code, 'close,pre_close', start_date, end_date)
    r_style = np.log(np.array(style.Data[0])/np.array(style.Data[1]))
    x, y = r_style - rf, r_fund - rf
    x = x.reshape(len(x),1)
    c = np.ones((len(x),1))
    X = np.hstack((c,x))
    res = (sm.OLS(y,X)).fit()
    list_r2.append(res.rsquared)
    list_beta.append(res.params[1])
    list_tr.append(np.log(style.Data[0][-1]/style.Data[0][0]) - rf.mean())
res_style = pd.DataFrame([])
res_style['指数代码']= list_style
res_style['指数名称'] = label_style
res_style['拟合R方'] = list_r2
res_style['beta'] = list_beta
res_style['期间超额收益'] = list_tr
res_style['开始时间'] = '2017-01-01'
res_style['终止时间'] = '2017-12-31'
res_style = res_style.sort_values('拟合R方',ascending=False)
print(res_style)

style = w.wsd('801853.SI', 'close,pre_close', start_date, end_date) #绩优股指数
r_style = np.log(np.array(style.Data[0])/np.array(style.Data[1]))
x, y = r_style - rf, r_fund - rf
x = x.reshape(len(x),1)
c = np.ones((len(x),1))
X = np.hstack((c,x))
res = (sm.OLS(y,X)).fit()

plt.style.use('ggplot')
plt.figure(figsize=(11,5))
plt.scatter(x, y, s=30 ,color='blue',label='Fact')
plt.plot(x, res.params[0]+res.params[1]*x, linewidth=3,color='red',label='regression line')
plt.ylabel('excess return of fund')
plt.xlabel('excess return of style index')
plt.title('The Style Index that fits the fund"s return best:801853(SW)', fontsize=13, bbox={'facecolor':'0.8', 'pad':5})
plt.grid(True)
plt.legend(loc='upper left')  #添加图例
plt.show()


