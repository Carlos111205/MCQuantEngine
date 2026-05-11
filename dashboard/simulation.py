import random
import math

def run_monte_carlo_simulation(params):
    win_rate = params.get('winRate', 50)
    risk_reward = params.get('riskReward', 2)
    num_trades = params.get('numTrades', 100)
    num_simulations = params.get('numSimulations', 100)
    initial_balance = params.get('initialBalance', 10000)
    risk_per_trade = params.get('riskPerTrade', 1)
    risk_type = params.get('riskType', 'percent')  # 'percent' or 'fixed'
    fixed_amount = params.get('fixedAmount', 100)
    commission = params.get('commission', 0)  # In currency units per trade
    slippage = params.get('slippage', 0)      # In percentage of the win/loss

    win_prob = win_rate / 100
    paths = []
    final_balances = []
    total_max_drawdown = 0
    ruin_count = 0

    for sim in range(num_simulations):
        path = [initial_balance]
        balance = initial_balance
        peak = initial_balance
        max_dd = 0

        for trade in range(num_trades):
            is_win = random.random() < win_prob
            
            if risk_type == 'percent':
                current_risk = (risk_per_trade / 100) * balance
            else:
                current_risk = fixed_amount
            
            # Apply commission
            balance -= commission
            
            if is_win:
                # Apply slippage to the win (reduces win)
                win_amount = current_risk * risk_reward
                win_amount *= (1 - (slippage / 100))
                balance += win_amount
            else:
                # Apply slippage to the loss (increases loss)
                loss_amount = current_risk
                loss_amount *= (1 + (slippage / 100))
                balance -= loss_amount

            if balance <= 0:
                balance = 0
                ruin_count += 1
                path.append(0)
                break

            peak = max(peak, balance)
            dd = ((peak - balance) / peak) * 100
            max_dd = max(max_dd, dd)
            path.append(balance)

        paths.append(path)
        final_balances.append(balance)
        total_max_drawdown = max(total_max_drawdown, max_dd)

    # Calculate percentiles
    max_len = max(len(p) for p in paths)
    median_path = []
    percentile_5 = []
    percentile_95 = []

    for i in range(max_len):
        values_at_step = sorted([p[i] for p in paths if i < len(p)])
        if values_at_step:
            median_path.append(values_at_step[int(len(values_at_step) * 0.5)])
            percentile_5.append(values_at_step[int(len(values_at_step) * 0.05)])
            percentile_95.append(values_at_step[int(len(values_at_step) * 0.95)])

    avg_final = sum(final_balances) / len(final_balances)
    avg_return = ((avg_final - initial_balance) / initial_balance) * 100
    
    # Simplified Sharpe calculation
    returns = [(b - initial_balance) / initial_balance for b in final_balances]
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    std_return = math.sqrt(variance)
    sharpe_ratio = mean_return / std_return if std_return > 0 else 0

    return {
        'paths': paths[:50],  # Limit displayed paths
        'medianPath': median_path,
        'percentile5': percentile_5,
        'percentile95': percentile_95,
        'maxDrawdown': total_max_drawdown,
        'ruinProbability': (ruin_count / num_simulations) * 100,
        'finalBalances': final_balances,
        'avgReturn': avg_return,
        'sharpeRatio': sharpe_ratio,
    }

def calculate_drawdown_distribution(final_balances, initial_balance):
    buckets = [
        { 'min': -100, 'max': -50, 'label': '-100% to -50%' },
        { 'min': -50, 'max': -25, 'label': '-50% to -25%' },
        { 'min': -25, 'max': -10, 'label': '-25% to -10%' },
        { 'min': -10, 'max': 0, 'label': '-10% to 0%' },
        { 'min': 0, 'max': 25, 'label': '0% to +25%' },
        { 'min': 25, 'max': 50, 'label': '+25% to +50%' },
        { 'min': 50, 'max': 100, 'label': '+50% to +100%' },
        { 'min': 100, 'max': 500, 'label': '+100% to +500%' },
    ]

    results = []
    for bucket in buckets:
        count = 0
        for b in final_balances:
            ret = ((b - initial_balance) / initial_balance) * 100
            if bucket['min'] <= ret < bucket['max']:
                count += 1
        results.append({
            'bucket': bucket['label'],
            'count': count,
        })
    return results
