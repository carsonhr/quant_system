"""
RSI均值回归策略
找到的最佳策略: RSI<30买入, RSI>65卖出
回测结果: 2015-2023年收益 +64.33%, 年化5.89%
"""

import akshare as ak
import pandas as pd
import numpy as np


def get_index_data(symbol='000001', start_date='20150101', end_date='20231231'):
    """获取指数数据"""
    df = ak.index_zh_a_hist(symbol=symbol, period='daily', 
                           start_date=start_date, end_date=end_date)
    df = df.rename(columns={
        '日期': 'date', '开盘': 'open', '收盘': 'close', 
        '最高': 'high', '最低': 'low', '成交量': 'volume'
    })
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    for col in ['open', 'close', 'high', 'low', 'volume']:
        df[col] = pd.to_numeric(df[col])
    return df.sort_index()


def calculate_rsi(df, period=14):
    """计算RSI指标"""
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


class RSIStrategy:
    """
    RSI均值回归策略
    
    策略逻辑:
    - 当RSI < 30 (超卖)时买入
    - 当RSI > 65 (超买)时卖出
    
    回测结果 (2015-2023):
    - 总收益: +64.33%
    - 年化收益: 5.89%
    - 最大回撤: 17.39%
    """
    
    def __init__(self, oversold=30, overbought=65):
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, df):
        """生成交易信号"""
        df = df.copy()
        df['RSI'] = calculate_rsi(df)
        
        # 信号
        df['signal'] = 0
        
        # 买入信号: RSI超卖
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1
        
        # 卖出信号: RSI超买
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1
        
        return df
    
    def backtest(self, df, initial_capital=100000, commission=0.001):
        """回测"""
        df = self.generate_signals(df)
        
        cash = initial_capital
        position = 0
        trades = []
        portfolio = []
        
        for i in range(60, len(df)):
            rsi = df['RSI'].iloc[i]
            price = df['close'].iloc[i]
            date = df.index[i]
            
            # 买入
            if rsi < self.oversold and position == 0:
                shares = int(cash / price)
                if shares > 0:
                    cost = shares * price * (1 + commission)
                    cash -= cost
                    position = shares
                    trades.append({'date': date, 'action': 'BUY', 'price': price})
            
            # 卖出
            elif rsi > self.overbought and position > 0:
                revenue = position * price * (1 - commission)
                trades.append({'date': date, 'action': 'SELL', 'price': price})
                cash += revenue
                position = 0
            
            # 记录组合价值
            value = cash + position * price
            portfolio.append({'date': date, 'value': value})
        
        # 计算指标
        final_value = cash + position * df.iloc[-1]['close']
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        years = len(df) / 252
        annual_return = ((final_value / initial_capital) ** (1/years) - 1) * 100
        
        # 最大回撤
        pf = pd.DataFrame(portfolio)
        pf['cummax'] = pf['value'].cummax()
        max_dd = ((pf['cummax'] - pf['value']) / pf['cummax']).max() * 100
        
        # 夏普比率
        returns = pf['value'].pct_change().dropna()
        if returns.std() > 0:
            sharpe = (returns.mean() * 252 - 0.03) / (returns.std() * np.sqrt(252))
        else:
            sharpe = 0
        
        return {
            'strategy': 'RSI均值回归',
            'params': f'RSI<{self.oversold}买入, RSI>{self.overbought}卖出',
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_dd,
            'sharpe_ratio': sharpe,
            'total_trades': len(trades),
            'trades': trades,
            'portfolio': pf
        }


if __name__ == '__main__':
    print("=" * 60)
    print("RSI均值回归策略回测")
    print("=" * 60)
    
    # 获取数据
    print("\n[1] 获取上证指数数据...")
    df = get_index_data('000001', '20150101', '20231231')
    print(f"    数据量: {len(df)} 条")
    
    # 回测
    print("\n[2] 运行回测...")
    strategy = RSIStrategy(oversold=30, overbought=65)
    result = strategy.backtest(df)
    
    # 显示结果
    print(f"""
============================================================
                    回测结果
============================================================
策略: {result['strategy']}
参数: {result['params']}
初始资金: ¥{result['initial_capital']:,.0f}
最终价值: ¥{result['final_value']:,.0f}
总收益: {result['total_return']:.2f}%
年化收益: {result['annual_return']:.2f}%
最大回撤: {result['max_drawdown']:.2f}%
夏普比率: {result['sharpe_ratio']:.2f}
交易次数: {result['total_trades']}
============================================================
""")
