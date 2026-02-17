"""
多因子策略模块
"""

import pandas as pd
import numpy as np
from strategy.strategies import BaseStrategy


class MultiFactorStrategy(BaseStrategy):
    """
    多因子策略
    结合多个因子进行选股
    """
    
    def __init__(self, factors=None, weights=None, top_n=10):
        """
        Args:
            factors: 因子列表
            weights: 因子权重
            top_n: 选股数量
        """
        super().__init__(name="MultiFactor")
        self.factors = factors or ['pe', 'pb', 'roe', 'momentum']
        self.weights = weights or [0.25, 0.25, 0.25, 0.25]
        self.top_n = top_n
    
    def generate_signals(self, data):
        """多因子选股信号"""
        df = data.copy()
        
        # 模拟因子数据（实际需接入数据库）
        n = len(df)
        
        # PE 因子（市盈率，越低越好）
        df['factor_pe'] = np.random.uniform(5, 30, n)
        
        # PB 因子（市净率，越低越好）
        df['factor_pb'] = np.random.uniform(0.5, 5, n)
        
        # ROE 因子（净资产收益率，越高越好）
        df['factor_roe'] = np.random.uniform(5, 30, n)
        
        # 动量因子（20日涨幅，越高越好）
        df['factor_momentum'] = df['close'].pct_change(20)
        
        # 标准化因子
        for factor in self.factors:
            if f'factor_{factor}' in df.columns:
                col = f'factor_{factor}'
                df[f'{col}_rank'] = df[col].rank(pct=True)
        
        # 计算综合得分
        df['composite_score'] = 0
        for i, factor in enumerate(self.factors):
            col = f'factor_{factor}_rank'
            if col in df.columns:
                # 动量和ROE越高越好，其他越低越好
                if factor in ['momentum', 'roe']:
                    df['composite_score'] += df[col] * self.weights[i]
                else:
                    df['composite_score'] += (1 - df[col]) * self.weights[i]
        
        # 信号
        df['signal'] = 0
        # 选择综合得分最高的 N 只股票
        if 'composite_score' in df.columns:
            score = df['composite_score'].iloc[-1]
            if pd.notna(score) and score > df['composite_score'].quantile(0.8):
                df.loc[df.index[-1], 'signal'] = 1
        
        return df


class PairsTradingStrategy(BaseStrategy):
    """
    配对交易策略
    两只高度相关的股票，当价差偏离时套利
    """
    
    def __init__(self, lookback=60, entry_threshold=2, exit_threshold=0.5):
        super().__init__(name="PairsTrading")
        self.lookback = lookback
        self.entry_threshold = entry_threshold
        self.exit_threshold = exit_threshold
    
    def generate_signals(self, data):
        """
        data: 需要包含两只股票的价格
        格式: DataFrame with columns ['stock1', 'stock2']
        """
        df = data.copy()
        
        # 计算价格比率
        df['ratio'] = df['stock1'] / df['stock2']
        
        # 计算均值和标准差
        df['ratio_mean'] = df['ratio'].rolling(self.lookback).mean()
        df['ratio_std'] = df['ratio'].rolling(self.lookback).std()
        
        # 计算 z-score
        df['zscore'] = (df['ratio'] - df['ratio_mean']) / df['ratio_std']
        
        # 信号
        df['signal'] = 0
        
        # 当 z-score > 阈值，做空 stock1，做多 stock2
        df.loc[df['zscore'] > self.entry_threshold, 'signal'] = -1
        
        # 当 z-score < -阈值，做多 stock1，做空 stock2
        df.loc[df['zscore'] < -self.entry_threshold, 'signal'] = 1
        
        # 当 z-score 回归到 0 附近，平仓
        df.loc[np.abs(df['zscore']) < self.exit_threshold, 'signal'] = 0
        
        return df


class DualThrustStrategy(BaseStrategy):
    """
    Dual Thrust 策略
    日内突破策略
    """
    
    def __init__(self, k1=0.5, k2=0.5):
        super().__init__(name="DualThrust")
        self.k1 = k1  # 上轨系数
        self.k2 = k2  # 下轨系数
    
    def generate_signals(self, data):
        df = data.copy()
        
        # 计算 N 日最高价、最低价、收盘价
        n = 20
        df['hh'] = df['high'].rolling(n).max()  # N日最高价
        df['ll'] = df['low'].rolling(n).min()   # N日最低价
        df['hc'] = df['close'].rolling(n).max()  # N日收盘最高价
        df['lc'] = df['close'].rolling(n).min()  # N日收盘最低价
        
        # 计算枢轴
        df['pivot'] = (df['hh'] + df['lc'] + df['ll'] + df['hc']) / 4
        
        # 上轨和下轨
        df['upper'] = df['pivot'] + self.k1 * (df['hh'] - df['ll'])
        df['lower'] = df['pivot'] - self.k2 * (df['hh'] - df['ll'])
        
        # 信号
        df['signal'] = 0
        # 突破上轨买入
        df.loc[df['close'] > df['upper'], 'signal'] = 1
        # 跌破下轨卖出
        df.loc[df['close'] < df['lower'], 'signal'] = -1
        
        return df


class TurtleStrategy(BaseStrategy):
    """
    海龟交易策略
    趋势跟踪策略
    """
    
    def __init__(self, entry_period=20, exit_period=10, atr_period=20):
        super().__init__(name="Turtle")
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.atr_period = atr_period
    
    def generate_signals(self, data):
        df = data.copy()
        
        # 计算最高价和最低价
        df['entry_high'] = df['high'].rolling(self.entry_period).max()
        df['exit_low'] = df['low'].rolling(self.exit_period).min()
        
        # 计算 ATR（真实波幅）
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        df['tr'] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        df['atr'] = df['tr'].rolling(self.atr_period).mean()
        
        # 信号
        df['signal'] = 0
        # 突破20日高点买入
        df.loc[df['close'] > df['entry_high'], 'signal'] = 1
        # 跌破10日低点卖出
        df.loc[df['close'] < df['exit_low'], 'signal'] = -1
        
        return df


class GridStrategy(BaseStrategy):
    """
    网格交易策略
    震荡市场策略
    """
    
    def __init__(self, grid_count=10, grid_pct=0.02):
        super().__init__(name="Grid")
        self.grid_count = grid_count
        self.grid_pct = grid_pct
    
    def generate_signals(self, data):
        df = data.copy()
        
        # 计算网格价格
        base_price = df['close'].iloc[0]
        grid_prices = [
            base_price * (1 + self.grid_pct * i) 
            for i in range(-self.grid_count, self.grid_count + 1)
        ]
        
        # 当前价格所在的网格
        df['current_grid'] = df['close'].apply(
            lambda x: min(range(len(grid_prices)), 
                        key=lambda i: abs(grid_prices[i] - x))
        )
        
        # 信号
        df['signal'] = 0
        
        # 价格低于网格买入
        df.loc[df['current_grid'] < self.grid_count // 2, 'signal'] = 1
        # 价格高于网格卖出
        df.loc[df['current_grid'] > self.grid_count * 3 // 2, 'signal'] = -1
        
        return df


if __name__ == '__main__':
    # 测试
    from data.data_loader import DataLoader
    
    loader = DataLoader()
    data = loader.load_stock_data('1810.HK', '20240101', '20240601')
    data = loader.add_technical_indicators(data)
    
    # 测试多因子策略
    strategy = MultiFactorStrategy(factors=['pe', 'pb', 'roe', 'momentum'])
    result = strategy.backtest(data)
    print(f"策略: {result['strategy']}")
    print(f"收益: {result['total_return']:.2f}%")
