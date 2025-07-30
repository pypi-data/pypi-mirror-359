from atrax import Dataset
from atrax import Atrax as tx
from .utils import rolling_mean

def prep_data(ds: Dataset, sale_date, sale_col) -> Dataset:
    """
    Preprocess the dataset by setting up the date column.
    
    Args:
        ds (DataSet): The dataset to preprocess.
        
    Returns:
        DataSet: The preprocessed dataset with NaN values removed.
    """
    ds[sale_date] = tx.to_datetime(ds[sale_date])
    ds = ds.sort_values(by=sale_date)

    ds['trend'] = rolling_mean(ds[sale_col], window=7)
    ds['day_of_week'] = ds[sale_date].dt.weekday
    ds['is_weekend'] = ds[sale_date].dt.is_weekend.astype(int)
    ds['lag_1'] = ds[sale_col].shift(1)
    ds['lag_7'] = ds[sale_col].shift(7)
    ds['lag_mean_1_7'] = ds[['lag_1', 'lag_2']].mean(axis=1)

    ds = ds.dropna()

    features = ['day_of_week', 'is_weekend', 'lag_1', 'lag_7', 'trend', 'lag_mean_1_7']
    X = ds[features]
    y = ds[sale_col]

    return X, y, features