"""
数据加载模块
"""

import pandas as pd
import numpy as np


class DataLoader:
    """数据加载器"""
    
    def __init__(self):
        self.cache = {}
    
    def load_csv(self, filepath, **kwargs):
        """从CSV加载数据"""
        return pd.read_csv(filepath, **kwargs)
    
    def load_stock_data(self, symbol, start_date, end_date):
        """
        加载股票数据
        
        Args:
            symbol: 股票代码，如 '1810.HK'
            start_date: 开始日期 'YYYYMMDD'
            end_date: 结束日期 'YYYYMMDD'
        
        Returns:
            DataFrame with OHLCV data
        """
        # 模拟数据（实际需要接入数据源）
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        n = len(dates)
        
        # 生成模拟价格数据
        np.random.seed(42)
        returns = np.random.randn(n) * 0.02
        close = 30 * np.exp(np.cumsum(returns))
        
        df = pd.DataFrame({
            'date': dates,
            'open': close * (1 + np.random.randn(n) * 0.005),
            'high': close * (1 + np.abs(np.random.randn(n)) * 0.01),
            'low': close * (1 - np.abs(np.random.randn(n)) * 0.01),
            'close': close,
            'volume': np.random.randint(1000000, 50000000, n)
        })
        
        df.set_index('date', inplace=True)
        return df
    
    def add_technical_indicators(self, df):
        """添加技术指标"""
        # 移动平均线
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA10'] = df['close'].rolling(window=10).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        
        # BOLL
        df['BB_middle'] = df['close'].rolling(window=20).mean()
        df['BB_std'] = df['close'].rolling(window=20).std()
        df['BB_upper'] = df['BB_middle'] + 2 * df['BB_std']
        df['BB_lower'] = df['BB_middle'] - 2 * df['BB_std']
        
        return df
    
    def preprocess(self, df):
        """数据预处理"""
        # 删除空值
        df = df.dropna()
        
        # 处理异常值
        df = df[df['volume'] > 0]
        
        return df


if __name__ == '__main__':
    # 测试
    loader = DataLoader()
    df = loader.load_stock_data('1810.HK', '20240101', '20240601')
    df = loader.add_technical_indicators(df)
    print(df.tail())
