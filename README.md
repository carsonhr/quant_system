# Quant System - 量化回测系统

一个轻量级的量化交易回测系统，支持多种策略和风险管理。

## 功能特性

### 策略模块
- ✅ 动量策略 (Momentum)
- ✅ 均值回归策略 (Mean Reversion)
- ✅ RSI 策略
- ✅ MACD 策略
- ✅ 多因子策略 (Multi-Factor)
- ✅ 配对交易策略 (Pairs Trading)
- ✅ Dual Thrust 策略
- ✅ 海龟交易策略 (Turtle)
- ✅ 网格交易策略 (Grid)

### 数据模块
- ✅ 模拟数据生成
- ✅ A股数据 (Akshare)
- ✅ 港股数据
- ✅ 美股数据
- ✅ 基本面数据

### 回测模块
- ✅ 回测引擎
- ✅ 风险指标分析
- ✅ 参数优化
- ✅ 多策略对比

### 分析模块
- ✅ 可视化 (K线、收益曲线、回撤)
- ✅ 报告生成

## 快速开始

```python
from quant_system.data import DataLoader
from quant_system.strategy import MomentumStrategy
from quant_system.backtest import BacktestEngine

# 加载数据
loader = DataLoader()
data = loader.load_stock_data('1810.HK', '20240101', '20240601')

# 创建策略
strategy = MomentumStrategy(lookback=20, threshold=0.05)

# 回测
engine = BacktestEngine(data)
result = engine.run(strategy)

print(f"总收益: {result['total_return']:.2f}%")
print(f"夏普比率: {result['sharpe_ratio']:.2f}")
print(f"最大回撤: {result['max_drawdown']:.2f}%")
```

## 目录结构

```
quant_system/
├── data/                    # 数据模块
│   ├── data_loader.py       # 数据加载
│   └── realtime_data.py     # 实时数据(Akshare)
│
├── strategy/               # 策略模块
│   ├── strategies.py       # 基础策略
│   └── advanced_strategies.py  # 高级策略
│
├── backtest/             # 回测模块
│   └── engine.py         # 回测引擎
│
└── analysis/            # 分析模块
    └── visualizer.py    # 可视化
```

## 安装

```bash
pip install pandas numpy matplotlib akshare
```

## 风险指标

| 指标 | 说明 | 优秀 |
|------|------|------|
| 年化收益 | 策略年化收益率 | >20% |
| 夏普比率 | 风险调整收益 | >1.5 |
| 最大回撤 | 最大亏损幅度 | <20% |
| 胜率 | 盈利交易比例 | >50% |
| 盈亏比 | 平均盈利/亏损 | >1.5 |

## 示例策略

### 动量策略
```python
strategy = MomentumStrategy(lookback=20, threshold=0.05)
```

### RSI 策略
```python
strategy = RSIStrategy(period=14, oversold=30, overbought=70)
```

### 多因子策略
```python
strategy = MultiFactorStrategy(
    factors=['pe', 'pb', 'roe', 'momentum'],
    weights=[0.25, 0.25, 0.25, 0.25]
)
```

## 注意事项

1. 回测结果不代表实盘收益
2. 需考虑滑点和交易成本
3. 避免过度拟合
4. 建议用模拟盘验证

## License

MIT
