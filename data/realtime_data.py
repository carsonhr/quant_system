"""
实时数据接口 - 使用 Akshare
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta


class RealTimeData:
    """实时数据获取"""
    
    @staticmethod
    def get_stock_zh_a_hist(symbol, period='daily', start_date='20240101', end_date='20241231'):
        """
        获取A股历史数据
        
        Args:
            symbol: 股票代码，如 '1810'（港股）或 '000001'（A股）
            period: 'daily', 'weekly', 'monthly'
            start_date: 开始日期 YYYYMMDD
            end_date: 结束日期 YYYYMMDD
        
        Returns:
            DataFrame
        """
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=""
            )
            return df
        except Exception as e:
            print(f"获取数据失败: {e}")
            return None
    
    @staticmethod
    def get_stock_info(symbol):
        """获取股票基本信息"""
        try:
            df = ak.stock_individual_info_em(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取信息失败: {e}")
            return None
    
    @staticmethod
    def get_realtime_quote(symbol):
        """获取实时行情"""
        try:
            df = ak.stock_zh_a_spot_em()
            df = df[df['代码'] == symbol]
            return df
        except Exception as e:
            print(f"获取实时行情失败: {e}")
            return None
    
    @staticmethod
    def get_hk_stock_hist(symbol, period='daily', start_date='20240101', end_date='20241231'):
        """
        获取港股历史数据
        
        Args:
            symbol: 港股代码，如 '1810'
            period: 'daily', 'weekly', 'monthly'
        """
        try:
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
            return df
        except Exception as e:
            print(f"获取港股数据失败: {e}")
            return None
    
    @staticmethod
    def get_us_stock_hist(symbol, period='daily', start_date='2024-01-01'):
        """
        获取美股历史数据
        
        Args:
            symbol: 美股代码，如 'AAPL'
            period: '1d', '1wk', '1mo'
        """
        try:
            df = ak.stock_us_hist(symbol=symbol, period=period, start_date=start_date)
            return df
        except Exception as e:
            print(f"获取美股数据失败: {e}")
            return None


class FundamentalData:
    """基本面数据"""
    
    @staticmethod
    def get_financial_index(symbol):
        """获取财务指标"""
        try:
            df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="按报告期")
            return df
        except Exception as e:
            print(f"获取财务数据失败: {e}")
            return None
    
    @staticmethod
    def get_stock_holder(symbol):
        """获取股东信息"""
        try:
            df = ak.stock_zh_a_gdhs(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取股东数据失败: {e}")
            return None
    
    @staticmethod
    def get_news():
        """获取财经新闻"""
        try:
            df = ak.stock_news_em()
            return df
        except Exception as e:
            print(f"获取新闻失败: {e}")
            return None


class MarketData:
    """市场数据"""
    
    @staticmethod
    def get_index_daily():
        """获取指数日线"""
        try:
            df = ak.index_zh_a_hist(symbol="000001", period="daily", start_date="20240101")
            return df
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return None
    
    @staticmethod
    def get_market_baidu():
        """获取百度股市情绪"""
        try:
            df = ak.stock_market_liquidity东南()
            return df
        except Exception as e:
            print(f"获取市场情绪失败: {e}")
            return None


class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.realtime = RealTimeData()
        self.fundamental = FundamentalData()
        self.market = MarketData()
    
    def get_stock_data(self, market='hk', symbol='1810', days=250):
        """
        获取股票数据
        
        Args:
            market: 'hk', 'us', 'a'
            symbol: 股票代码
            days: 获取天数
        """
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
        
        if market == 'hk':
            return self.realtime.get_hk_stock_hist(symbol, start_date=start_date, end_date=end_date)
        elif market == 'us':
            return self.realtime.get_us_stock_hist(symbol, start_date=start_date)
        else:
            return self.realtime.get_stock_zh_a_hist(symbol, start_date=start_date, end_date=end_date)
    
    def get_multiple_stocks(self, symbols, days=250):
        """获取多只股票数据"""
        data = {}
        for symbol in symbols:
            df = self.get_stock_data(symbol=symbol, days=days)
            if df is not None:
                data[symbol] = df
        return data


if __name__ == '__main__':
    # 测试
    dm = DataManager()
    
    # 获取港股小米数据
    print("获取小米(1810)数据...")
    df = dm.get_stock_data(market='hk', symbol='1810', days=30)
    if df is not None:
        print(df.tail())
    
    # 获取A股数据
    print("\n获取A股(000001)数据...")
    df_a = dm.get_stock_data(market='a', symbol='000001', days=30)
    if df_a is not None:
        print(df_a.tail())
