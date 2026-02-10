#!/usr/bin/env python3
"""
ALMA Consolidated Modules
Imports all ALMA modules for easy access
"""

from .alma_config import *
from .alma_meta_agent import MetaLearningAgent, MemoryDesign
from .alma_trading_adapter_v2 import TradingMemory
from .alma_consensus_v2 import ALMAConsensus, get_consensus, compute_weighted_vote
from .alma_performance_tracker import PerformanceTracker
from .alma_ab_testing import ABTest, RollbackSafety

__all__ = [
    # Config
    'BASE_DIR', 'MONITORING_DIR', 'MEMORY_DIR',
    'ALMA_DESIGNS_DB', 'ALMA_TRADING_MEMORY_DB',
    'STRATEGIES', 'ALMA_WEIGHTS',
    # Core
    'MetaLearningAgent', 'MemoryDesign',
    'TradingMemory',
    'ALMAConsensus', 'get_consensus', 'compute_weighted_vote',
    'PerformanceTracker', 'ABTest', 'RollbackSafety',
]

__version__ = '2.0.0'
