# Revised Project Plan: Algorithmic Trading Model

**Objective:** Develop a robust, real-time algorithmic trading model by enhancing an initial Kaggle-based solution with live data, advanced feature engineering, and a professional development workflow, including comprehensive options data analysis.

---

### Step 1: Initial Setup & Environment Configuration (Completed)
- **Task:** Establish a clean, isolated virtual environment for the project.
- **Details:** Created a `venv` and installed all necessary dependencies (`numpy==2.2.0`, `pandas-ta`, `yfinance`, etc.) from a `requirements.txt` file to resolve library version conflicts.
- **Status:** Done.

### Step 2: Data Exploration & Initial Cleaning (Completed)
- **Task:** Analyze the initial `train.csv` dataset to understand its structure and identify missing values.
- **Details:** Used pandas for initial data loading and `seaborn`/`matplotlib` to create heatmaps and bar charts visualizing the percentage of missing data per feature. This informed our data cleaning and imputation strategy.
- **Status:** Done.

### Step 3: Advanced Feature Engineering & Modeling (Completed)
- **Task:** Engineer new features and build a stacked ensemble model.
- **Details:** 
    - Used `polars` for high-performance data manipulation.
    - Created derived features and interaction terms from the original Kaggle dataset.
    - Imputed missing values using forward-fills and median values.
    - Trained three base models (ElasticNet, XGBoost, LightGBM) on a reduced feature set.
    - Trained a `LinearRegression` meta-learner on the predictions of the base models.
- **Status:** Done.

### Step 4: Volatility-Adjusted Allocation Strategy (Completed)
- **Task:** Develop a function to translate model predictions into a risk-adjusted allocation strategy.
- **Details:** Created a `get_allocations` function that estimates volatility and uses it to scale, clip, and smooth the raw model output. Backtested the strategy against the training data to validate performance.
- **Status:** Done.

### Step 5: Real-Time Implementation & Advanced Feature Engineering

**5a. Live Data Pipeline for Equities (In Progress)**
- **Task:** Transition from the static Kaggle dataset to a live data pipeline using `yfinance`.
- **Details:** 
    - Create `data_pipeline.py`.
    - Fetch historical S&P 500 (SPY) data, ensuring column names are correctly flattened and standardized.
    - Manually engineer a robust set of technical analysis features (RSI, MACD, Bollinger Bands, etc.) using direct calls to `pandas-ta` functions for better portability.

**5b. New: Comprehensive Options Data Pipeline & Feature Engineering**
- **Task:** Extend the data pipeline to fetch and engineer a wide array of features from options chain data to capture forward-looking market sentiment and positioning.
- **Details:**
    - In `data_pipeline.py`, add functionality to fetch full options chain data (calls and puts) for multiple near-term expiration dates for SPY.
    - **Sentiment & Flow Analysis:** Calculate Put/Call ratios based on both daily volume and open interest to gauge trader sentiment.
    - **Volatility Structure Analysis:**
        - Calculate and track at-the-money (ATM) Implied Volatility as a core 'fear gauge'.
        - Analyze the **Volatility Skew** by comparing the IV of out-of-the-money (OTM) puts versus OTM calls. A steep skew indicates high demand for downside protection.
        - Analyze the **Term Structure** by comparing IV between short-term and longer-term options to understand expectations of future volatility.
    - **Greeks Exposure Analysis:**
        - Aggregate key Greeks (Delta, Gamma, Vega, Theta, Vanna) across the entire options chain.
        - Calculate **Net Delta and Net Gamma exposure** to estimate dealer positioning, which can indicate potential price pinning or acceleration points (i.e., 'Gamma Flips').
        - Analyze 'Charm' (Delta decay over time) to predict positioning changes as expiration approaches.
    - These new features will serve as a rich, forward-looking input for a next-generation predictive model.

**5c. Dashboard Creation**
- **Task:** Build an interactive dashboard to visualize the model's real-time predictions and the new options data insights.
- **Details:** 
    - Use a library like `streamlit` or `dash`.
    - Create visualizations for the live model allocation signal.
    - Add new charts for advanced options analysis, including plots of the volatility skew/smile, Put/Call ratios over time, and net Gamma exposure to provide a complete market outlook.

---
