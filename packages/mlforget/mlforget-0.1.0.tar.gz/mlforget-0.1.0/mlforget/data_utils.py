import os
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler


def load_dataset(path: str, required_columns: list = None) -> pd.DataFrame:
    """
    Loads a dataset from a file path, supporting multiple formats.

    Parameters:
    - path: path to the dataset file (CSV, Feather, Parquet)
    - required_columns: optional list of columns that must be present

    Returns:
    - Loaded pandas DataFrame

    Raises:
    - FileNotFoundError: if the file doesn't exist
    - ValueError: if file type is unsupported or required columns are missing
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext == ".feather" or ext == ".ft":
        df = pd.read_feather(path)
    elif ext == ".parquet":
        df = pd.read_parquet(path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return df

def preprocess_data(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Preprocesses the input DataFrame using a configurable schema.

    Parameters:
    - df: raw input DataFrame
    - config: dict with the following keys:
        - "timestamp_col": column with datetime
        - "target_col": target variable name
        - "categorical_cols": list of categorical columns to encode
        - "drop_cols": columns to drop entirely
        - "scale_cols": list of numerical features to scale

    Returns:
    - Processed DataFrame ready for modeling
    """
    df = df.copy()

    # 1. Parse and sort by timestamp
    if config.get("timestamp_col") in df.columns:
        df[config["timestamp_col"]] = pd.to_datetime(df[config["timestamp_col"]])
        df.sort_values(by=config["timestamp_col"], inplace=True)

    # 2. Handle missing values
    df.fillna(df.mean(numeric_only=True), inplace=True)

    # 3. Encode categorical columns
    for col in config.get("categorical_cols", []):
        if col in df.columns:
            df[col] = LabelEncoder().fit_transform(df[col].astype(str))

    # 4. Drop unnecessary columns
    for col in config.get("drop_cols", []):
        if col in df.columns:
            df.drop(columns=[col], inplace=True)

    # 5. Scale numerical columns
    if config.get("scale_cols"):
        scaler = StandardScaler()
        df[config["scale_cols"]] = scaler.fit_transform(df[config["scale_cols"]])

    return df

def select_forget_set(df, id_column, id_values):
    """
    Splits the input DataFrame into a forget set and a retain set
    based on a list of IDs in the given column.

    Parameters:
        df (pd.DataFrame): Full dataset
        id_column (str): Name of the column to match IDs
        id_values (list of int): List of IDs to forget

    Returns:
        forget_df (pd.DataFrame), retain_df (pd.DataFrame)
    """
    forget_df = df[df[id_column].isin(id_values)].copy()
    retain_df = df[~df[id_column].isin(id_values)].copy()
    return forget_df, retain_df
