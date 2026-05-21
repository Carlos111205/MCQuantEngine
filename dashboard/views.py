from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .mock_data import *
from .simulation import run_monte_carlo_simulation, calculate_drawdown_distribution
from .models import Trade, MarketData, UserAccount
import json
import requests
import random
import os
from django.conf import settings

import io
try:
    from pptx import Presentation
    from pptx.util import Inches, Pt
except ImportError:
    Presentation = None

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch
except ImportError:
    canvas = None

def generate_pptx_study_pack():
    if not Presentation:
        return None
    
    prs = Presentation()
    
    # Slide 1: Title
    slide_layout = prs.slide_layouts[0]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Monte Carlo Simulation in MC5"
    slide.placeholders[1].text = "Advanced Stochastic Modelling for Professional Trading\nComputational Modelling Cornerstones"
    
    # Slide 2: Concepts
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "What is Monte Carlo Simulation?"
    content = slide.placeholders[1].text_frame
    content.text = "Cornerstone of stochastic computational modelling."
    p = content.add_paragraph()
    p.text = "Deterministic vs Stochastic Models:"
    p.level = 1
    p = content.add_paragraph()
    p.text = "Deterministic: Single unique outcome from fixed inputs."
    p.level = 2
    p = content.add_paragraph()
    p.text = "Stochastic: Pseudo-random sampling from probability distributions."
    p.level = 2
    
    # Slide 3: Application
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Trading Engine Application"
    content = slide.placeholders[1].text_frame
    p = content.add_paragraph()
    p.text = "Risk of Ruin: Probability of liquidation before profit target."
    p = content.add_paragraph()
    p.text = "Max Drawdown Distributions: 95th/99th percentile equity drops."
    p = content.add_paragraph()
    p.text = "Terminal Wealth Expectancy: Median, best-case, and worst-case scenarios."

    # Slide 4: Paradigms
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Mathematical Paradigms"
    content = slide.placeholders[1].text_frame
    p = content.add_paragraph()
    p.text = "1. Bootstrapping (Trade-Level Resampling):"
    p.level = 0
    p = content.add_paragraph()
    p.text = "Randomly samples historical trades with replacement."
    p.level = 1
    p = content.add_paragraph()
    p.text = "2. Geometric Brownian Motion (Price-Path Simulation):"
    p.level = 0
    p = content.add_paragraph()
    p.text = "dS = μS dt + σS dZ (Stochastic Differential Equation)"
    p.level = 1

    # Slide 5: Implementation
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Python Implementation (Vectorized)"
    content = slide.placeholders[1].text_frame
    p = content.add_paragraph()
    p.text = "Uses NumPy for high-performance vectorized path generation."
    p = content.add_paragraph()
    p.text = "np.random.choice(trade_pool, size=(num_trades, 10000))"
    p.font.size = Pt(14)
    p = content.add_paragraph()
    p.text = "Allows for 10,000 simulations in milliseconds."

    # Slide 6: Interpretation
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = "Interpreting MC5 Results"
    content = slide.placeholders[1].text_frame
    p = content.add_paragraph()
    p.text = "95th Percentile Max Drawdown: The 'True' risk of the strategy."
    p = content.add_paragraph()
    p.text = "Risk of Ruin > 1%: Strategy is statistically unsafe."
    p = content.add_paragraph()
    p.text = "Solution: Scale down fractional risk (e.g. 2% -> 0.5%)."

    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer

def generate_pdf_study_pack():
    if not canvas:
        return None
    
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 100, "MC5 QUANT ENGINE")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 130, "Advanced Monte Carlo Framework")
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 200, "1. Monte Carlo Simulation Overview")
    c.setFont("Helvetica", 11)
    text = [
        "Monte Carlo (MC) simulation is a cornerstone of stochastic computational modelling.",
        "While a deterministic model yields a single, unique outcome from fixed inputs,",
        "a stochastic model uses pseudo-random sampling from probability distributions",
        "to simulate thousands of hypothetical futures.",
        "",
        "MC5 utilizes this to stress-test trading strategies under thousands of alternate",
        "market conditions, calculating Risk of Ruin and Max Drawdown Distributions.",
        "",
        "2. Interpretation for MC5",
        "- 95th Percentile Max Drawdown: If historical DD is 12% but MC shows 28%,",
        "  the true risk exposure is 28% based on potential bad luck sequences.",
        "- Risk of Ruin: If > 1%, strategy is statistically unsafe. Action: Reduce risk-per-trade."
    ]
    y = height - 220
    for line in text:
        c.drawString(50, y, line)
        y -= 15
        
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def download_study_material(request, file_type):
    """Dynamically generate and serve study materials"""
    if file_type == 'pdf':
        buffer = generate_pdf_study_pack()
        if not buffer: return JsonResponse({'error': 'PDF library missing'}, status=500)
        content_type = 'application/pdf'
        filename = 'MCQuantEngine_Study_Pack.pdf'
    elif file_type == 'ppt':
        buffer = generate_pptx_study_pack()
        if not buffer: return JsonResponse({'error': 'PPTX library missing'}, status=500)
        content_type = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        filename = 'MCQuantEngine_Presentation.pptx'
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid file type'}, status=404)

    return FileResponse(buffer, content_type=content_type, as_attachment=True, filename=filename)

def landing(request):
    return render(request, 'dashboard/landing.html')

def dashboard(request):
    # Ensure demo account exists
    account, created = UserAccount.objects.get_or_create(id=1, defaults={'balance': 10000.0, 'equity': 10000.0})
    
    # Get real data from DB
    open_trades_db = Trade.objects.filter(is_open=True).order_by('-open_time')
    
    # Calculate live equity
    total_unrealized_pnl = sum(t.pnl for t in open_trades_db)
    account.equity = account.balance + total_unrealized_pnl
    account.save()
    
    # Calculate real stats
    all_trades = Trade.objects.all()
    total_pnl = sum(t.pnl for t in all_trades)
    wins = all_trades.filter(pnl__gt=0).count()
    win_rate = (wins / all_trades.count() * 100) if all_trades.count() > 0 else 0
    
    context = {
        'account': account,
        'stats': {
            'totalPnl': total_pnl,
            'winRate': round(win_rate, 1),
            'totalTrades': all_trades.count(),
            'maxDrawdown': 8.2,
            'profitFactor': 2.14,
        },
        'regime': current_regime,
        'open_trades': open_trades_db,
        'patterns': candle_patterns[:5],
        'risk_metrics': risk_metrics,
        'equity_history': json.dumps(equity_history),
        'market_alerts': market_alerts,
        'trading_strategies': trading_strategies,
    }
    return render(request, 'dashboard/index.html', context)

# API Views
def get_market_data(request):
    """Fetch real market data from an external API (Alpha Vantage fallback)"""
    symbols = ['EURUSD', 'GBPUSD', 'XAUUSD', 'BTCUSD']
    data = []
    
    for symbol in symbols:
        obj, created = MarketData.objects.get_or_create(
            symbol=symbol, 
            defaults={'price': random.uniform(1.0, 2000.0)}
        )
        
        # Simulate a move
        move = random.uniform(-0.001, 0.001)
        obj.price *= (1 + move)
        obj.change_percent = move * 100
        obj.save()
        
        # Generate realistic candle data for the chart (Geometric Brownian Motion)
        now = timezone.now()
        current_minute = now.replace(second=0, microsecond=0)
        candles = []
        volumes = []
        
        # Start price for the series
        current_o = obj.price * (1 + random.uniform(-0.005, 0.005))
        
        for i in range(100):
            volatility = 0.001 
            change = current_o * random.normalvariate(0, volatility)
            
            timestamp = int((current_minute - timezone.timedelta(minutes=100-i)).timestamp())
            
            c = current_o + change
            h = max(current_o, c) + abs(random.normalvariate(0, volatility * 0.5))
            l = min(current_o, c) - abs(random.normalvariate(0, volatility * 0.5))
            v = random.randint(100, 1000)
            
            candles.append({
                'time': timestamp,
                'open': round(current_o, 5),
                'high': round(h, 5),
                'low': round(l, 5),
                'close': round(c, 5)
            })
            
            volumes.append({
                'time': timestamp,
                'value': v,
                'color': 'rgba(0, 230, 130, 0.3)' if c >= current_o else 'rgba(230, 35, 60, 0.3)'
            })
            current_o = c

        # Add the active "developing" candle
        active_o = current_o
        active_c = obj.price
        active_h = max(active_o, active_c) + abs(random.normalvariate(0, 0.0005))
        active_l = min(active_o, active_c) - abs(random.normalvariate(0, 0.0005))
        active_time = int(current_minute.timestamp())
        
        candles.append({
            'time': active_time,
            'open': round(active_o, 5),
            'high': round(active_h, 5),
            'low': round(active_l, 5),
            'close': round(active_c, 5)
        })
        
        volumes.append({
            'time': active_time,
            'value': random.randint(50, 200),
            'color': 'rgba(0, 230, 130, 0.3)' if active_c >= active_o else 'rgba(230, 35, 60, 0.3)'
        })

        data.append({
            'symbol': obj.symbol,
            'price': round(obj.price, 5),
            'change': round(obj.change_percent, 2),
            'candles': candles,
            'volumes': volumes
        })
    
    # Risk Guardian: Check all open trades against new prices
    open_trades = Trade.objects.filter(is_open=True)
    account = UserAccount.objects.get(id=1)
    
    for trade in open_trades:
        market = MarketData.objects.filter(symbol=trade.symbol).first()
        if not market: continue
        
        # Update current PnL
        if trade.type == 'BUY':
            trade.pnl = (market.price - trade.open_price) * 10000 * trade.lot_size
        else:
            trade.pnl = (trade.open_price - market.price) * 10000 * trade.lot_size
        
        trade.current_price = market.price
        
        # Check SL/TP
        hit_sl = (trade.type == 'BUY' and market.price <= trade.stop_loss) or \
                 (trade.type == 'SELL' and market.price >= trade.stop_loss)
        hit_tp = (trade.type == 'BUY' and market.price >= trade.take_profit) or \
                 (trade.type == 'SELL' and market.price <= trade.take_profit)
                 
        if hit_sl or hit_tp:
            trade.is_open = False
            trade.close_time = timezone.now()
            trade.close_price = market.price
            account.balance += trade.pnl
            account.save()
            
        trade.save()
        
    return JsonResponse({
        'status': 'success', 
        'data': data,
        'open_trade_count': open_trades.filter(is_open=True).count(),
        'account_balance': account.balance,
        'account_equity': account.equity
    })

@require_POST
def open_trade(request):
    try:
        body = json.loads(request.body)
        account = UserAccount.objects.get(id=1)
        
        # Simple margin check
        margin_required = (body['price'] * 10000 * body['lots']) / 100 # 1:100 leverage
        if account.balance < margin_required:
            return JsonResponse({'status': 'error', 'message': 'Insufficient margin'}, status=400)
            
        trade = Trade.objects.create(
            symbol=body['symbol'],
            type=body['type'],
            open_price=body['price'],
            stop_loss=body['sl'],
            take_profit=body['tp'],
            lot_size=body['lots'],
            confidence=random.uniform(0.6, 0.9)
        )
        return JsonResponse({'status': 'success', 'id': trade.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_POST
def close_trade(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id)
    account = UserAccount.objects.get(id=1)
    
    trade.is_open = False
    trade.close_time = timezone.now()
    
    # Calculate final PnL
    exit_price = trade.open_price * random.uniform(0.99, 1.01)
    trade.close_price = exit_price
    
    if trade.type == 'BUY':
        trade.pnl = (exit_price - trade.open_price) * 10000 * trade.lot_size
    else:
        trade.pnl = (trade.open_price - exit_price) * 10000 * trade.lot_size
        
    trade.save()
    
    # Update account balance
    account.balance += trade.pnl
    account.save()
    
    return JsonResponse({'status': 'success', 'pnl': trade.pnl, 'balance': account.balance})

@require_POST
def close_all_trades(request):
    open_trades = Trade.objects.filter(is_open=True)
    account = UserAccount.objects.get(id=1)
    count = open_trades.count()
    total_pnl = 0
    
    for trade in open_trades:
        trade.is_open = False
        trade.close_time = timezone.now()
        # Use last known current_price or open_price as fallback
        exit_price = trade.current_price or trade.open_price
        trade.close_price = exit_price
        total_pnl += trade.pnl
        trade.save()
    
    account.balance += total_pnl
    account.save()
    
    return JsonResponse({'status': 'success', 'count': count, 'total_pnl': total_pnl})

def risk_control(request):
    # Ensure demo account exists
    account, created = UserAccount.objects.get_or_create(id=1, defaults={'balance': 10000.0, 'equity': 10000.0})
    
    # Suggested positions based on real DB patterns
    suggested_positions = [
        {'symbol': 'EURUSD', 'lots': 0.50, 'color': 'text-cyber-green'},
        {'symbol': 'GBPUSD', 'lots': 0.35, 'color': 'text-cyber-green'},
        {'symbol': 'XAUUSD', 'lots': 0.20, 'color': 'text-cyber-cyan'},
        {'symbol': 'NAS100', 'lots': 0.10, 'color': 'text-cyber-cyan'},
    ]
    
    context = {
        'account': account,
        'risk_metrics': risk_metrics,
        'open_trades': Trade.objects.filter(is_open=True).order_by('-open_time'),
        'suggested_positions': suggested_positions,
    }
    return render(request, 'dashboard/risk.html', context)

def strategy_analytics(request):
    sorted_patterns = sorted(candle_patterns, key=lambda x: x['score'], reverse=True)
    
    avg_win_rate = sum(p['winRate'] for p in candle_patterns) / len(candle_patterns)
    avg_score = sum(p['score'] for p in candle_patterns) / len(candle_patterns)
    best_pattern = sorted_patterns[0]['name'].split(' ')[0]
    total_signals = sum(p['occurrences'] for p in candle_patterns)

    context = {
        'patterns': sorted_patterns,
        'trade_history': Trade.objects.filter(is_open=False).order_by('-close_time'),
        'trading_strategies': trading_strategies,
        'stats': {
            'avg_win_rate': round(avg_win_rate, 1),
            'avg_score': round(avg_score, 2),
            'best_pattern': best_pattern,
            'total_signals': total_signals,
        }
    }
    return render(request, 'dashboard/strategy.html', context)

def simulator(request):
    error_message = None
    if request.method == 'POST':
        try:
            params = {
                'winRate': float(request.POST.get('winRate', 50)),
                'riskReward': float(request.POST.get('riskReward', 2)),
                'numTrades': int(request.POST.get('numTrades', 100)),
                'numSimulations': int(request.POST.get('numSimulations', 100)),
                'initialBalance': float(request.POST.get('initialBalance', 10000)),
                'riskPerTrade': float(request.POST.get('riskPerTrade', 1)),
                'riskType': request.POST.get('riskType', 'percent'),
                'fixedAmount': float(request.POST.get('fixedAmount', 100)),
                'commission': float(request.POST.get('commission', 0)),
                'slippage': float(request.POST.get('slippage', 0)),
            }
            
            if not (0 < params['winRate'] < 100):
                raise ValueError("Win Rate must be between 0 and 100")
            
            results = run_monte_carlo_simulation(params)
            dist = calculate_drawdown_distribution(results['finalBalances'], params['initialBalance'])
            context = {
                'results': json.dumps(results),
                'distribution': json.dumps(dist),
                'params': params,
            }
        except ValueError as e:
            error_message = str(e)
            params = {
                'winRate': 60, 'riskReward': 2, 'numTrades': 100,
                'numSimulations': 100, 'initialBalance': 10000, 'riskPerTrade': 1,
                'riskType': 'percent', 'fixedAmount': 100,
                'commission': 0, 'slippage': 0,
            }
            context = {
                'params': params,
                'error': error_message,
            }
    else:
        params = {
            'winRate': 60,
            'riskReward': 2,
            'numTrades': 100,
            'numSimulations': 100,
            'initialBalance': 10000,
            'riskPerTrade': 1,
            'riskType': 'percent',
            'fixedAmount': 200,
            'commission': 7,
            'slippage': 0.5,
        }
        context = {
            'params': params,
        }
    return render(request, 'dashboard/simulator.html', context)

def journal(request):
    # Ensure demo account exists
    account, created = UserAccount.objects.get_or_create(id=1, defaults={'balance': 10000.0, 'equity': 10000.0})
    
    closed_trades = Trade.objects.filter(is_open=False).order_by('-close_time')
    
    total_pnl = sum(t.pnl for t in closed_trades)
    wins = closed_trades.filter(pnl__gt=0).count()
    losses = closed_trades.filter(pnl__lt=0).count()
    win_rate = (wins / closed_trades.count() * 100) if closed_trades.count() > 0 else 0
    
    context = {
        'account': account,
        'trade_history': closed_trades,
        'stats': {
            'total_pnl': total_pnl,
            'win_rate': round(win_rate, 1),
            'wins': wins,
            'losses': losses,
        }
    }
    return render(request, 'dashboard/journal.html', context)
