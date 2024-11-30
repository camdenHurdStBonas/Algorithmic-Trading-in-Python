import unittest
from unittest.mock import patch, MagicMock
from trading_logic import (
    get_account_value,
    fetch_historical_data,
    calculate_macd,
    calculate_mvcd,
    calculate_vwap,
    calculate_tema,
    aggregate_signals,
    execute_trade
)
from robinhood_api_trading import CryptoAPITrading
import pandas as pd


class TestTradingLogic(unittest.TestCase):

    @patch('trading_logic.CryptoAPITrading')
    def test_get_account_value(self, MockCryptoAPITrading):
        # Mock API responses
        mock_client = MockCryptoAPITrading()
        mock_client.get_account.return_value = {'buying_power': '5000.00'}
        mock_client.get_holdings.return_value = {
            'results': [
                {'asset_code': 'BTC', 'total_quantity': '0.5'},
                {'asset_code': 'ETH', 'total_quantity': '2.0'}
            ]
        }
        mock_client.get_best_bid_ask.side_effect = [
            {'results': [{'bid_inclusive_of_sell_spread': '60000.00'}]},  # BTC price
            {'results': [{'bid_inclusive_of_sell_spread': '4000.00'}]}    # ETH price
        ]

        # Test account value calculation
        account_value = get_account_value(mock_client)
        self.assertAlmostEqual(account_value, 5000.00 + (0.5 * 60000) + (2 * 4000))

    @patch('trading_logic.ccxt.coinbase')
    def test_fetch_historical_data(self, MockCoinbase):
        # Mock exchange response
        mock_exchange = MockCoinbase.return_value
        mock_exchange.fetch_ohlcv.return_value = [
            [1638316800000, 57000, 58000, 56000, 57500, 1000],  # Example OHLCV data
            [1638403200000, 57500, 58500, 56500, 58000, 1100]
        ]

        # Test historical data fetch
        data = fetch_historical_data(symbol="BTC/USD", start_date="2022-01-01T00:00:00Z")
        self.assertEqual(len(data), 2)  # Two rows of data
        self.assertIn('close', data.columns)

    def test_calculate_macd(self):
        # Generate mock price data
        prices = pd.Series([100, 101, 102, 103, 104])

        # Test MACD calculation
        signal = calculate_macd(prices)
        self.assertIn(signal, ['buy', 'sell', 'hold'])

    def test_calculate_mvcd(self):
        # Generate mock price data
        prices = pd.Series([100, 101, 102, 103, 104])

        # Test MVCD calculation
        signal = calculate_mvcd(prices)
        self.assertIn(signal, ['buy', 'sell', 'hold'])

    def test_calculate_vwap(self):
        # Generate mock price data
        prices = pd.DataFrame({
            'high': [105, 106, 107],
            'low': [95, 96, 97],
            'close': [100, 101, 102],
            'volume': [1000, 1100, 1200]
        })

        # Test VWAP calculation
        signal = calculate_vwap(prices)
        self.assertIn(signal, ['buy', 'sell', 'hold'])

    def test_calculate_tema(self):
        # Generate mock price data
        prices = pd.Series([100, 101, 102, 103, 104])

        # Test TEMA calculation
        signal = calculate_tema(prices)
        self.assertIn(signal, ['buy', 'sell', 'hold'])

    def test_aggregate_signals(self):
        # Define mock signals and weights
        signals = {'MACD': 'buy', 'MVCD': 'sell', 'VWAP': 'hold', 'TEMA': 'buy'}
        weights = {'MACD': 0.4, 'MVCD': 0.3, 'VWAP': 0.2, 'TEMA': 0.1}

        # Test signal aggregation
        aggregated_signal = aggregate_signals(signals, weights)
        self.assertIn(aggregated_signal, ['buy', 'sell', 'hold'])

    @patch('trading_logic.CryptoAPITrading')
    def test_execute_trade(self, MockCryptoAPITrading):
        mock_client = MockCryptoAPITrading()
        signal = 'buy'
        account_value = 10000.0
        risk_per_trade = 0.01
        stop_loss_percent = 0.02
        take_profit_percent = 0.05
        confidence = 0.5

        # Mock API client methods
        mock_client.get_account.return_value = {'buying_power': '1000.00'}
        mock_client.get_best_bid_ask.return_value = {'results': [{'bid_inclusive_of_sell_spread': '60000.00'}]}
        mock_client.place_order = MagicMock()

        # Test trade execution
        execute_trade(mock_client, signal, "BTC-USD", account_value, risk_per_trade, stop_loss_percent, take_profit_percent, confidence)
        mock_client.place_order.assert_called_once()
