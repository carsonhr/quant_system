"""
量化回测系统
Quantitative Trading Backtest System
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .backtest import BacktestEngine
from .strategy import BaseStrategy, MomentumStrategy, MeanReversionStrategy
from .data import DataLoader

__all__ = [
    'BacktestEngine',
    'BaseStrategy', 
    'MomentumStrategy',
    'MeanReversionStrategy',
    'DataLoader',
]
