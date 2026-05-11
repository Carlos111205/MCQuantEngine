from django.db import models

class UserAccount(models.Model):
    balance = models.FloatField(default=10000.0)
    equity = models.FloatField(default=10000.0)
    margin_used = models.FloatField(default=0.0)
    
    def __str__(self):
        return f"Demo Account: ${self.balance}"

class Trade(models.Model):
    TRADE_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    symbol = models.CharField(max_length=20)
    type = models.CharField(max_length=4, choices=TRADE_TYPES)
    open_price = models.FloatField()
    current_price = models.FloatField(null=True, blank=True)
    close_price = models.FloatField(null=True, blank=True)
    stop_loss = models.FloatField()
    take_profit = models.FloatField()
    lot_size = models.FloatField()
    pnl = models.FloatField(default=0.0)
    open_time = models.DateTimeField(auto_now_add=True)
    close_time = models.DateTimeField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    pattern = models.CharField(max_length=100, null=True, blank=True)
    confidence = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.symbol} {self.type} - {self.pnl}"

class MarketData(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    price = models.FloatField()
    change_percent = models.FloatField(default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol}: {self.price}"
