# Algorithmic Trading in Python

## 🚀 Project Overview

This repository demonstrates an end-to-end algorithmic trading system written in Python. It integrates trading strategies (like MACD, VWAP, and TEMA), API interactions with Robinhood or other brokers, and an efficient scheduler to execute trades in real-time.

---

## 📂 Project Structure

```
Algorithmic-Trading-in-Python/
│
├── main.py                        # Entry point for the application
├── trading_scheduler.py           # Scheduler and strategy execution logic
├── trading_strategy.py            # Contains all trading strategies (BTC_trading_strategy, etc.)
├── crypto_api_trading.py          # API interaction logic for Robinhood or other platforms
├── generate_keypair.py            # Script to generate API keys
├── config/
│   └── api_config.py              # API key and logging configurations
├── docs/
│   ├── strategy_docs.md           # Detailed explanation of implemented strategies
│   ├── api_docs.md                # Details about the API and its integration
│   └── architecture_overview.md   # Project architecture description
├── tests/
│   ├── test_trading_scheduler.py  # Unit tests for the scheduler
│   ├── test_trading_strategy.py   # Unit tests for strategies
├── requirements.txt               # Dependency file
└── README.md                      # Project documentation
```

---

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Pip (Python package manager)
- A Robinhood API account or other crypto API access

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Algorithmic-Trading-in-Python.git
   cd Algorithmic-Trading-in-Python
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys:
   - Add your API key and private key to a `.env` file or `config/api_config.py`.

4. Run the application:
   ```bash
   python main.py
   ```

---

## 📊 Features

- **Trading Strategies**: Implements technical indicators like MACD, VWAP, TEMA, and custom risk management techniques.
- **Automated Scheduling**: Uses `schedule` to run strategies at regular intervals.
- **API Integration**: Interacts with trading APIs to place and manage orders.
- **Logging**: Tracks trades, errors, and account value changes.
- **Risk Management**: Implements stop-loss, take-profit, and account value monitoring.

---

## 📈 Trading Logic

### Signal Aggregation Process
The trading logic combines signals from multiple indicators to make a final decision: `buy`, `sell`, or `hold`. Signals are weighted based on predefined importance, and a normalized score determines the action:

1. **Indicators**: Signals are calculated from strategies like MACD, MVCD, VWAP, and TEMA.
2. **Weights**: Each indicator contributes to the final decision proportionally to its assigned weight.
3. **Decision Thresholds**:
   - `Buy`: Normalized score > 0.5
   - `Sell`: Normalized score < -0.5
   - `Hold`: Score between -0.5 and 0.5

### Risk Management and Logging
- **Risk Parameters**:
  - **Predefined Risk**: A percentage of account value is allocated for each trade.
  - **Confidence**: Adjusts trade size based on signal confidence.
  - **Stop Loss**: Automatically exits trades if the price moves against the position beyond a set percentage.
  - **Take Profit**: Locks in profits when the price reaches a favorable percentage.

- **Logging**:
  - All decisions, trades, and account updates are logged in `trading_scheduler.log`.

### Example Workflow:
1. Fetch market data (prices, volume, etc.).
2. Calculate signals using technical indicators.
3. Aggregate signals with predefined weights.
4. Execute trade if a `buy` or `sell` signal is generated.
5. Log the trade details, including stop-loss and take-profit thresholds.

---

## 🧠 Trading Strategies

The system uses the following technical indicators:

- **MACD**: Measures momentum and identifies trend reversals.
- **MVCD**: Applies MACD principles to volatility analysis.
- **VWAP**: Assesses fair price levels based on price and volume.
- **TEMA**: Reduces lag in moving averages for more responsive signals.

For detailed descriptions, see [Strategy Documentation](docs/strategy_docs.md).

---

## 🔬 Testing

Run unit tests to validate functionality:
```bash
pytest tests/
```

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository.
2. Create a feature branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add a feature"
   ```
4. Push to your fork:
   ```bash
   git push origin feature-name
   ```
5. Submit a pull request.

---

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 🙋‍♂️ Questions?

Feel free to open an issue or contact us at [hurdc21@bonaventure.edu].

---

