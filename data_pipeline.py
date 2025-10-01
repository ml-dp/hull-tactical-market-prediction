
import yfinance as yf
import pandas_ta as ta
import pandas as pd
import numpy as np
import logging
from typing import Tuple, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LiveDataHandler:
    """
    Handles fetching live market data (equity and options) and engineering a comprehensive feature set.
    """
    def __init__(self, ticker: str = "SPY"):
        self.ticker = ticker
        self.tk = yf.Ticker(self.ticker)
        self.data = None
        self.options_data = None

    def fetch_data(self, period: str = "5y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches and preprocesses historical equity data.
        """
        logging.info(f"Fetching {period} of {interval} data for {self.ticker}...")
        self.data = self.tk.history(period=period, interval=interval, auto_adjust=False, progress=False)
        if self.data.empty:
            logging.error(f"No data fetched for ticker {self.ticker}.")
            return pd.DataFrame()

        self.data.columns = [str(col).lower().replace(' ', '_') for col in self.data.columns]
        logging.info(f"Equity data fetched. Shape: {self.data.shape}")
        return self.data

    def create_equity_features(self) -> pd.DataFrame:
        """
        Engineers technical analysis features on the fetched equity data.
        """
        if self.data is None or self.data.empty:
            logging.error("Equity data not fetched. Call fetch_data() first.")
            return pd.DataFrame()

        logging.info("Starting equity feature engineering...")
        
        # Manually append indicators
        self.data.ta.rsi(length=14, append=True)
        self.data.ta.macd(fast=12, slow=26, signal=9, append=True)
        self.data.ta.bbands(length=20, std=2, append=True)
        self.data.ta.atr(length=14, append=True)
        self.data.ta.ema(length=50, append=True)
        self.data.ta.ema(length=200, append=True)
        self.data.ta.adx(length=14, append=True)
        self.data.ta.obv(append=True)
        self.data.ta.stoch(k=14, d=3, append=True)
        self.data.ta.cmf(length=20, append=True)
        self.data.ta.psar(append=True)

        # Additional Custom Features
        if 'ema_50' in self.data.columns and 'ema_200' in self.data.columns:
            self.data['price_to_ema50'] = self.data['close'] / self.data['ema_50']
            self.data['price_to_ema200'] = self.data['close'] / self.data['ema_200']
            self.data['ema50_to_ema200'] = self.data['ema_50'] / self.data['ema_200']

        for lag in [1, 3, 5, 10, 21]:
            self.data[f'return_{lag}d'] = self.data['close'].pct_change(lag)

        self.data.dropna(inplace=True)
        logging.info(f"Equity feature engineering complete. Final shape: {self.data.shape}")
        return self.data

    def fetch_and_analyze_options(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fetches options chain for near-term expirations and calculates comprehensive metrics.
        """
        logging.info(f"Fetching and analyzing options chain for {self.ticker}...")
        analysis = {}
        try:
            expirations = self.tk.options
            if not expirations:
                logging.warning(f"No options expiration dates found.")
                return pd.DataFrame(), {}

            # Analyze nearest two expiration dates
            options_dfs = []
            for exp in expirations[:2]:
                opt_chain = self.tk.option_chain(exp)
                calls = opt_chain.calls
                puts = opt_chain.puts
                calls['type'], puts['type'] = 'call', 'put'
                options_dfs.append(pd.concat([calls, puts]))

            self.options_data = pd.concat(options_dfs)
            df = self.options_data
            logging.info(f"Options data fetched for expirations: {expirations[:2]}. Total contracts: {len(df)}")

            # --- Sentiment & Flow Analysis ---
            put_volume = df[df['type'] == 'put']['volume'].sum()
            call_volume = df[df['type'] == 'call']['volume'].sum()
            analysis['put_call_volume_ratio'] = put_volume / call_volume if call_volume > 0 else np.nan

            put_oi = df[df['type'] == 'put']['openInterest'].sum()
            call_oi = df[df['type'] == 'call']['openInterest'].sum()
            analysis['put_call_oi_ratio'] = put_oi / call_oi if call_oi > 0 else np.nan

            # --- Volatility Structure ---
            atm_options = df.iloc[(df['strike'] - self.data['close'].iloc[-1]).abs().argsort()[:4]]
            analysis['atm_iv'] = atm_options['impliedVolatility'].mean()
            
            otm_puts = df[(df['type'] == 'put') & (df['inTheMoney'] == False)]
            otm_calls = df[(df['type'] == 'call') & (df['inTheMoney'] == False)]
            analysis['volatility_skew'] = otm_puts['impliedVolatility'].mean() - otm_calls['impliedVolatility'].mean()

            # --- Greeks Exposure ---
            df['notional_value'] = df['openInterest'] * df['strike'] * 100
            analysis['total_notional'] = df['notional_value'].sum()
            
            analysis['net_delta'] = (df['delta'] * df['notional_value']).sum() / analysis['total_notional']
            analysis['net_gamma'] = (df['gamma'] * df['notional_value']).sum() / analysis['total_notional']

            logging.info(f"Options analysis complete.")
            return df, analysis

        except Exception as e:
            logging.error(f"Failed during options processing: {e}")
            return pd.DataFrame(), {}

# --- Example Usage ---
if __name__ == "__main__":
    pipeline = LiveDataHandler(ticker="SPY")
    equity_data = pipeline.fetch_data(period="1y")
    
    if not equity_data.empty:
        featured_equity = pipeline.create_equity_features()
        options_df, options_analysis = pipeline.fetch_and_analyze_options()

        print("\n" + "="*50)
        print("Live Equity Data (Tail)")
        print("="*50)
        print(featured_equity.tail())

        if options_analysis:
            print("\n" + "="*50)
            print("Comprehensive Options Analysis")
            print("="*50)
            for key, value in options_analysis.items():
                print(f"- {key}: {value:.4f}")
