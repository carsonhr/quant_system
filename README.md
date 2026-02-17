# Quant System - 量化回测系统

一个轻量级的量化交易回测系统，支持多种策略和风险管理。

## 功能特性

- 支持多种交易策略（动量、均值回归、RSI、MACD）
- 完整的回测引擎
- 风险指标分析
- 参数优化

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

print(result)
```

## 安装

```bash
pip install pandas numpy
```

## 目录结构

```
quant_system/
├── data/          # 数据模块
├── strategy/      # 策略模块
├── backtest/      # 回测模块
└── trading/       # 交易模块
```

## License

MIT
