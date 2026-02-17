"""
可视化模块
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import io
import base64


class Visualizer:
    """可视化模块"""
    
    def __init__(self, style='seaborn-v0_8-darkgrid'):
        try:
            plt.style.use(style)
        except:
            plt.style.use('ggplot')
        plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    
    def plot_portfolio(self, portfolio_df, title='组合价值走势'):
        """
        绘制组合价值走势图
        
        Args:
            portfolio_df: 包含 'date', 'value' 列的 DataFrame
            title: 图表标题
        
        Returns:
            base64 encoded image
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(portfolio_df['date'], portfolio_df['value'], linewidth=2, label='组合价值')
        ax.fill_between(portfolio_df['date'], portfolio_df['value'], alpha=0.3)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel('价值', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 格式化日期
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # 转换为 base64
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_base64
    
    def plot_returns(self, portfolio_df, title='收益分析'):
        """绘制收益分析图"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. 累计收益
        ax1 = axes[0, 0]
        portfolio_df['cumulative_return'] = (1 + portfolio_df['returns']).cumprod() - 1
        ax1.plot(portfolio_df.index, portfolio_df['cumulative_return'] * 100, linewidth=2)
        ax1.set_title('累计收益率', fontsize=12)
        ax1.set_ylabel('收益率 (%)')
        ax1.grid(True, alpha=0.3)
        ax1.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        
        # 2. 回撤曲线
        ax2 = axes[0, 1]
        portfolio_df['cummax'] = portfolio_df['value'].cummax()
        portfolio_df['drawdown'] = (portfolio_df['cummax'] - portfolio_df['value']) / portfolio_df['cummax'] * 100
        ax2.fill_between(portfolio_df.index, portfolio_df['drawdown'], alpha=0.5, color='red')
        ax2.set_title('回撤曲线', fontsize=12)
        ax2.set_ylabel('回撤 (%)')
        ax2.grid(True, alpha=0.3)
        
        # 3. 月收益分布
        ax3 = axes[1, 0]
        if 'date' in portfolio_df.columns:
            portfolio_df['month'] = pd.to_datetime(portfolio_df['date']).dt.month
            monthly_returns = portfolio_df.groupby('month')['returns'].mean() * 100
            ax3.bar(monthly_returns.index, monthly_returns.values, color='steelblue')
            ax3.set_title('月平均收益率', fontsize=12)
            ax3.set_xlabel('月份')
            ax3.set_ylabel('收益率 (%)')
            ax3.grid(True, alpha=0.3)
        
        # 4. 收益分布
        ax4 = axes[1, 1]
        returns = portfolio_df['returns'].dropna() * 100
        ax4.hist(returns, bins=50, color='steelblue', alpha=0.7, edgecolor='white')
        ax4.axvline(x=returns.mean(), color='r', linestyle='--', label=f'均值: {returns.mean():.2f}%')
        ax4.set_title('日收益率分布', fontsize=12)
        ax4.set_xlabel('收益率 (%)')
        ax4.set_ylabel('频次')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_base64
    
    def plot_strategy_comparison(self, results_df, title='策略对比'):
        """策略对比图"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # 1. 收益对比
        ax1 = axes[0]
        ax1.barh(results_df['strategy'], results_df['total_return'], color='steelblue')
        ax1.set_title('总收益率对比', fontsize=12)
        ax1.set_xlabel('收益率 (%)')
        ax1.grid(True, alpha=0.3, axis='x')
        
        # 2. 夏普比率对比
        ax2 = axes[1]
        colors = ['green' if x > 1 else 'orange' if x > 0 else 'red' for x in results_df['sharpe_ratio']]
        ax2.barh(results_df['strategy'], results_df['sharpe_ratio'], color=colors)
        ax2.set_title('夏普比率对比', fontsize=12)
        ax2.set_xlabel('夏普比率')
        ax2.axvline(x=1, color='r', linestyle='--', alpha=0.5)
        ax2.grid(True, alpha=0.3, axis='x')
        
        # 3. 最大回撤对比
        ax3 = axes[2]
        ax3.barh(results_df['strategy'], results_df['max_drawdown'], color='coral')
        ax3.set_title('最大回撤对比', fontsize=12)
        ax3.set_xlabel('回撤 (%)')
        ax3.grid(True, alpha=0.3, axis='x')
        
        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_base64
    
    def plot_technical(self, data, signals=None, title='技术分析'):
        """
        绘制技术分析图
        
        Args:
            data: OHLCV 数据
            signals: 信号数据
        """
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={'height_ratios': [3, 1, 1]})
        
        # 1. 价格和均线
        ax1 = axes[0]
        ax1.plot(data.index, data['close'], label='收盘价', linewidth=1.5)
        if 'MA5' in data.columns:
            ax1.plot(data.index, data['MA5'], label='MA5', alpha=0.7)
        if 'MA10' in data.columns:
            ax1.plot(data.index, data['MA10'], label='MA10', alpha=0.7)
        if 'MA20' in data.columns:
            ax1.plot(data.index, data['MA20'], label='MA20', alpha=0.7)
        
        # 标记买入信号
        if signals is not None:
            buy_signals = signals[signals['signal'] == 1]
            ax1.scatter(buy_signals.index, buy_signals['close'], 
                       marker='^', color='green', s=100, label='买入', zorder=5)
            
            sell_signals = signals[signals['signal'] == -1]
            ax1.scatter(sell_signals.index, sell_signals['close'], 
                       marker='v', color='red', s=100, label='卖出', zorder=5)
        
        ax1.set_title(title, fontsize=14, fontweight='bold')
        ax1.set_ylabel('价格')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 2. 成交量
        ax2 = axes[1]
        ax2.bar(data.index, data['volume'], color='steelblue', alpha=0.7)
        ax2.set_ylabel('成交量')
        ax2.grid(True, alpha=0.3)
        
        # 3. 技术指标 (RSI)
        ax3 = axes[2]
        if 'RSI' in data.columns:
            ax3.plot(data.index, data['RSI'], label='RSI', color='purple')
            ax3.axhline(y=70, color='r', linestyle='--', alpha=0.5)
            ax3.axhline(y=30, color='g', linestyle='--', alpha=0.5)
            ax3.fill_between(data.index, 30, 70, alpha=0.1, color='gray')
            ax3.set_ylabel('RSI')
            ax3.set_ylim(0, 100)
        
        ax3.set_xlabel('日期')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        img_buffer = io.BytesIO()
        plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
        img_buffer.seek(0)
        img_base64 = base64.b64encode(img_buffer.read()).decode()
        plt.close()
        
        return img_base64
    
    def save_plot(self, img_base64, filepath):
        """保存图片到文件"""
        img_data = base64.b64decode(img_base64)
        with open(filepath, 'wb') as f:
            f.write(img_data)
        print(f"图片已保存到: {filepath}")


if __name__ == '__main__':
    # 测试
    import pandas as pd
    import numpy as np
    
    # 模拟数据
    dates = pd.date_range('2024-01-01', '2024-06-01', freq='D')
    np.random.seed(42)
    
    portfolio_df = pd.DataFrame({
        'date': dates,
        'value': 100000 * (1 + np.random.randn(len(dates)).cumsum() * 0.02),
        'returns': np.random.randn(len(dates)) * 0.02
    })
    
    viz = Visualizer()
    
    # 测试组合走势图
    img = viz.plot_portfolio(portfolio_df)
    print(f"图片长度: {len(img)} 字符")
