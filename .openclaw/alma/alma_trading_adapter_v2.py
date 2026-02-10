#!/usr/bin/env python3
"""
ALMA Memory Adapter for Trading V7 System
Integrates meta-learned memory designs with trading strategies
"""

import sqlite3
from datetime import datetime
from typing import Dict, List
import json
import os


class TradingMemory:
    """
    ALMA-optimized memory for trading system
    Stores strategy performance, market regimes, and signal history
    """

    def __init__(self, db_path: str = None):
        # Use monitoring directory for write access
        self.db_path = db_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'alma_trading_memory.db'
        )
        self._init_database()

    def _init_database(self):
        """Initialize trading memory tables"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Strategy performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS strategy_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                timestamp TEXT,
                win_rate REAL,
                avg_return REAL,
                max_drawdown REAL,
                num_trades INTEGER,
                regime TEXT,
                UNIQUE(strategy_name, timestamp)
            )
        ''')

        # Market regime detection
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_regimes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                regime TEXT NOT NULL,
                confidence REAL,
                features TEXT,
                duration_hours INTEGER
            )
        ''')

        # Signal accuracy history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy TEXT,
                timestamp TEXT,
                signal TEXT,
                actual_outcome REAL,
                accuracy REAL,
                market_condition TEXT
            )
        ''')

        # Memory template (meta-learned)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_template (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                design_id TEXT,
                template_code TEXT,
                performance_metrics TEXT,
                active BOOLEAN,
                created_at TEXT,
                last_updated TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def update_strategy_performance(self, strategy_name: str, metrics: Dict):
        """Record strategy performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO strategy_performance
            (strategy_name, timestamp, win_rate, avg_return, max_drawdown, num_trades, regime)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            strategy_name,
            datetime.now().isoformat(),
            metrics.get('win_rate', 0.0),
            metrics.get('avg_return', 0.0),
            metrics.get('max_drawdown', 0.0),
            metrics.get('num_trades', 0),
            metrics.get('regime', 'unknown')
        ))

        conn.commit()
        conn.close()

    def get_best_strategies(self, limit: int = 5, regime: str = None) -> List[Dict]:
        """Retrieve top performing strategies, optionally filtered by regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if regime:
            cursor.execute('''
                SELECT strategy_name, win_rate, avg_return, max_drawdown, num_trades
                FROM strategy_performance
                WHERE regime = ?
                ORDER BY win_rate DESC, avg_return DESC
                LIMIT ?
            ''', (regime, limit))
        else:
            cursor.execute('''
                SELECT strategy_name, win_rate, avg_return, max_drawdown, num_trades
                FROM strategy_performance
                ORDER BY win_rate DESC, avg_return DESC
                LIMIT ?
            ''', (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'strategy': row[0],
                'win_rate': row[1],
                'avg_return': row[2],
                'max_drawdown': row[3],
                'num_trades': row[4]
            })

        conn.close()
        return results

    def record_regime(self, regime: str, confidence: float, features: Dict = None):
        """Record detected market regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO market_regimes
            (timestamp, regime, confidence, features)
            VALUES (?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            regime,
            confidence,
            json.dumps(features) if features else None
        ))

        conn.commit()
        conn.close()

    def get_current_regime(self, hours: int = 24) -> Dict:
        """Get most recent market regime"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT regime, confidence, features, timestamp
            FROM market_regimes
            WHERE datetime(timestamp) > datetime('now', '-{} hours')
            ORDER BY timestamp DESC
            LIMIT 1
        '''.format(hours))

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'regime': row[0],
                'confidence': row[1],
                'features': json.loads(row[2]) if row[2] else None,
                'timestamp': row[3]
            }
        return None

    def compute_dynamic_weights(self, strategies: List[str]) -> Dict[str, float]:
        """
        ALMA-style: Compute dynamic consensus weights based on historical performance
        Returns weights that sum to 1.0
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        weights = {}
        total_score = 0.0

        for strategy in strategies:
            cursor.execute('''
                SELECT win_rate, avg_return, num_trades
                FROM strategy_performance
                WHERE strategy_name = ?
                ORDER BY timestamp DESC
                LIMIT 10
            ''', (strategy,))

            rows = cursor.fetchall()
            if rows:
                # Weight by recent performance
                recent_win_rate = sum(r[0] for r in rows) / len(rows)
                recent_return = sum(r[1] for r in rows) / len(rows)
                num_trades = rows[0][2]

                # ALMA-inspired scoring
                score = (recent_win_rate * 0.5 +
                        recent_return * 0.3 +
                        min(num_trades / 100, 1.0) * 0.2)
                weights[strategy] = max(score, 0.0)
                total_score += weights[strategy]
            else:
                weights[strategy] = 0.1  # Default weight

        conn.close()

        # Normalize
        if total_score > 0:
            for k in weights:
                weights[k] /= total_score

        return weights

    def save_memory_template(self, design_id: str, template_code: str, metrics: Dict):
        """Save a meta-learned memory template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO memory_template
            (design_id, template_code, performance_metrics, active, created_at, last_updated)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            design_id,
            template_code,
            json.dumps(metrics),
            True,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

    def get_active_template(self) -> Dict:
        """Get currently active memory template"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT design_id, template_code, performance_metrics, last_updated
            FROM memory_template
            WHERE active = TRUE
            ORDER BY last_updated DESC
            LIMIT 1
        ''')

        row = cursor.fetchone()
        conn.close()

        if row:
            return {
                'design_id': row[0],
                'template_code': row[1],
                'metrics': json.loads(row[2]),
                'last_updated': row[3]
            }
        return None

    def get_stats(self) -> Dict:
        """Get memory statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        cursor.execute('SELECT COUNT(*) FROM strategy_performance')
        stats['total_performance_records'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(DISTINCT strategy_name) FROM strategy_performance')
        stats['unique_strategies'] = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM signal_history')
        stats['total_signals'] = cursor.fetchone()[0]

        cursor.execute('SELECT AVG(win_rate) FROM strategy_performance')
        avg = cursor.fetchone()[0]
        stats['avg_win_rate'] = avg if avg else 0.0

        conn.close()
        return stats


def main():
    """Demo trading memory functionality"""
    print("🧠 ALMA Trading Memory Adapter")
    print("="*60)

    memory = TradingMemory()

    # Add some sample performance data
    sample_strategies = [
        ('DivergenceVolatility', 65.0, 2.5, -5.0, 100, 'TRENDING'),
        ('SelectiveMomentum', 60.0, 1.8, -3.5, 85, 'RANGING'),
        ('TrendCapturePro', 70.0, 3.2, -4.0, 120, 'TRENDING'),
        ('TV_Screener', 75.0, 4.0, -2.0, 50, 'BREAKOUT'),
    ]

    print("📊 Adding sample strategy performance...")
    for strat in sample_strategies:
        metrics = {
            'win_rate': strat[1],
            'avg_return': strat[2],
            'max_drawdown': strat[3],
            'num_trades': strat[4],
            'regime': strat[5]
        }
        memory.update_strategy_performance(strat[0], metrics)
        print(f"  ✅ {strat[0]}: {strat[1]}% win rate")

    # Get best strategies
    print("\n🏆 Top 3 strategies:")
    best = memory.get_best_strategies(limit=3)
    for i, s in enumerate(best, 1):
        print(f"  {i}. {s['strategy']}: {s['win_rate']:.1f}%")

    # Compute dynamic weights
    strategies = [strat[0] for strat in sample_strategies]
    weights = memory.compute_dynamic_weights(strategies)
    print("\n⚖️  Dynamic consensus weights:")
    for strat, weight in weights.items():
        print(f"  {strat}: {weight:.3f} ({weight*100:.1f}%)")

    # Stats
    stats = memory.get_stats()
    print(f"\n📈 Memory stats:")
    print(f"  Performance records: {stats['total_performance_records']}")
    print(f"  Unique strategies: {stats['unique_strategies']}")
    print(f"  Average win rate: {stats['avg_win_rate']:.1f}%")

    print("\n" + "="*60)
    print("✅ ALMA Trading Memory Ready")


if __name__ == '__main__':
    main()
