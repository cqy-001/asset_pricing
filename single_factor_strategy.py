from WindPy import *
from datetime import *
import pandas as pd

w.start(show_welcome=False)

stocks_list = w.wset("SectorConstituent", "date=2013-06-03;windcode=000300.SH").Data[1]  # 初始股票池

from WindAlgo import *  # 引入回测框架


def initialize(context):  # 定义初始化函数
    context.capital = 10000000  # 回测的初始资金
    context.securities = stocks_list  # 回测标的
    context.start_date = "20130601"  # 回测开始时间
    context.end_date = "20190531"  # 回测结束时间
    context.period = 'd'  # 'd' 代表日, 'm'代表分钟   表示行情数据的频率
    context.pos = 1  # 这个的1 表示查看因子最大的10%作为建仓股票
    context.feature = 'WEST_AVGROE_FY1'  # ROE一致性预期；这里 输入 感兴趣的因子-大写
    context.benchmark = '000300.SH'  # 设置回测基准为沪深300
    context.slippage_setting = SlippageSetting(stock_slippage_type='byRate', stock_slippage=0.0003)


def handle_data(bar_datetime, context, bar_data):
    pass


def my_schedule(bar_datetime, context, bar_data):  # 注意：schedule函数里不能加入新的参数

    field = context.feature  # 选择要下载的特征
    bar_datetime_str = bar_datetime.strftime('%Y-%m-%d')  # 设置时间
    data = w.wss(stocks_list, field, "tradeDate=" + bar_datetime_str) # 某些指标键值参数非tradeDate，而是rptDate（报告期）
    data = pd.DataFrame(data.Data, columns=data.Codes, index=data.Fields).T  # 改变格式为数据框
    data = data.fillna(0)  # 缺失设置为0
    data = data[data[context.feature] != 0]  # 因子为缺失的记录删除

    data = data.sort_values(context.feature)  # 截面按因子排序 注意是 由小到大的排序
    code_list = list(data[-(round(len(data) / 10) * context.pos):].index)  # 选择最后10%的股票 即因子最大的10%的股票

    is_success, bar_data = wa.change_securities(code_list)  # 改变股票池,同时返回当日新行情（对于停牌股票无行情）
    ##############剔除涨停的股票,并使用批量调仓函数调仓#############
    bar_data_df = bar_data.get_dataframe()
    lt_95_code = list(bar_data_df[bar_data_df['pctchg'] < 9.5]['code'])  # 获取行情中涨跌幅小余9.5%的股票
    buy_stock = list(set(lt_95_code) & set(code_list))  # 取交集，即要买且涨跌幅小余9.5%的股票
    if is_success == True:
        wa.batch_order.change_to(buy_stock, 1, price='close', volume_check=False, no_quotation='skip')


wa = BackTest(init_func=initialize, handle_data_func=handle_data)  # 实例化回测对象
wa.schedule(my_schedule, "m", 0)  # m表示在每个月执行一次策略 0表示偏移  表示月初第一个交易日往后0天
res = wa.run(show_progress=True)  # 调用run()函数开始回测,show_progress可用于指定是否显示回测净值曲线图

result = wa.summary('result')  # WindFrame 结构
result_df = result.get_dataframe() # DataFrame结构
result_df[['alpha','beta']]

nav = wa.summary('nav')
nav_df = nav.get_dataframe()
nav_df
