import pandas as pd


def topic_two(input_path, output_path):
    """
    已知：根据分钟K线的收盘价(close字段)，向前取5根（包含当前根，共5根）的收盘价的平均值，是当前K线的5分钟均值，
    10根K线收盘价平均值为当前K线的10分钟均值。将均值连线，成为移动平均线，简称均线
	现有如下策略：当5分钟均线上穿10分钟均线（即在前一根K线上5分钟均线的值小于10分钟均线的值，当前K线上，5分钟均线的值大于10分钟均线的值）时，
	执行买入操作，等向后第一次出现10分钟均线上穿5分钟均线时，执行卖出操作。每次交易买入卖出单位为10，每次没有卖出前不重复买入。例如10点时，
	5分钟均线上穿10分钟均线，收盘价为100，执行买入操作，11点时，出现了10分钟均线上穿5分钟均线，此时收盘价为110，
	执行卖出操作。这样盈亏为（110-100）*10 = 100，即盈利100。

	根据给出的中证500指数1分钟K线数据，截取2022年1月1日到2023年1月1日的数据，在这个时间区间内，
	使用上述策略，将交易流水写入csv文件（表头包括：时间、价格、方向（买/卖）），并统计盈利总额和胜率（盈利交易次数占总交易次数的比值）。

    :param input_path: 样本输入路径
    :param output_path: 交易信息输入路径
    :return:
    """

    data = pd.read_csv(input_path, parse_dates=[0], index_col=0)
    data = data[(data.index >= '2022-01-01') & (data.index <= '2023-01-01')]

    # 取每五个的平均值
    data['MA_5'] = data['close'].rolling(window=5).mean()
    data['MA_10'] = data['close'].rolling(window=10).mean()

    data['Signal'] = 0  # 1 买 -1 卖
    for i in range(1, len(data)):
        # 当前K线上，5分钟均线的值大于10分钟均线的值    and  前一根K线上5分钟均线的值小于10分钟均线的值
        if data['MA_5'].iloc[i] > data['MA_10'].iloc[i] and data['MA_5'].iloc[i - 1] <= data['MA_10'].iloc[i - 1]:
            data.loc[data.index[i], 'Signal'] = 1  # 买
        # 当前K线上，5分钟均线的值小于10分钟均线的值    and  前一根K线上5分钟均线的值大于10分钟均线的值
        elif data['MA_5'].iloc[i] < data['MA_10'].iloc[i] and data['MA_5'].iloc[i - 1] >= data['MA_10'].iloc[i - 1]:
            data.loc[data.index[i], 'Signal'] = -1  # 卖

    # 交易信息
    trades = []
    position = 0  # 0 没有 1 拥有
    for i in range(len(data)):
        # 买 and 没有
        if data['Signal'].iloc[i] == 1 and position == 0:
            # 买 信息
            trades.append({'datetime_nano': data.index[i], 'price': data['close'].iloc[i], 'direction': 'buy'})
            position = 1
        # 卖 and 有
        elif data['Signal'].iloc[i] == -1 and position == 1:
            # 卖 信息
            trades.append({'datetime_nano': data.index[i], 'price': data['close'].iloc[i], 'direction': 'sell'})
            position = 0

    # 写入交易信息
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv(output_path, index=False)

    profits = []
    for i in range(0, len(trades) - 1, 2):
        buy_price = trades[i]['price']  # 买
        sell_price = trades[i + 1]['price']  # 卖出
        profit = (sell_price - buy_price) * 10  # 差额 * 10
        profits.append(profit)

    total_profit = sum(profits)  # 盈利总额
    win_rate = len([p for p in profits if p > 0]) / len(profits) if profits else 0  # 胜率

    print(f"Total Profit: {total_profit}")
    print(f"Win Rate: {win_rate}")


if __name__ == '__main__':
    input_path = "CFFEX.IC_1min.csv"
    out_path = "trade_info.csv"
    topic_two(input_path, out_path)
