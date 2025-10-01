### Revised Project Plan: Elite Ensemble for Market Prediction

**Objective:** Develop a high-performance, adaptive modeling pipeline to predict S&P 500 excess returns. The solution will be an ensemble of models with a meta-learner, incorporate advanced feature engineering, and use online learning to adapt to new market data, with the ultimate goal of maximizing the competition's Sharpe-like metric.

**1. Data Preprocessing & Initial Analysis (with `polars`)**

*   **Efficient Data Loading:** Use the `polars` library for high-performance data manipulation.
*   **Initial Filtering:**
    *   Load `train.csv` and filter it to the most recent and relevant data (e.g., the last 1000 rows, `date_id >= 37`) to focus the model on the current market regime.
    *   Drop columns with a high percentage of missing values (e.g., > 50%) to reduce noise.
*   **Imputation Strategy:**
    *   For interest rate features (`I*`), use forward/backward fills.
    *   For other features, impute remaining missing values using the median. Cache these median values for consistent application on test data.

**2. Advanced Feature Engineering**

*   **Base Feature Set:** Define a core set of features by selecting prefixes (D, E, I, M, P, S, V).
*   **Derived Features:** Engineer new features to capture complex relationships, including:
    *   **Interest Rate Spreads:** `U1 = I2 - I1`
    *   **Economic Ratios:** `U2 = M11 / ((I2 + I9 + I7) / 3)`
    *   **Interaction Terms:** Create features by multiplying potentially related indicators, such as `V1 * S1`, `M11 * V1`, and `I9 * S1`.
*   **Lagged Features:** Incorporate `lagged_market_forward_excess_returns` from the test set as a predictive feature.

**3. Ensemble Model Development & Stacking**

*   **Base Models:** Train a diverse set of models on the preprocessed and engineered features:
    1.  **ElasticNet:** A robust linear model.
    2.  **XGBoost:** A powerful gradient boosting model.
    3.  **LightGBM:** A fast and efficient gradient boosting model.
*   **Feature Selection:**
    *   Use the feature importance scores from the initial XGBoost model to identify the top ~15 most predictive features.
    *   Retrain the base models using only this reduced, high-signal feature set.
*   **Stacking with a Meta-Learner:**
    *   Use the predictions from the three retrained base models as input features for a final `LinearRegression` meta-model.
    *   This meta-learner will determine the optimal weights for combining the base model predictions.

**4. Volatility-Adjusted Allocation Strategy**

*   **Volatility Estimation:**
    *   Implement a **GARCH-like model** to get a dynamic estimate of market volatility. This will combine the `V1` feature with the standard deviation of recent target returns.
*   **Signal Processing:**
    *   Take the raw prediction from the meta-model and scale it with a multiplier to create a stronger "signal."
    *   Clip the signal to the allowed allocation range `[0, 2]`.
*   **Final Allocation:**
    *   Adjust the signal based on the estimated volatility (i.e., reduce allocation in high-volatility regimes).
    *   Apply a smoothing function (e.g., a weighted average of the new and previous allocation) and account for transaction costs to create a more stable and realistic betting strategy.

**5. Online Learning and Submission**

*   **Adaptive Retraining:** Implement an online learning loop. As each new row of test data is processed:
    *   Append the `lagged_market_forward_excess_returns` to our training data as a new target value.
    *   Periodically retrain the entire ensemble and meta-learner to allow the model to adapt to the latest market data.
*   **Submission:**
    *   Integrate the entire pipeline—from feature creation to allocation—into the `predict` function required by the `kaggle_evaluation` API.
    *   Ensure the startup time and prediction runtime are within the competition's limits (900 seconds).