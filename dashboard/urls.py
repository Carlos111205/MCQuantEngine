from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.dashboard, name='index'),
    path('risk/', views.risk_control, name='risk'),
    path('strategy/', views.strategy_analytics, name='strategy'),
    path('simulator/', views.simulator, name='simulator'),
    path('journal/', views.journal, name='journal'),
    
    # API endpoints
    path('api/market-data/', views.get_market_data, name='api_market_data'),
    path('api/trade/close/<int:trade_id>/', views.close_trade, name='api_close_trade'),
    path('api/trade/close-all/', views.close_all_trades, name='api_close_all_trades'),
    path('api/trade/open/', views.open_trade, name='api_open_trade'),
    path('download/<str:file_type>/', views.download_study_material, name='download_study_material'),
]
