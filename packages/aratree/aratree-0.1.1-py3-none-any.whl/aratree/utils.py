import numpy as np

def rolling_mean(series, window, min_periods=1):
    """
    Computes a rolling mean after the length of the rolling window is >= min_periods and >= window size.

    Parameters:
    - series: array-like numeric data
    - window: number of trailing points to use
    - min_periods: min required for mean (default = window)

    Returns:
    - Array of rolling mean values
    """
    if min_periods is None:
        min_periods = window

    result = []
    for i in range(len(series)):
        start = max(0, i - window + 1)
        window_vals = series.iloc[start:i+1].values

        if len(window_vals) >= min_periods and len(window_vals) >= window:
            result.append(np.mean(window_vals))
        else:
            result.append(np.nan)
    return result

def train_test_split(X, y, test_size=0.2):

    if len(X) != len(y):
        raise ValueError(f"X and y must have the same length. detected X: {len(X)}, y: {len(y)}")

    split_idx = int((1 - test_size) * len(X.data))

    X_train_series = X.iloc[:split_idx]
    X_test_series = X.iloc[split_idx:]

    X_train = np.array([list(d.values()) for d in X_train_series])
    X_test = np.array([list(d.values()) for d in X_test_series])

    y_train = np.array(y.values[:split_idx])
    y_test = np.array(y.values[split_idx:])


    return X_train, X_test, y_train, y_test



