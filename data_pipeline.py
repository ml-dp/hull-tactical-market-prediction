
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LiveDataHandler:
    """
    Handles fetching live market data and engineering features for real-time prediction.
    """
    def __init__(self, ticker: str = "SPY"):
        self.ticker = ticker
        self.data = None

    def fetch_data(self, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical data for the specified ticker from Yahoo Finance.
        """
        logging.info(f"Fetching {period} of {interval} data for {self.ticker}...")
        self.data = yf.download(self.ticker, period=period, interval=interval)
        
        if self.data.empty:
            logging.error(f"No data fetched for ticker {self.ticker}. Please check the ticker symbol.")
            return pd.DataFrame()
        
        # --- FIX: Robustly flatten column index ---
        if isinstance(self.data.columns, pd.MultiIndex):
            # If it's a multi-index, take the first level (e.g., 'Open', 'Close')
            self.data.columns = self.data.columns.get_level_values(0)

        # Now, ensure all column names are lowercase strings
        self.data.columns = [str(col).lower().replace(' ', '_') for col in self.data.columns]
        
        logging.info(f"Data fetched successfully. Shape: {self.data.shape}")
        return self.data

    def create_features(self) -> pd.DataFrame:
        """
        Engineers a comprehensive set of technical analysis features on the fetched data.
        """
        if self.data is None or self.data.empty:
            logging.error("Data not fetched. Please call fetch_data() before creating features.")
            return pd.DataFrame()

        logging.info("Starting feature engineering for live data...")

        custom_strategy = ta.Strategy(
            name="Comprehensive TA",
            description="A mix of momentum, volatility, and trend indicators",
            ta=[
                {"kind": "rsi", "length": 14},
                {"kind": "macd", "fast": 12, "slow": 26, "signal": 9},
                {"kind": "bbands", "length": 20, "std": 2},
                {"kind": "atr", "length": 14},
                {"kind": "ema", "length": 50},
                {"kind": "ema", "length": 200},
                {"kind": "adx", "length": 14},
                {"kind": "obv"},
                {"kind": "stoch", "k": 14, "d": 3},
                {"kind": "cmf", "length": 20},
                {"kind": "psar"},
            ]
        )

        self.data.ta.strategy(custom_strategy)

        # Price-to-Moving-Average Ratios
        if 'ema_50' in self.data.columns and 'ema_200' in self.data.columns:
            self.data['price_to_ema50'] = self.data['close'] / self.data['EMA_50']
            self.data['price_to_ema200'] = self.data['close'] / self.data['EMA_200']
            self.data['ema50_to_ema200'] = self.data['EMA_50'] / self.data['EMA_200']

        # Lagged Returns
        for lag in [1, 3, 5, 10, 21]:
            self.data[f'return_{lag}d'] = self.data['close'].pct_change(lag)

        self.data.dropna(inplace=True)

        logging.info(f"Feature engineering complete. Final data shape: {self.data.shape}")
        logging.info(f"Available columns: {self.data.columns.tolist()}")

        return self.data

# Example Usage
if __name__ == "__main__":
    pipeline = LiveDataHandler(ticker="SPY")
    raw_data = pipeline.fetch_data(period="5y")
    
    if not raw_data.empty:
        featured_data = pipeline.create_features()
        
        print("\n" + "="*50)
        print("Live Data Pipeline - Sample Output")
        print("="*50)
        print("Data Head with Features:")
        print(featured_data.head())
        print("\nData Tail with Features:")
        print(featured_data.tail())
        print(f"\nTotal features created: {len(featured_data.columns)}")
