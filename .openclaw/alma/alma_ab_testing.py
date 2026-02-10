#!/usr/bin/env python3
"""
A/B Testing Framework for ALMA Memory Designs
Compares meta-learned vs static memory approaches
"""

import sqlite3
import time
import json
from datetime import datetime
from typing import Dict, List, Tuple
import statistics


class ABTest:
    """
    A/B test for memory design comparison
    """

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.db_path = '/home/majinbu/pi-mono-workspace/monitoring/ab_tests.db'
        self._init_database()

    def _init_database(self):
        """Initialize A/B test database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_name TEXT NOT NULL,
                variant_a TEXT,
                variant_b TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT,
                winner TEXT,
                confidence REAL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER,
                variant TEXT,
                metric_name TEXT,
                metric_value REAL,
                timestamp TEXT,
                FOREIGN KEY (test_id) REFERENCES tests(id)
            )
        ''')

        conn.commit()
        conn.close()

    def start_test(self, variant_a: str, variant_b: str) -> int:
        """Start a new A/B test"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        test_id = cursor.execute('''
            INSERT INTO tests
            (test_name, variant_a, variant_b, start_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.test_name, variant_a, variant_b, datetime.now().isoformat(), 'running')).lastrowid

        conn.commit()
        conn.close()

        print(f"🧪 A/B Test started: {self.test_name}")
        print(f"   Variant A: {variant_a}")
        print(f"   Variant B: {variant_b}")
        print(f"   Test ID: {test_id}")

        return test_id

    def record_metric(self, test_id: int, variant: str, metric_name: str, value: float):
        """Record a metric for a variant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO metrics
            (test_id, variant, metric_name, metric_value, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (test_id, variant, metric_name, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_variant_metrics(self, test_id: int, variant: str) -> List[float]:
        """Get all metrics for a variant"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT metric_value
            FROM metrics
            WHERE test_id = ? AND variant = ?
            ORDER BY timestamp
        ''', (test_id, variant))

        values = [row[0] for row in cursor.fetchall()]
        conn.close()
        return values

    def analyze_results(self, test_id: int) -> Dict:
        """
        Analyze A/B test results
        Returns winner and confidence
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get test info
        cursor.execute('SELECT variant_a, variant_b FROM tests WHERE id = ?', (test_id,))
        test_info = cursor.fetchone()
        if not test_info:
            return None

        variant_a, variant_b = test_info

        # Get metrics for each variant
        a_values = self.get_variant_metrics(test_id, variant_a)
        b_values = self.get_variant_metrics(test_id, variant_b)

        if not a_values or not b_values:
            return {'status': 'insufficient_data'}

        # Statistical comparison (simplified)
        a_mean = statistics.mean(a_values)
        b_mean = statistics.mean(b_values)

        a_std = statistics.stdev(a_values) if len(a_values) > 1 else 0
        b_std = statistics.stdev(b_values) if len(b_values) > 1 else 0

        # Effect size (Cohen's d)
        pooled_std = ((a_std**2 + b_std**2) / 2) ** 0.5
        effect_size = (b_mean - a_mean) / pooled_std if pooled_std > 0 else 0

        # Confidence (simplified)
        confidence = min(abs(effect_size) / 0.5, 1.0) * 100

        # Determine winner
        if abs(a_mean - b_mean) < (pooled_std * 0.1):
            winner = 'no_significant_difference'
        else:
            winner = variant_b if b_mean > a_mean else variant_a

        result = {
            'status': 'complete',
            'variant_a': variant_a,
            'variant_b': variant_b,
            'a_mean': a_mean,
            'b_mean': b_mean,
            'a_std': a_std,
            'b_std': b_std,
            'effect_size': effect_size,
            'confidence': confidence,
            'winner': winner
        }

        # Save results
        cursor.execute('''
            UPDATE tests
            SET end_time = ?, status = ?, winner = ?, confidence = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), 'complete', winner, confidence, test_id))

        conn.commit()
        conn.close()

        return result

    def print_results(self, result: Dict):
        """Print A/B test results"""
        print("\n" + "="*60)
        print("🧪 A/B TEST RESULTS")
        print("="*60)
        print(f"Variant A ({result['variant_a']}):")
        print(f"  Mean: {result['a_mean']:.4f}")
        print(f"  Std:  {result['a_std']:.4f}")
        print()
        print(f"Variant B ({result['variant_b']}):")
        print(f"  Mean: {result['b_mean']:.4f}")
        print(f"  Std:  {result['b_std']:.4f}")
        print()
        print(f"Effect Size: {result['effect_size']:.4f}")
        print(f"Confidence: {result['confidence']:.1f}%")
        print(f"Winner: {result['winner'].upper()}")
        print("="*60)


class RollbackSafety:
    """
    Automatic rollback safety for ALMA deployments
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or '/home/majinbu/pi-mono-workspace/monitoring/rollback_safety.db'
        self.degradation_threshold = 0.1  # 10% degradation triggers rollback
        self._init_database()

    def _init_database(self):
        """Initialize rollback safety database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deployments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT,
                timestamp TEXT,
                baseline_score REAL,
                current_score REAL,
                status TEXT,
                rolled_back BOOLEAN
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deployment_id TEXT,
                metric_name TEXT,
                value REAL,
                timestamp TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def record_deployment(self, deployment_id: str, baseline_score: float):
        """Record a new deployment with baseline"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO deployments
            (deployment_id, timestamp, baseline_score, current_score, status, rolled_back)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (deployment_id, datetime.now().isoformat(), baseline_score, baseline_score, 'active', False))

        conn.commit()
        conn.close()

        print(f"📦 Deployment recorded: {deployment_id}")
        print(f"   Baseline score: {baseline_score:.4f}")

    def record_metric(self, deployment_id: str, metric_name: str, value: float):
        """Record a metric for a deployment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO metrics_history
            (deployment_id, metric_name, value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (deployment_id, metric_name, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def check_degradation(self, deployment_id: str) -> Dict:
        """
        Check if current deployment shows degradation
        Returns recommendation: 'continue', 'rollback', or 'warn'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get baseline
        cursor.execute('''
            SELECT baseline_score FROM deployments
            WHERE deployment_id = ? AND status = 'active'
        ''', (deployment_id,))

        result = cursor.fetchone()
        if not result:
            return {'recommendation': 'not_found'}

        baseline = result[0]

        # Get recent metrics
        cursor.execute('''
            SELECT value FROM metrics_history
            WHERE deployment_id = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (deployment_id,))

        recent = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not recent:
            return {'recommendation': 'insufficient_data', 'baseline': baseline}

        current_avg = statistics.mean(recent[-5:])  # Last 5 metrics

        # Calculate degradation
        degradation = (baseline - current_avg) / baseline if baseline > 0 else 0

        recommendation = 'continue'
        if degradation > self.degradation_threshold:
            recommendation = 'rollback'
        elif degradation > self.degradation_threshold * 0.5:
            recommendation = 'warn'

        return {
            'recommendation': recommendation,
            'baseline': baseline,
            'current': current_avg,
            'degradation': degradation,
            'threshold': self.degradation_threshold
        }

    def rollback_deployment(self, deployment_id: str):
        """Rollback a deployment"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE deployments
            SET status = 'rolled_back', rolled_back = TRUE
            WHERE deployment_id = ?
        ''', (deployment_id,))

        conn.commit()
        conn.close()

        print(f"🔄 Rollback triggered: {deployment_id}")


def main():
    """Demo A/B testing and rollback safety"""
    print("🧪 A/B Testing & Rollback Safety")
    print("="*60)

    # A/B Test Demo
    ab_test = ABTest('Dynamic_vs_Static_Weights')
    test_id = ab_test.start_test('Static Weights', 'ALMA Dynamic Weights')

    # Record some sample metrics
    for i in range(10):
        ab_test.record_metric(test_id, 'Static Weights', 'win_rate', 65.0 + i)
        ab_test.record_metric(test_id, 'ALMA Dynamic Weights', 'win_rate', 70.0 + i)

    # Analyze
    result = ab_test.analyze_results(test_id)
    ab_test.print_results(result)

    # Rollback Safety Demo
    print("\n" + "="*60)
    print("🛡️  Rollback Safety Demo")
    print("="*60)

    safety = RollbackSafety()
    safety.record_deployment('deploy_001', 0.7500)

    # Record metrics
    for i in range(10):
        value = 0.7500 - (i * 0.005)  # Gradual degradation
        safety.record_metric('deploy_001', 'accuracy', value)

    # Check
    check = safety.check_degradation('deploy_001')
    print(f"\nDegradation check:")
    print(f"  Baseline: {check['baseline']:.4f}")
    print(f"  Current: {check['current']:.4f}")
    print(f"  Degradation: {check['degradation']:.2%}")
    print(f"  Recommendation: {check['recommendation'].upper()}")

    if check['recommendation'] == 'rollback':
        safety.rollback_deployment('deploy_001')
        print("  ✅ Rollback executed")

    print("\n" + "="*60)
    print("✅ A/B Testing & Rollback Safety Demo Complete")
    print("="*60)


if __name__ == '__main__':
    main()
