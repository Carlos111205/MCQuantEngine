from datetime import datetime, timedelta
import math
import random

dashboard_stats = {
    'totalPnl': 14832.50,
    'todayPnl': 1247.80,
    'winRate': 67.3,
    'totalTrades': 342,
    'openPositions': 4,
    'maxDrawdown': 8.2,
    'sharpeRatio': 1.87,
    'profitFactor': 2.14,
}

current_regime = {
    'regime': 'TRENDING',
    'probability': 0.78,
    'atr': 0.00142,
    'adx': 34.5,
    'trend': 'UP',
    'volatility': 'MEDIUM',
}

open_trades = [
    { 'id': 'T001', 'symbol': 'EURUSD', 'type': 'BUY', 'openPrice': 1.08420, 'currentPrice': 1.08650, 'stopLoss': 1.08180, 'takeProfit': 1.09100, 'lotSize': 0.50, 'pnl': 115.00, 'pnlPercent': 1.15, 'openTime': '2024-01-15 09:32', 'pattern': 'Bullish Engulfing', 'confidence': 0.74, 'regime': 'TRENDING' },
    { 'id': 'T002', 'symbol': 'GBPUSD', 'type': 'BUY', 'openPrice': 1.27150, 'currentPrice': 1.27380, 'stopLoss': 1.26890, 'takeProfit': 1.27850, 'lotSize': 0.30, 'pnl': 69.00, 'pnlPercent': 0.69, 'openTime': '2024-01-15 10:15', 'pattern': 'Pin Bar', 'confidence': 0.68, 'regime': 'TRENDING' },
    { 'id': 'T003', 'symbol': 'XAUUSD', 'type': 'SELL', 'openPrice': 2038.50, 'currentPrice': 2035.20, 'stopLoss': 2044.00, 'takeProfit': 2025.00, 'lotSize': 0.20, 'pnl': 66.00, 'pnlPercent': 0.66, 'openTime': '2024-01-15 11:00', 'pattern': 'Evening Star', 'confidence': 0.71, 'regime': 'HIGH_VOL' },
    { 'id': 'T004', 'symbol': 'NAS100', 'type': 'BUY', 'openPrice': 17245.00, 'currentPrice': 17312.50, 'stopLoss': 17180.00, 'takeProfit': 17450.00, 'lotSize': 0.10, 'pnl': 67.50, 'pnlPercent': 0.68, 'openTime': '2024-01-15 14:30', 'pattern': 'Inside Bar Breakout', 'confidence': 0.82, 'regime': 'TRENDING' },
]

candle_patterns = [
    { 'id': 'CP01', 'name': 'Bullish Engulfing', 'type': 'BULLISH', 'score': 0.74, 'occurrences': 89, 'winRate': 68.5, 'avgReturn': 1.42, 'lastSeen': '2h ago' },
    { 'id': 'CP02', 'name': 'Pin Bar (Bull)', 'type': 'BULLISH', 'score': 0.68, 'occurrences': 124, 'winRate': 63.7, 'avgReturn': 1.18, 'lastSeen': '4h ago' },
    { 'id': 'CP03', 'name': 'Inside Bar Breakout', 'type': 'BULLISH', 'score': 0.82, 'occurrences': 56, 'winRate': 71.4, 'avgReturn': 1.85, 'lastSeen': '1h ago' },
    { 'id': 'CP04', 'name': 'Morning Star', 'type': 'BULLISH', 'score': 0.71, 'occurrences': 43, 'winRate': 67.4, 'avgReturn': 1.55, 'lastSeen': '6h ago' },
    { 'id': 'CP05', 'name': 'Bearish Engulfing', 'type': 'BEARISH', 'score': 0.72, 'occurrences': 91, 'winRate': 66.0, 'avgReturn': 1.38, 'lastSeen': '3h ago' },
    { 'id': 'CP06', 'name': 'Evening Star', 'type': 'BEARISH', 'score': 0.69, 'occurrences': 38, 'winRate': 65.8, 'avgReturn': 1.32, 'lastSeen': '5h ago' },
    { 'id': 'CP07', 'name': 'Pin Bar (Bear)', 'type': 'BEARISH', 'score': 0.65, 'occurrences': 112, 'winRate': 61.6, 'avgReturn': 1.12, 'lastSeen': '8h ago' },
    { 'id': 'CP08', 'name': 'Doji Reversal', 'type': 'NEUTRAL', 'score': 0.58, 'occurrences': 78, 'winRate': 57.7, 'avgReturn': 0.95, 'lastSeen': '12h ago' },
    { 'id': 'CP09', 'name': 'Breakout Candle', 'type': 'BULLISH', 'score': 0.76, 'occurrences': 67, 'winRate': 69.5, 'avgReturn': 1.62, 'lastSeen': '30m ago' },
    { 'id': 'CP10', 'name': 'Hammer', 'type': 'BULLISH', 'score': 0.63, 'occurrences': 95, 'winRate': 62.1, 'avgReturn': 1.08, 'lastSeen': '7h ago' },
    { 'id': 'CP11', 'name': 'Shooting Star', 'type': 'BEARISH', 'score': 0.67, 'occurrences': 83, 'winRate': 64.2, 'avgReturn': 1.25, 'lastSeen': '9h ago' },
    { 'id': 'CP12', 'name': 'Three White Soldiers', 'type': 'BULLISH', 'score': 0.79, 'occurrences': 28, 'winRate': 72.4, 'avgReturn': 1.92, 'lastSeen': '2d ago' },
    { 'id': 'CP13', 'name': 'Three Black Crows', 'type': 'BEARISH', 'score': 0.77, 'occurrences': 31, 'winRate': 70.1, 'avgReturn': 1.78, 'lastSeen': '1d ago' },
    { 'id': 'CP14', 'name': 'Tweezer Bottom', 'type': 'BULLISH', 'score': 0.61, 'occurrences': 52, 'winRate': 60.6, 'avgReturn': 1.01, 'lastSeen': '14h ago' },
    { 'id': 'CP15', 'name': 'Inverted Hammer', 'type': 'BULLISH', 'score': 0.59, 'occurrences': 71, 'winRate': 58.2, 'avgReturn': 0.88, 'lastSeen': '11h ago' },
]

risk_metrics = [
    { 'label': 'Daily Risk Used', 'value': 1.4, 'max': 2.0, 'status': 'warning', 'unit': '%' },
    { 'label': 'Open Exposure', 'value': 3.2, 'max': 5.0, 'status': 'safe', 'unit': '%' },
    { 'label': 'Consecutive Losses', 'value': 1, 'max': 5, 'status': 'safe', 'unit': '' },
    { 'label': 'Max Drawdown', 'value': 8.2, 'max': 15, 'status': 'safe', 'unit': '%' },
    { 'label': 'Correlation Risk', 'value': 0.42, 'max': 1.0, 'status': 'safe', 'unit': '' },
    { 'label': 'Volatility Score', 'value': 6.8, 'max': 10, 'status': 'warning', 'unit': '/10' },
]

equity_history = []
for i in range(90):
    base_equity = 10000 + (i * 55) + math.sin(i * 0.3) * 200 + random.random() * 150
    drawdown = max(0, math.sin(i * 0.15) * 3 + random.random() * 2)
    equity_history.append({
        'date': (datetime(2024, 1, 1) + timedelta(days=i)).strftime('%Y-%m-%d'),
        'equity': round(base_equity, 2),
        'drawdown': round(drawdown, 2),
    })

trade_history = [
    { 'id': 'TH01', 'symbol': 'EURUSD', 'type': 'BUY', 'pattern': 'Bullish Engulfing', 'entryPrice': 1.08120, 'exitPrice': 1.08540, 'pnl': 210.00, 'pnlPercent': 2.10, 'duration': '4h 12m', 'date': '2024-01-14', 'regime': 'TRENDING', 'confidence': 0.72 },
    { 'id': 'TH02', 'symbol': 'GBPUSD', 'type': 'SELL', 'pattern': 'Evening Star', 'entryPrice': 1.27850, 'exitPrice': 1.27420, 'pnl': 129.00, 'pnlPercent': 1.29, 'duration': '2h 45m', 'date': '2024-01-14', 'regime': 'RANGING', 'confidence': 0.65 },
    { 'id': 'TH03', 'symbol': 'XAUUSD', 'type': 'BUY', 'pattern': 'Pin Bar', 'entryPrice': 2025.30, 'exitPrice': 2019.80, 'pnl': -110.00, 'pnlPercent': -1.10, 'duration': '1h 30m', 'date': '2024-01-14', 'regime': 'HIGH_VOL', 'confidence': 0.58 },
    { 'id': 'TH04', 'symbol': 'NAS100', 'type': 'BUY', 'pattern': 'Inside Bar Breakout', 'entryPrice': 17120.00, 'exitPrice': 17285.00, 'pnl': 165.00, 'pnlPercent': 1.65, 'duration': '5h 20m', 'date': '2024-01-13', 'regime': 'TRENDING', 'confidence': 0.81 },
    { 'id': 'TH05', 'symbol': 'EURUSD', 'type': 'SELL', 'pattern': 'Bearish Engulfing', 'entryPrice': 1.09150, 'exitPrice': 1.08780, 'pnl': 185.00, 'pnlPercent': 1.85, 'duration': '3h 15m', 'date': '2024-01-13', 'regime': 'TRENDING', 'confidence': 0.70 },
    { 'id': 'TH06', 'symbol': 'BTCUSD', 'type': 'BUY', 'pattern': 'Breakout Candle', 'entryPrice': 42850.00, 'exitPrice': 43420.00, 'pnl': 285.00, 'pnlPercent': 2.85, 'duration': '6h 45m', 'date': '2024-01-13', 'regime': 'HIGH_VOL', 'confidence': 0.76 },
    { 'id': 'TH07', 'symbol': 'GBPUSD', 'type': 'BUY', 'pattern': 'Morning Star', 'entryPrice': 1.26900, 'exitPrice': 1.27180, 'pnl': 84.00, 'pnlPercent': 0.84, 'duration': '2h 10m', 'date': '2024-01-12', 'regime': 'RANGING', 'confidence': 0.62 },
    { 'id': 'TH08', 'symbol': 'XAUUSD', 'type': 'SELL', 'pattern': 'Shooting Star', 'entryPrice': 2048.70, 'exitPrice': 2042.30, 'pnl': 128.00, 'pnlPercent': 1.28, 'duration': '3h 55m', 'date': '2024-01-12', 'regime': 'TRENDING', 'confidence': 0.69 },
    { 'id': 'TH09', 'symbol': 'NAS100', 'type': 'SELL', 'pattern': 'Three Black Crows', 'entryPrice': 17380.00, 'exitPrice': 17420.00, 'pnl': -40.00, 'pnlPercent': -0.40, 'duration': '45m', 'date': '2024-01-12', 'regime': 'HIGH_VOL', 'confidence': 0.55 },
    { 'id': 'TH10', 'symbol': 'EURUSD', 'type': 'BUY', 'pattern': 'Hammer', 'entryPrice': 1.07850, 'exitPrice': 1.08120, 'pnl': 135.00, 'pnlPercent': 1.35, 'duration': '4h 30m', 'date': '2024-01-11', 'regime': 'RANGING', 'confidence': 0.64 },
    { 'id': 'TH11', 'symbol': 'BTCUSD', 'type': 'SELL', 'pattern': 'Pin Bar', 'entryPrice': 44200.00, 'exitPrice': 43750.00, 'pnl': 225.00, 'pnlPercent': 2.25, 'duration': '8h 15m', 'date': '2024-01-11', 'regime': 'TRENDING', 'confidence': 0.73 },
    { 'id': 'TH12', 'symbol': 'GBPUSD', 'type': 'BUY', 'pattern': 'Bullish Engulfing', 'entryPrice': 1.26450, 'exitPrice': 1.26320, 'pnl': -39.00, 'pnlPercent': -0.39, 'duration': '1h 05m', 'date': '2024-01-11', 'regime': 'RANGING', 'confidence': 0.57 },
    { 'id': 'TH13', 'symbol': 'XAUUSD', 'type': 'BUY', 'pattern': 'Doji Reversal', 'entryPrice': 2032.10, 'exitPrice': 2039.80, 'pnl': 154.00, 'pnlPercent': 1.54, 'duration': '5h 40m', 'date': '2024-01-10', 'regime': 'RANGING', 'confidence': 0.61 },
    { 'id': 'TH14', 'symbol': 'NAS100', 'type': 'BUY', 'pattern': 'Breakout Candle', 'entryPrice': 16980.00, 'exitPrice': 17155.00, 'pnl': 175.00, 'pnlPercent': 1.75, 'duration': '7h 20m', 'date': '2024-01-10', 'regime': 'TRENDING', 'confidence': 0.79 },
    { 'id': 'TH15', 'symbol': 'EURUSD', 'type': 'SELL', 'pattern': 'Pin Bar', 'entryPrice': 1.09420, 'exitPrice': 1.09550, 'pnl': -65.00, 'pnlPercent': -0.65, 'duration': '2h 00m', 'date': '2024-01-10', 'regime': 'HIGH_VOL', 'confidence': 0.52 },
    { 'id': 'TH16', 'symbol': 'BTCUSD', 'type': 'BUY', 'pattern': 'Three White Soldiers', 'entryPrice': 41200.00, 'exitPrice': 42100.00, 'pnl': 450.00, 'pnlPercent': 4.50, 'duration': '12h 30m', 'date': '2024-01-09', 'regime': 'TRENDING', 'confidence': 0.84 },
    { 'id': 'TH17', 'symbol': 'GBPUSD', 'type': 'SELL', 'pattern': 'Bearish Engulfing', 'entryPrice': 1.28100, 'exitPrice': 1.27720, 'pnl': 114.00, 'pnlPercent': 1.14, 'duration': '3h 45m', 'date': '2024-01-09', 'regime': 'TRENDING', 'confidence': 0.71 },
    { 'id': 'TH18', 'symbol': 'XAUUSD', 'type': 'BUY', 'pattern': 'Inside Bar Breakout', 'entryPrice': 2018.40, 'exitPrice': 2029.60, 'pnl': 224.00, 'pnlPercent': 2.24, 'duration': '6h 10m', 'date': '2024-01-09', 'regime': 'RANGING', 'confidence': 0.77 },
    { 'id': 'TH19', 'symbol': 'NAS100', 'type': 'SELL', 'pattern': 'Evening Star', 'entryPrice': 17450.00, 'exitPrice': 17320.00, 'pnl': 130.00, 'pnlPercent': 1.30, 'duration': '4h 55m', 'date': '2024-01-08', 'regime': 'TRENDING', 'confidence': 0.66 },
    { 'id': 'TH20', 'symbol': 'EURUSD', 'type': 'BUY', 'pattern': 'Morning Star', 'entryPrice': 1.07620, 'exitPrice': 1.07980, 'pnl': 180.00, 'pnlPercent': 1.80, 'duration': '5h 25m', 'date': '2024-01-08', 'regime': 'RANGING', 'confidence': 0.68 },
    { 'id': 'TH21', 'symbol': 'BTCUSD', 'type': 'SELL', 'pattern': 'Shooting Star', 'entryPrice': 45100.00, 'exitPrice': 44650.00, 'pnl': 225.00, 'pnlPercent': 2.25, 'duration': '9h 40m', 'date': '2024-01-08', 'regime': 'HIGH_VOL', 'confidence': 0.72 },
    { 'id': 'TH22', 'symbol': 'GBPUSD', 'type': 'BUY', 'pattern': 'Tweezer Bottom', 'entryPrice': 1.25800, 'exitPrice': 1.26050, 'pnl': 75.00, 'pnlPercent': 0.75, 'duration': '2h 30m', 'date': '2024-01-07', 'regime': 'RANGING', 'confidence': 0.59 },
    { 'id': 'TH23', 'symbol': 'XAUUSD', 'type': 'SELL', 'pattern': 'Three Black Crows', 'entryPrice': 2055.00, 'exitPrice': 2041.20, 'pnl': 276.00, 'pnlPercent': 2.76, 'duration': '8h 05m', 'date': '2024-01-07', 'regime': 'TRENDING', 'confidence': 0.80 },
    { 'id': 'TH24', 'symbol': 'NAS100', 'type': 'BUY', 'pattern': 'Hammer', 'entryPrice': 16850.00, 'exitPrice': 16920.00, 'pnl': 70.00, 'pnlPercent': 0.70, 'duration': '1h 50m', 'date': '2024-01-07', 'regime': 'RANGING', 'confidence': 0.56 },
    { 'id': 'TH25', 'symbol': 'EURUSD', 'type': 'BUY', 'pattern': 'Inverted Hammer', 'entryPrice': 1.07280, 'exitPrice': 1.07150, 'pnl': -65.00, 'pnlPercent': -0.65, 'duration': '55m', 'date': '2024-01-06', 'regime': 'HIGH_VOL', 'confidence': 0.51 },
]

symbol_colors = {
    'EURUSD': '#00E6FF',
    'GBPUSD': '#FF00C8',
    'XAUUSD': '#FFD700',
    'NAS100': '#00E682',
    'BTCUSD': '#FF9600',
}

market_alerts = [
    { 'id': 1, 'symbol': 'EURUSD', 'type': 'SIGNAL', 'direction': 'BUY', 'message': 'H1 Bullish Divergence detected on RSI. Confluence with S1 Pivot.', 'time': '5m ago', 'priority': 'HIGH' },
    { 'id': 2, 'symbol': 'XAUUSD', 'type': 'ALERT', 'direction': 'NEUTRAL', 'message': 'High volatility expected in 15m due to FOMC Meeting Minutes.', 'time': '12m ago', 'priority': 'CRITICAL' },
    { 'id': 3, 'symbol': 'BTCUSD', 'type': 'SIGNAL', 'direction': 'SELL', 'message': 'Bearish Engulfing on M15. Institutional sell-off detected in order flow.', 'time': '20m ago', 'priority': 'MEDIUM' },
    { 'id': 4, 'symbol': 'GBPUSD', 'type': 'ANALYSIS', 'direction': 'BUY', 'message': 'Price approaching major demand zone at 1.2650. Watch for reversal.', 'time': '45m ago', 'priority': 'LOW' },
]

trading_strategies = [
    { 
        'name': 'Neural Momentum', 
        'description': 'AI-driven momentum strategy using LSTM networks to predict short-term price movements.',
        'risk': 'Medium',
        'timeframe': 'M15/H1',
        'status': 'ACTIVE',
        'win_rate': 68.4
    },
    { 
        'name': 'Institutional Liquidity', 
        'description': 'Tracks large block orders and liquidity pools to identify high-probability reversal zones.',
        'risk': 'Low',
        'timeframe': 'H1/H4',
        'status': 'OPTIMIZING',
        'win_rate': 72.1
    },
    { 
        'name': 'Mean Reversion Pro', 
        'description': 'Statistical arbitrage strategy focused on overextended market conditions using Bollinger Bands and ATR.',
        'risk': 'High',
        'timeframe': 'M5',
        'status': 'BACKTESTING',
        'win_rate': 61.8
    }
]
