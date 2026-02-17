"""
真实数据回测示例
使用 Akshare 获取真实历史数据
"""

import akshare as ak
import pandas as pd
import numpy as np


def get_real_stock_data(symbol, market='index', start_date='20200101', end_date='20231231'):
    """
    获取真实股票/指数数据
    
    Args:
        symbol: 代码
            - 指数: '000001' (上证指数), '399001' (深证成指)
            - A股: '000001', '600519' (茅台)
        market: 'index' (指数), 'stock' (股票)
        start_date: 开始日期 YYYYMMDD
        end_date: 结束日期 YYYYMMDD
    
    Returns:
        DataFrame: OHLCV 数据
    """
    if market == 'index':
        df = ak.index_zh_a_hist(
            symbol=symbol, 
            period="daily",
            start_date=start_date, 
            end_date=end_date
        )
    else:
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily", 
            start_date=start_date,
            end_date=end_date,
            adjust=""
        )
    
    # 标准化列名
    df = df.rename(columns={
        '日期': 'date',
        '开盘': 'open',
        '收盘': 'close', 
        '最高': 'high',
        '最低': 'low',
        '成交量': 'volume',
        '成交额': 'amount',
        '涨跌幅': 'pct_change'
    })
    
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    df = df.sort_index()
    
    # 确保数值类型
    for col in ['open', 'close', 'high', 'low', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def get_hk_stock_data(symbol='01810', start_date='20200101', end_date='20231231'):
    """
    获取港股数据
    
    注意: Akshare 港股数据可能不稳定
    """
    # 尝试获取港股
    try:
        # 港股需要用特殊接口
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"  # 前复权
        )
        return df
    except:
        print("港股数据获取失败，尝试其他方法...")
        return None


def get_us_stock_data(symbol='DJI', start_date='20200101'):
    """
    获取美股/港股数据
    """
    try:
        df = ak.stock_us_hist(symbol=symbol, period='1d', start_date=start_date)
        return df
    except Exception as e:
        print(f"美股数据获取失败: {e}")
        return None


def get_multiple_stocks(symbols, market='index', days=250):
    """
    获取多只股票/指数数据
    
    Args:
        symbols: 代码列表
        market: 'index' 或 'stock'
        days: 获取天数
    
    Returns:
        dict: {symbol: DataFrame}
    """
    from datetime import datetime, timedelta
    
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
    
    data = {}
    for symbol in symbols:
        print(f"获取 {symbol}...")
        df = get_real_stock_data(symbol, market, start_date, end_date)
        if df is not None:
            data[symbol] = df
    
    return data


# ============ 数据预处理 ============

def add_indicators(df):
    """添加技术指标"""
    # 均线
    for window in [5, 10, 20, 60, 120, 250]:
        df[f'MA{window}'] = df['close'].rolling(window).mean()
    
    # RSI
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
    
    # BOLL
    df['BOLL_Mid'] = df['close'].rolling(20).mean()
    df['BOLL_Std'] = df['close'].rolling(20).std()
    df['BOLL_Upper'] = df['BOLL_Mid'] + 2 * df['BOLL_Std']
    df['BOLL_Lower'] = df['BOLL_Mid'] - 2 * df['BOLL_Std']
    
    # ATR
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(14).mean()
    
    return df


# ============ 主程序 ============

if __name__ == '__main__':
    print("=" * 60)
    print("真实数据回测示例")
    print("=" * 60)
    
    # 获取上证指数数据
    print("\n[1] 获取上证指数 (000001)...")
    df = get_real_stock_data('000001', market='index', 
                            start_date='20200101', 
                            end_date='20231231')
    print(f"    获取成功: {len(df)} 条")
    
    # 添加指标
    print("\n[2] 计算技术指标...")
    df = add_indicators(df)
    print("    完成")
    
    # 显示数据
    print("\n[3] 数据预览:")
    print(df[['close', 'MA5', 'MA20', 'RSI', 'MACD']].tail())
    
    print("\n✅ 完成!")
