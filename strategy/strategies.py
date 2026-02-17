"""
策略模块
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    """策略基类"""
    
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
        self.positions = []
        self.trades = []
    
    @abstractmethod
    def generate_signals(self, data):
        """
        生成交易信号
        
        Returns:
            DataFrame with 'signal' column:
                1 = 买入
                0 = 持有
                -1 = 卖出
        """
        pass
    
    def backtest(self, data, initial_capital=100000, commission=0.001):
        """
        回测策略
        
        Args:
            data: OHLCV 数据
            initial_capital: 初始资金
            commission: 交易佣金费率
        
        Returns:
            dict: 回测结果
        """
        df = self.generate_signals(data).copy()
        
        # 初始化
        cash = initial_capital
        position = 0  # 持仓股数
        trades = []
        portfolio_values = []
        
        for i, (date, row) in enumerate(df.iterrows()):
            price = row['close']
            signal = row['signal']
            
            # 买入信号
            if signal == 1 and position == 0:
                # 全部买入
                shares = int(cash / (price * (1 + commission)))
                if shares > 0:
                    cost = shares * price * (1 + commission)
                    cash -= cost
                    position = shares
                    trades.append({
                        'date': date,
                        'action': 'BUY',
                        'price': price,
                        'shares': shares,
                        'cost': cost
                    })
            
            # 卖出信号
            elif signal == -1 and position > 0:
                # 全部卖出
                revenue = position * price * (1 - commission)
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'price': price,
                    'shares': position,
                    'revenue': revenue
                })
                cash += revenue
                position = 0
            
            # 记录组合价值
            portfolio_value = cash + position * price
            portfolio_values.append({
                'date': date,
                'value': portfolio_value,
                'position': position,
                'cash': cash
            })
        
        # 计算收益
        final_value = cash + position * df.iloc[-1]['close']
        total_return = (final_value - initial_capital) / initial_capital * 100
        
        # 计算风险指标
        portfolio_df = pd.DataFrame(portfolio_values)
        portfolio_df['returns'] = portfolio_df['value'].pct_change()
        
        # 年化收益
        days = len(portfolio_df)
        annual_return = ((1 + total_return/100) ** (252/days) - 1) * 100
        
        # 最大回撤
        portfolio_df['cummax'] = portfolio_df['value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['cummax'] - portfolio_df['value']) / portfolio_df['cummax']
        max_drawdown = portfolio_df['drawdown'].max() * 100
        
        # 夏普比率 (假设无风险利率3%)
        returns = portfolio_df['returns'].dropna()
        if returns.std() > 0:
            sharpe = (returns.mean() - 0.03/252) / returns.std() * np.sqrt(252)
        else:
            sharpe = 0
        
        return {
            'strategy': self.name,
            'initial_capital': initial_capital,
            'final_value': final_value,
            'total_return': total_return,
            'annual_return': annual_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe,
            'total_trades': len(trades),
            'trades': trades,
            'portfolio_history': portfolio_df
        }


class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    def __init__(self, lookback=20, threshold=0.05):
        super().__init__(name="Momentum")
        self.lookback = lookback
        self.threshold = threshold
    
    def generate_signals(self, data):
        """基于动量生成信号"""
        df = data.copy()
        
        # 计算N日收益率
        df['momentum'] = df['close'].pct_change(self.lookback)
        
        # 信号
        df['signal'] = 0
        df.loc[df['momentum'] > self.threshold, 'signal'] = 1   # 买入
        df.loc[df['momentum'] < -self.threshold, 'signal'] = -1  # 卖出
        
        return df


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self, window=20, std_threshold=2):
        super().__init__(name="MeanReversion")
        self.window = window
        self.std_threshold = std_threshold
    
    def generate_signals(self, data):
        """基于均值回归生成信号"""
        df = data.copy()
        
        # 计算布林带
        df['ma'] = df['close'].rolling(window=self.window).mean()
        df['std'] = df['close'].rolling(window=self.window).std()
        df['upper'] = df['ma'] + self.std_threshold * df['std']
        df['lower'] = df['ma'] - self.std_threshold * df['std']
        
        # 信号
        df['signal'] = 0
        df.loc[df['close'] < df['lower'], 'signal'] = 1   # 低于下轨，买入
        df.loc[df['close'] > df['upper'], 'signal'] = -1  # 高于上轨，卖出
        
        return df


class RSIStrategy(BaseStrategy):
    """RSI策略"""
    
    def __init__(self, period=14, oversold=30, overbought=70):
        super().__init__(name="RSI")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def generate_signals(self, data):
        """基于RSI生成信号"""
        df = data.copy()
        
        # 计算RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # 信号
        df['signal'] = 0
        df.loc[df['rsi'] < self.oversold, 'signal'] = 1   # 超卖，买入
        df.loc[df['rsi'] > self.overbought, 'signal'] = -1 # 超买，卖出
        
        return df


class MACDStrategy(BaseStrategy):
    """MACD策略"""
    
    def __init__(self, fast=12, slow=26, signal=9):
        super().__init__(name="MACD")
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, data):
        """基于MACD生成信号"""
        df = data.copy()
        
        # 计算MACD
        exp1 = df['close'].ewm(span=self.fast, adjust=False).mean()
        exp2 = df['close'].ewm(span=self.slow, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal_line'] = df['macd'].ewm(span=self.signal, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal_line']
        
        # 信号
        df['signal'] = 0
        # 金叉买入
        df.loc[(df['macd'] > df['signal_line']) & 
               (df['macd'].shift(1) <= df['signal_line'].shift(1)), 'signal'] = 1
        # 死叉卖出
        df.loc[(df['macd'] < df['signal_line']) & 
               (df['macd'].shift(1) >= df['signal_line'].shift(1)), 'signal'] = -1
        
        return df


if __name__ == '__main__':
    # 测试
    from data.data_loader import DataLoader
    
    loader = DataLoader()
    data = loader.load_stock_data('1810.HK', '20240101', '20240601')
    data = loader.add_technical_indicators(data)
    
    # 测试动量策略
    strategy = MomentumStrategy(lookback=20, threshold=0.05)
    result = strategy.backtest(data)
    
    print(f"策略: {result['strategy']}")
    print(f"总收益: {result['total_return']:.2f}%")
    print(f"年化收益: {result['annual_return']:.2f}%")
    print(f"最大回撤: {result['max_drawdown']:.2f}%")
    print(f"夏普比率: {result['sharpe_ratio']:.2f}")
    print(f"交易次数: {result['total_trades']}")
