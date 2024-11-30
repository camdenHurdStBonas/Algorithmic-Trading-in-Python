# Strategy Documentation

This document provides an overview of the trading strategies used in the **Algorithmic Trading in Python** project. Each strategy is based on technical indicators and aims to identify optimal buy, sell, or hold decisions.

---

## **1. Moving Average Convergence Divergence (MACD)**

### Description:
The MACD is a momentum-based indicator that calculates the difference between a short-term Exponential Moving Average (EMA) and a long-term EMA. A signal line (EMA of the MACD line) helps identify trend reversals.

### Calculation:
- **Short EMA**: Faster-moving average over a shorter period.
- **Long EMA**: Slower-moving average over a longer period.
- **MACD Line**: Difference between Short EMA and Long EMA.
- **Signal Line**: EMA of the MACD line.

### Signal Logic:
- **Buy Signal**: The MACD line crosses above the Signal line.
- **Sell Signal**: The MACD line crosses below the Signal line.
- **Hold**: No crossover is detected.

### Code Snippet:
```python
def calculate_macd(prices, short_window=60, long_window=69, signal_window=8):
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    return 'buy' if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2] else 'sell' if macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2] else 'hold'
```

---

## **2. Modified Volatility Convergence Divergence (MVCD)**

### Description:
MVCD applies the principles of MACD to volatility rather than price. It calculates the difference between short-term and long-term volatility, providing a unique perspective on market conditions.

### Calculation:
- **Short EMA (Volatility)**: Standard deviation of returns over a short period.
- **Long EMA (Volatility)**: Standard deviation of returns over a long period.
- **MVCD Line**: Difference between short-term and long-term volatility.
- **Signal Line**: EMA of the MVCD line.

### Signal Logic:
- **Buy Signal**: The MVCD line crosses above the Signal line.
- **Sell Signal**: The MVCD line crosses below the Signal line.
- **Hold**: No crossover is detected.

### Code Snippet:
```python
def calculate_mvcd(prices, short_window=60, long_window=69, signal_window=8):
    returns = prices.pct_change().dropna()
    short_ema = prices.ewm(span=short_window, adjust=False).std()
    long_ema = prices.ewm(span=long_window, adjust=False).std()
    mvcd_line = short_ema - long_ema
    signal_line = mvcd_line.ewm(span=signal_window, adjust=False).std()
    return 'buy' if mvcd_line.iloc[-1] > signal_line.iloc[-1] and mvcd_line.iloc[-2] <= signal_line.iloc[-2] else 'sell' if mvcd_line.iloc[-1] < signal_line.iloc[-1] and mvcd_line.iloc[-2] >= signal_line.iloc[-2] else 'hold'
```

---

## **3. Volume Weighted Average Price (VWAP)**

### Description:
VWAP measures the average price of a security, weighted by trading volume, over a specified time period. It is a benchmark often used to determine if a security is trading at a fair price.

### Calculation:
- **Typical Price**: Average of High, Low, and Close prices.
- **VWAP**: Rolling sum of (Typical Price * Volume) divided by rolling sum of Volume.

### Signal Logic:
- **Buy Signal**: Current price crosses above VWAP.
- **Sell Signal**: Current price crosses below VWAP.
- **Hold**: No crossover is detected.

### Code Snippet:
```python
def calculate_vwap(prices, vwap_window=20):
    typical_price = (prices['high'] + prices['low'] + prices['close']) / 3
    rolling_cumulative_price_volume = (typical_price * prices['volume']).rolling(window=vwap_window).sum()
    rolling_cumulative_volume = prices['volume'].rolling(window=vwap_window).sum()
    vwap = rolling_cumulative_price_volume / rolling_cumulative_volume
    return 'buy' if prices['close'].iloc[-1] > vwap.iloc[-1] and prices['close'].iloc[-2] <= vwap.iloc[-2] else 'sell' if prices['close'].iloc[-1] < vwap.iloc[-1] and prices['close'].iloc[-2] >= vwap.iloc[-2] else 'hold'
```

---

## **4. Triple Exponential Moving Average (TEMA)**

### Description:
TEMA reduces the lag associated with moving averages by combining three EMAs, making it more responsive to price changes.

### Calculation:
- **EMA1**: Standard EMA.
- **EMA2**: EMA of EMA1.
- **EMA3**: EMA of EMA2.
- **TEMA**: Combines EMA1, EMA2, and EMA3 using the formula: `3 * (EMA1 - EMA2) + EMA3`.

### Signal Logic:
- **Buy Signal**: Current price crosses above TEMA.
- **Sell Signal**: Current price crosses below TEMA.
- **Hold**: No crossover is detected.

### Code Snippet:
```python
def calculate_tema(prices, window=20):
    ema1 = prices.ewm(span=window, adjust=False).mean()
    ema2 = ema1.ewm(span=window, adjust=False).mean()
    ema3 = ema2.ewm(span=window, adjust=False).mean()
    tema = 3 * (ema1 - ema2) + ema3
    return 'buy' if prices.iloc[-1] > tema.iloc[-1] and prices.iloc[-2] <= tema.iloc[-2] else 'sell' if prices.iloc[-1] < tema.iloc[-1] and prices.iloc[-2] >= tema.iloc[-2] else 'hold'
```

---

## **5. Signal Aggregation**

### Description:
Aggregates signals from multiple indicators using a weighted average to generate a final trading decision.

### Logic:
- **Buy**: Weighted score > 0.5.
- **Sell**: Weighted score < -0.5.
- **Hold**: Weighted score between -0.5 and 0.5.

### Code Snippet:
```python
def aggregate_signals(signals, weights):
    weighted_sum = sum(weights[indicator] * (1 if signal == 'buy' else -1 if signal == 'sell' else 0) for indicator, signal in signals.items())
    normalized_score = weighted_sum / sum(weights.values())
    return 'buy' if normalized_score > 0.5 else 'sell' if normalized_score < -0.5 else 'hold'
```

---
