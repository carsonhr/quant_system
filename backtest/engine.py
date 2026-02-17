"""
回测引擎
"""

import pandas as pd
import numpy as np
from datetime import datetime


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, data, initial_capital=100000, commission=0.001):
        """
        初始化回测引擎
        
        Args:
            data: DataFrame with OHLCV data
            initial_capital: 初始资金
            commission: 交易佣金费率
        """
        self.data = data
        self.initial_capital = initial_capital
        self.commission = commission
        
    def run(self, strategy):
        """
        运行回测
        
        Args:
            strategy: 策略实例
        
        Returns:
            dict: 回测结果
        """
        return strategy.backtest(
            self.data, 
            self.initial_capital, 
            self.commission
        )
    
    def run_multiple(self, strategies):
        """
        运行多个策略对比
        
        Args:
            strategies: 策略列表
        
        Returns:
            DataFrame: 多策略对比结果
        """
        results = []
        
        for strategy in strategies:
            result = self.run(strategy)
            results.append({
                'strategy': result['strategy'],
                'total_return': result['total_return'],
                'annual_return': result['annual_return'],
                'max_drawdown': result['max_drawdown'],
                'sharpe_ratio': result['sharpe_ratio'],
                'total_trades': result['total_trades']
            })
        
        return pd.DataFrame(results)
    
    def optimize_parameters(self, strategy_class, param_grid, metric='sharpe_ratio'):
        """
        参数优化
        
        Args:
            strategy_class: 策略类
            param_grid: 参数网格
            metric: 优化指标
        
        Returns:
            dict: 最优参数和结果
        """
        results = []
        
        # 生成所有参数组合
        from itertools import product
        keys = param_grid.keys()
        values = param_grid.values()
        
        for params in product(*values):
            # 创建策略实例
            strategy = strategy_class(**dict(zip(keys, params)))
            
            # 运行回测
            result = self.run(strategy)
            
            results.append({
                'params': dict(zip(keys, params)),
                'metric': result[metric],
                'result': result
            })
        
        # 找到最优
        best = max(results, key=lambda x: x['metric'])
        
        return best


class PerformanceAnalyzer:
    """性能分析器"""
    
    @staticmethod
    def analyze(portfolio_df):
        """
        分析组合表现
        
        Args:
            portfolio_df: 组合历史数据
        
        Returns:
            dict: 性能指标
        """
        returns = portfolio_df['value'].pct_change().dropna()
        
        # 基础指标
        total_return = (portfolio_df['value'].iloc[-1] / portfolio_df['value'].iloc[0] - 1) * 100
        
        # 年化收益
        days = len(portfolio_df)
        annual_return = ((1 + total_return/100) ** (252/days) - 1) * 100
        
        # 波动率
        volatility = returns.std() * np.sqrt(252) * 100
        
        # 夏普比率
        if volatility > 0:
            sharpe = (annual_return - 3) / volatility  # 假设无风险利率3%
        else:
            sharpe = 0
        
        # 最大回撤
        cummax = portfolio_df['value'].cummax()
        drawdown = (cummax - portfolio_df['value']) / cummax
        max_drawdown = drawdown.max() * 100
        
        # 卡尔玛比率 (年化收益/最大回撤)
        if max_drawdown > 0:
            calmar = annual_return / max_drawdown
        else:
            calmar = 0
        
        # 胜率
        winning_days = (returns > 0).sum()
        win_rate = winning_days / len(returns) * 100 if len(returns) > 0 else 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'calmar_ratio': calmar,
            'win_rate': win_rate,
            'trading_days': days
        }
    
    @staticmethod
    def generate_report(result):
        """
        生成回测报告
        
        Args:
            result: 回测结果
        
        Returns:
            str: 报告文本
        """
        report = f"""
{'='*50}
            量化策略回测报告
{'='*50}

策略名称: {result['strategy']}
初始资金: ¥{result['initial_capital']:,.2f}
最终价值: ¥{result['final_value']:,.2f}

{'='*50}
                  收益分析
{'='*50}
总收益率:    {result['total_return']:>10.2f}%
年化收益率:  {result['annual_return']:>10.2f}%

{'='*50}
                  风险分析
{'='*50}
最大回撤:    {result['max_drawdown']:>10.2f}%
夏普比率:    {result['sharpe_ratio']:>10.2f}

{'='*50}
                  交易统计
{'='*50}
交易次数:    {result['total_trades']:>10d}

{'='*50}
"""
        return report


if __name__ == '__main__':
    # 测试
    from data.data_loader import DataLoader
    from strategy.strategies import MomentumStrategy, RSIStrategy
    
    loader = DataLoader()
    data = loader.load_stock_data('1810.HK', '20240101', '20240601')
    data = loader.add_technical_indicators(data)
    
    # 创建回测引擎
    engine = BacktestEngine(data, initial_capital=100000)
    
    # 运行多策略
    strategies = [
        MomentumStrategy(lookback=20, threshold=0.05),
        MomentumStrategy(lookback=10, threshold=0.03),
        RSIStrategy(period=14, oversold=30, overbought=70)
    ]
    
    results = engine.run_multiple(strategures)
    print(results)
