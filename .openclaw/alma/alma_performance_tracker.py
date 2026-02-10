#!/usr/bin/env python3
"""
Performance Tracking Dashboard for ALMA Integration
Monitors real-time metrics and improvements
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List
import statistics


class PerformanceTracker:
    """
    Tracks performance metrics for ALMA integration
    """

    def __init__(self):
        self.db_path = '/home/majinbu/pi-mono-workspace/monitoring/performance_tracker.db'
        self._init_database()

    def _init_database(self):
        """Initialize performance tracking database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_category TEXT,
                metric_name TEXT,
                metric_value REAL,
                baseline REAL,
                improvement_pct REAL,
                deployment_id TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS baselines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT UNIQUE,
                baseline_value REAL,
                established_at TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                alert_type TEXT,
                severity TEXT,
                message TEXT,
                resolved BOOLEAN
            )
        ''')

        conn.commit()
        conn.close()

    def establish_baseline(self, metric_name: str, value: float):
        """Establish a baseline for a metric"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO baselines
            (metric_name, baseline_value, established_at)
            VALUES (?, ?, ?)
        ''', (metric_name, value, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        print(f"📏 Baseline established: {metric_name} = {value:.4f}")

    def record_metric(self, category: str, name: str, value: float, deployment_id: str = None):
        """Record a metric value"""
        # Get baseline
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT baseline_value FROM baselines WHERE metric_name = ?', (name,))
        baseline_row = cursor.fetchone()

        baseline = baseline_row[0] if baseline_row else value
        improvement = ((value - baseline) / baseline * 100) if baseline != 0 else 0.0

        # Record metric
        cursor.execute('''
            INSERT INTO metrics
            (timestamp, metric_category, metric_name, metric_value, baseline, improvement_pct, deployment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), category, name, value, baseline, improvement, deployment_id))

        conn.commit()
        conn.close()

        # Check improvement threshold
        if improvement > 5.0:
            print(f"📈 Improvement: {name} +{improvement:.1f}% (baseline: {baseline:.4f} → {value:.4f})")

        elif improvement < -5.0:
            print(f"📉 Degradation: {name} {improvement:.1f}% (baseline: {baseline:.4f} → {value:.4f})")

    def get_improvement_summary(self, hours: int = 24) -> Dict[str, Dict]:
        """Get improvement summary for recent period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                metric_category,
                metric_name,
                AVG(metric_value) as avg_value,
                AVG(baseline) as avg_baseline,
                AVG(improvement_pct) as avg_improvement,
                COUNT(*) as samples
            FROM metrics
            WHERE datetime(timestamp) > datetime('now', '-{} hours')
            GROUP BY metric_category, metric_name
        '''.format(hours))

        summary = {}
        for row in cursor.fetchall():
            category, name, avg_value, avg_baseline, avg_improvement, samples = row
            if category not in summary:
                summary[category] = {}

            summary[category][name] = {
                'current': avg_value,
                'baseline': avg_baseline,
                'improvement_pct': avg_improvement,
                'samples': samples
            }

        conn.close()
        return summary

    def trigger_alert(self, alert_type: str, severity: str, message: str):
        """Trigger an alert"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO alerts
            (timestamp, alert_type, severity, message, resolved)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), alert_type, severity, message, False))

        conn.commit()
        conn.close()

        severity_icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}
        icon = severity_icon.get(severity, '⚪')
        print(f"{icon} ALERT [{severity.upper()}]: {message}")

    def get_unresolved_alerts(self) -> List[Dict]:
        """Get all unresolved alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT timestamp, alert_type, severity, message
            FROM alerts
            WHERE resolved = FALSE
            ORDER BY timestamp DESC
        ''')

        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'timestamp': row[0],
                'type': row[1],
                'severity': row[2],
                'message': row[3]
            })

        conn.close()
        return alerts

    def print_dashboard(self):
        """Print performance dashboard"""
        print("\n" + "="*60)
        print("📊 ALMA PERFORMANCE DASHBOARD")
        print("="*60)

        # Get improvement summary
        summary = self.get_improvement_summary(hours=24)

        if not summary:
            print("  No recent metrics available")
        else:
            for category, metrics in summary.items():
                print(f"\n{category.upper()}:")
                for metric_name, data in metrics.items():
                    imp = data['improvement_pct']
                    icon = '📈' if imp > 0 else '📉' if imp < 0 else '➖'
                    print(f"  {icon} {metric_name}:")
                    print(f"      Current: {data['current']:.4f}")
                    print(f"      Baseline: {data['baseline']:.4f}")
                    print(f"      Change: {imp:+.1f}% ({data['samples']} samples)")

        # Check alerts
        alerts = self.get_unresolved_alerts()
        if alerts:
            print(f"\n⚠️  UNRESOLVED ALERTS ({len(alerts)}):")
            for alert in alerts[:5]:
                severity_icon = {'critical': '🔴', 'warning': '🟡', 'info': '🔵'}
                icon = severity_icon.get(alert['severity'], '⚪')
                print(f"  {icon} [{alert['timestamp']}] {alert['message']}")

        print("="*60)


def main():
    """Demo performance tracking"""
    print("📊 Performance Tracking Dashboard")
    print("="*60)

    tracker = PerformanceTracker()

    # Establish baselines
    tracker.establish_baseline('win_rate', 65.0)
    tracker.establish_baseline('avg_return', 2.5)
    tracker.establish_baseline('retrieval_latency', 50.0)

    # Record some metrics
    print("\n📝 Recording sample metrics...")
    tracker.record_metric('trading', 'win_rate', 70.5, 'deploy_001')
    tracker.record_metric('trading', 'avg_return', 3.2, 'deploy_001')
    tracker.record_metric('memory', 'retrieval_latency', 42.0, 'deploy_001')
    tracker.record_metric('trading', 'win_rate', 68.0, 'deploy_001')
    tracker.record_metric('trading', 'avg_return', 2.8, 'deploy_001')

    # Trigger an alert
    tracker.trigger_alert('degradation', 'warning', 'Win rate dropped 5% below baseline')

    # Print dashboard
    tracker.print_dashboard()

    print("\n✅ Performance tracking demo complete")


if __name__ == '__main__':
    main()
