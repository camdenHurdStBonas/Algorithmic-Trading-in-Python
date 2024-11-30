import unittest
from unittest.mock import patch, MagicMock
from trading_scheduler import (
    get_account_value,
    job,
    run_scheduler,
    start_scheduler
)
from robinhood_api_trading import CryptoAPITrading

class TestTradingScheduler(unittest.TestCase):
    @patch('trading_scheduler.CryptoAPITrading')
    def test_get_account_value(self, MockCryptoAPITrading):
        # Mock API response
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

        # Call the function
        account_value = get_account_value(mock_client)

        # Assert total value calculation
        self.assertAlmostEqual(account_value, 5000.00 + 0.5 * 60000 + 2 * 4000)

    @patch('trading_scheduler.CryptoAPITrading')
    def test_job_execution(self, MockCryptoAPITrading):
        # Mock trading strategy
        mock_strategy = MagicMock()
        mock_client = MockCryptoAPITrading()

        # Mock account value
        with patch('trading_scheduler.get_account_value', return_value=10000.0):
            job(mock_strategy, mock_client)

        # Assert the strategy was executed
        mock_strategy.assert_called_once_with(mock_client)

    @patch('trading_scheduler.schedule')
    @patch('trading_scheduler.CryptoAPITrading')
    def test_run_scheduler(self, MockCryptoAPITrading, mock_schedule):
        mock_client = MockCryptoAPITrading()
        mock_strategy = MagicMock()
        mock_schedule.every.return_value.seconds.do = MagicMock()

        # Run the scheduler with a single strategy
        run_scheduler([(mock_strategy, 10)])

        # Assert the strategy was scheduled
        mock_schedule.every.assert_called_once_with(10)
        mock_schedule.every.return_value.seconds.do.assert_called_once()

    @patch('trading_scheduler.threading.Thread')
    @patch('trading_scheduler.run_scheduler')
    def test_start_scheduler(self, mock_run_scheduler, MockThread):
        mock_thread = MockThread.return_value
        mock_thread.start = MagicMock()

        # Mock strategy
        mock_strategy = MagicMock()

        # Start the scheduler
        with patch('builtins.input', side_effect=['q']):
            start_scheduler([(mock_strategy, 10)])

        # Assert that the thread was started
        mock_thread.start.assert_called_once()

if __name__ == "__main__":
    unittest.main()
