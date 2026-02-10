#!/usr/bin/env python3
"""
ALMA Consensus - Improved Version
- Uses centralized config
- Added comprehensive docstrings
- Refactored for clarity
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import configuration (handle both module and standalone usage)
try:
    from . import alma_config as cfg
except ImportError:
    # Standalone usage - add monitoring to path
    MONITORING_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(MONITORING_DIR))
    import alma_config as cfg


class ALMAConsensus:
    """
    ALMA-Enhanced Consensus Manager for trading system.

    This class manages dynamic consensus weights for trading strategies,
    using ALMA meta-learned performance data to adjust strategy weights
    in real-time. Falls back to static equal weights when ALMA is unavailable.

    Attributes:
        enabled (bool): Whether ALMA consensus is enabled
        memory (TradingMemory): Trading memory instance (if enabled)
        static_weights (Dict[str, float]): Fallback static weights

    Example:
        >>> from alma_consensus import get_consensus
        >>> consensus = get_consensus()
        >>> weights = consensus.get_weights(['StrategyA', 'StrategyB'])
        >>> print(weights)
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize ALMA Consensus manager.

        Args:
            enabled: Enable ALMA dynamic weights (default: True)
        """
        self.enabled = enabled and self._check_alma_available()
        self.memory = self._init_memory() if self.enabled else None
        self.static_weights = self._load_static_weights()

        if self.enabled:
            logging.info("🧠 ALMA consensus enabled - dynamic weights active")
        else:
            logging.info("⚠️  ALMA consensus disabled - using static weights")

    def _check_alma_available(self) -> bool:
        """Check if ALMA trading memory is available."""
        try:
            from .alma_trading_adapter_v2 import TradingMemory
            return True
        except ImportError as e:
            logging.warning(f"ALMA modules not available: {e}")
            return False

    def _init_memory(self):
        """Initialize trading memory connection."""
        from .alma_trading_adapter_v2 import TradingMemory
        return TradingMemory(cfg.ALMA_TRADING_MEMORY_DB)

    def _load_static_weights(self) -> Dict[str, float]:
        """
        Load static equal weights for all strategies.

        Returns:
            Dict mapping strategy names to equal weights (1/N)
        """
        strategies = cfg.STRATEGIES
        count = len(strategies)
        return {s: 1.0 / count for s in strategies}

    def get_weights(self, active_strategies: List[str]) -> Dict[str, float]:
        """
        Get consensus weights for active strategies.

        Returns ALMA dynamic weights if available, otherwise falls back
        to static equal weights.

        Args:
            active_strategies: List of active strategy names

        Returns:
            Dict mapping strategy names to weights (sum to 1.0)

        Example:
            >>> weights = consensus.get_weights(['TV_Screener', 'TrendCapture'])
            >>> print(weights['TV_Screener'])
            0.5176
        """
        if not self.enabled:
            return self._get_equal_weights(active_strategies)

        try:
            weights = self.memory.compute_dynamic_weights(active_strategies)

            if weights and len(weights) == len(active_strategies):
                return weights
            else:
                return self._get_static_weights_subset(active_strategies)

        except Exception as e:
            logging.error(f"ALMA weight computation failed: {e}")
            return self._get_equal_weights(active_strategies)

    def _get_equal_weights(self, strategies: List[str]) -> Dict[str, float]:
        """Return equal weights for all strategies."""
        count = len(strategies)
        return {s: 1.0 / count for s in strategies}

    def _get_static_weights_subset(self, strategies: List[str]) -> Dict[str, float]:
        """Get static weights for a subset of strategies."""
        default_weight = 1.0 / len(strategies)
        return {
            s: self.static_weights.get(s, default_weight)
            for s in strategies
        }

    def record_performance(self, strategy: str, metrics: Dict):
        """
        Record strategy performance for meta-learning.

        Args:
            strategy: Strategy name
            metrics: Dict with keys: win_rate, avg_return, max_drawdown,
                     num_trades, regime

        Example:
            >>> consensus.record_performance('TV_Screener', {
            ...     'win_rate': 75.0,
            ...     'avg_return': 3.5,
            ...     'max_drawdown': -2.0,
            ...     'num_trades': 50,
            ...     'regime': 'BREAKOUT'
            ... })
        """
        if not self.enabled or not self.memory:
            return

        try:
            self.memory.update_strategy_performance(strategy, metrics)
            logging.debug(f"Recorded performance for {strategy}")
        except Exception as e:
            logging.error(f"Failed to record performance for {strategy}: {e}")

    def get_best_strategies(
        self,
        limit: int = 5,
        regime: Optional[str] = None
    ) -> List[Dict]:
        """
        Get top performing strategies.

        Args:
            limit: Maximum number of strategies to return
            regime: Filter by market regime (optional)

        Returns:
            List of dicts with strategy, win_rate, avg_return, etc.
        """
        if not self.enabled or not self.memory:
            return []

        try:
            return self.memory.get_best_strategies(limit=limit, regime=regime)
        except Exception as e:
            logging.error(f"Failed to get best strategies: {e}")
            return []

    def get_status(self) -> Dict:
        """
        Get consensus system status.

        Returns:
            Dict with status info: enabled, mode, memory_connected, etc.
        """
        return {
            'enabled': self.enabled,
            'mode': 'dynamic' if self.enabled else 'static',
            'memory_connected': self.memory is not None,
            'static_weights_count': len(self.static_weights)
        }


# Singleton instance
_consensus_instance: Optional[ALMAConsensus] = None


def get_consensus(enabled: bool = True, force_refresh: bool = False) -> ALMAConsensus:
    """
    Get singleton consensus instance.

    Args:
        enabled: Enable ALMA (default: True)
        force_refresh: Force recreation of instance (default: False)

    Returns:
        ALMAConsensus instance

    Example:
        >>> consensus = get_consensus()
        >>> weights = consensus.get_weights(['StrategyA'])
    """
    global _consensus_instance

    if _consensus_instance is None or force_refresh:
        _consensus_instance = ALMAConsensus(enabled=enabled)

    return _consensus_instance


def compute_weighted_vote(
    votes: Dict[str, float],
    strategy_names: List[str]
) -> float:
    """
    Compute weighted vote sum using ALMA dynamic weights.

    Args:
        votes: Dict mapping strategy names to vote values (-1 to 1)
        strategy_names: List of active strategy names

    Returns:
        Weighted vote sum (typically -1 to 1 range)

    Example:
        >>> votes = {'TV_Screener': 0.8, 'TrendCapture': 0.6}
        >>> weighted = compute_weighted_vote(votes, list(votes.keys()))
        >>> print(f"Weighted consensus: {weighted:.3f}")
    """
    consensus = get_consensus()
    weights = consensus.get_weights(strategy_names)

    weighted_sum = sum(
        weights.get(name, 1.0 / len(strategy_names)) * votes.get(name, 0.0)
        for name in strategy_names
    )

    return weighted_sum


def reset_consensus():
    """Reset singleton consensus instance."""
    global _consensus_instance
    _consensus_instance = None
    logging.info("Consensus instance reset")


# Allow standalone usage
if __name__ == '__main__':
    # Demo
    logging.basicConfig(level=logging.INFO)

    consensus = get_consensus()

    print("🧠 ALMA Consensus Demo")
    print("="*60)

    # Get status
    status = consensus.get_status()
    print(f"Status: {status}")

    # Get weights for some strategies
    test_strategies = ['TV_Screener', 'TrendCapturePro', 'DivergenceVolatilityEnhanced']
    weights = consensus.get_weights(test_strategies)

    print(f"\nDynamic weights:")
    for name, weight in weights.items():
        print(f"  {name}: {weight:.4f} ({weight*100:.1f}%)")

    # Compute weighted vote
    votes = {s: 0.7 for s in test_strategies}
    weighted = compute_weighted_vote(votes, test_strategies)

    print(f"\nWeighted vote: {weighted:.3f}")
