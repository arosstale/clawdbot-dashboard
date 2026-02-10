# ALMA Configuration
# Centralized configuration for all ALMA components

# Base paths
BASE_DIR = "/home/majinbu/pi-mono-workspace"
MONITORING_DIR = f"{BASE_DIR}/monitoring"
MEMORY_DIR = f"{BASE_DIR}/memory"
LOG_DIR = f"{BASE_DIR}/logs"

# V7 paths
V7_DIR = "/home/majinbu/hl-trading-agent-private/hl-trading-agent"
V7_DB_PATH = f"{V7_DIR}/paper_trades.db"
V7_LAUNCH_SCRIPT = f"{V7_DIR}/launch_paper_trading_v7.py"
V7_BACKUP_PATH = f"{V7_DIR}/launch_paper_trading_v7.py.alma_backup"

# Database paths
ALMA_DESIGNS_DB = f"{MONITORING_DIR}/alma_designs.db"
ALMA_TRADING_MEMORY_DB = f"{MONITORING_DIR}/alma_trading_memory.db"
ALMA_AB_TESTS_DB = f"{MONITORING_DIR}/ab_tests.db"
ALMA_PERFORMANCE_TRACKER_DB = f"{MONITORING_DIR}/performance_tracker.db"
ALMA_ROLLBACK_SAFETY_DB = f"{MONITORING_DIR}/rollback_safety.db"

# Log paths
ALMA_V7_SYNC_LOG = f"{LOG_DIR}/alma_v7_sync.log"
ALMA_AB_TEST_LOG = f"{LOG_DIR}/alma_ab_test.log"
ALMA_PERF_LOG = f"{LOG_DIR}/alma_perf.log"
ALMA_AUDIT_LOG = f"{LOG_DIR}/alma_audit.log"

# Trading strategies (V7)
STRATEGIES = [
    'DivergenceVolatilityEnhanced',
    'SelectiveMomentumSwing',
    'TrendCapturePro',
    'SupertrendNovaCloud',
    'VolatilityBreakoutSystem',
    'BTC_Trend_Pullback',
    'MeanReversion_Bollinger',
    'Momentum_SMA_Cross',
    'RSI_Divergence',
    'TV_Screener',
    'Liquidator',
    'RenaissanceAI'
]

# ALMA meta-learning settings
ALMA_WEIGHTS = {
    'accuracy': 0.4,
    'compression': 0.2,
    'speed': 0.2,
    'success': 0.2
}

ALMA_SCORING = {
    'win_rate': 0.5,
    'avg_return': 0.3,
    'trade_volume': 0.2
}

# Consensus settings
CONSENSUS_THRESHOLD = 2  # Minimum strategies to agree
CONFIDENCE_THRESHOLD = 0.65  # Minimum confidence for trade
MIN_HOLD_MINUTES = 30  # Whipsaw protection

# Rollback safety
DEGRADATION_THRESHOLD = 0.10  # 10% degradation triggers rollback
ROLLBACK_WAIT_MINUTES = 60  # Wait before auto-rollback

# A/B testing
AB_TEST_SAMPLE_SIZE = 100
AB_TEST_CONFIDENCE_LEVEL = 0.95

# Cron schedules
V7_SYNC_SCHEDULE = "0 2 * * *"  # Daily at 2 AM UTC
AB_TEST_SCHEDULE = "0 3 * * 0"  # Sunday at 3 AM UTC
PERF_CHECK_SCHEDULE = "0 * * * *"  # Hourly

# Performance baselines
BASELINE_WIN_RATE = 65.0
BASELINE_AVG_RETURN = 2.5
BASELINE_RETRIEVAL_LATENCY = 50.0  # ms
