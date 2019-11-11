# -*- coding: utf-8 -*-
from WindPy import *
from pylab import *
import numpy as np
import pandas as pd
import scipy.optimize as sco  # 求解约束最优化问题
import matplotlib.pyplot as plt
plt.style.use('ggplot')
mpl.rcParams['font.sans-serif'] = ['SimHei']

risk_free = 0.03
w.start()
close = w.wsd("000001.SZ,000488.SZ,000651.SZ,002415.SZ,600104.SH,600196.SH,600340.SH,600895.SH,600900.SH,601989.SH",
              "close", "2017-01-01", "2017-12-31", "Fill=Previous;PriceAdj=F")
data = pd.DataFrame(close.Data, index=close.Codes, columns=close.Times).T
r = data.pct_change().mean()*252  # 期望收益率
cov_mat = data.pct_change().cov()*252   # 协方差矩阵
k = len(r)

port_r, port_var = [], []
for p in range(4000):
    weights = np.random.random(k)
    weights /= np.sum(weights)
    port_r.append(np.sum(r*weights))
    port_var.append(np.sqrt(weights.T.dot(cov_mat).dot(weights)))
port_r, port_var = np.array(port_r), np.array(port_var)


def statistics(weights):

    weights = np.array(weights)
    port_returns = np.sum(r*weights)
    port_variance = np.sqrt(weights.T.dot(cov_mat).dot(weights))

    return np.array([port_returns, port_variance, (port_returns-risk_free)/port_variance])

def variance(weights):
    return statistics(weights)[1]

# 在不同目标收益率水平（target_returns）循环时，最小化的一个约束条件会变化。
target_returns = np.linspace(0.0, 0.6, 100)
target_variance = []
for tar in target_returns:
    bnds = tuple((0,1) for x in range(k))
    #  这里使用了lambda函数来表示优化问题的约束条件
    cons = ({'type': 'eq', 'fun': lambda x: statistics(x)[0]-tar}, {'type': 'eq', 'fun': lambda x: np.sum(x)-1})
    res = sco.minimize(variance, k*[1./k], method='SLSQP', bounds=bnds, constraints=cons)
    target_variance.append(res.fun)
target_variance = np.array(target_variance)

plt.figure(figsize=(10, 5))
plt.scatter(port_var, port_r, c=(port_r-risk_free)/port_var,  marker='o', label='随机投资组合')
plt.plot(target_variance, target_returns, c='red', linewidth=2.3, label='有效边界')
plt.grid(True)
plt.xlabel('波动率')
plt.ylabel('期望收益率')
plt.legend(loc='best')
plt.colorbar(label='夏普比率')
plt.show()



