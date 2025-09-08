import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from sklearn.impute import KNNImputer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
import category_encoders as ce
import os

def load_data(csv_path: str, label_column: str = "policyType") -> Tuple[pd.DataFrame, Optional[pd.Series]]:
    df = pd.read_csv(csv_path)
    if label_column in df.columns:
        y = df[label_column]
        X = df.drop(columns=[label_column])
    else:
        raise ValueError(f"Label column '{label_column}' not found in the data.")
    return X, y

def parse_date_columns(df: pd.DataFrame, date_cols: List[str]) -> pd.DataFrame:
    """Parse date columns to datetime then expand to year/month/day numeric features for modeling."""
    df = df.copy()
    for col in date_cols:
        if col not in df.columns:
            continue
        dates = pd.to_datetime(df[col], errors="coerce")
        df[f"{col}_year"] = dates.dt.year
        df[f"{col}_month"] = dates.dt.month
        df[f"{col}_day"] = dates.dt.day
        df = df.drop(columns=[col])
    return df

def impute_numeric_with_knn(df: pd.DataFrame, n_neighbors: int = 3) -> pd.DataFrame:
    """Replicates notebook step: KNN imputation for numeric columns only."""
    result = df
    numeric_cols = result.select_dtypes(include=[np.number]).columns.tolist()
    if len(numeric_cols) == 0:
        return result
    imputer = KNNImputer(n_neighbors=n_neighbors)
    result[numeric_cols] = imputer.fit_transform(result[numeric_cols])
    return result

def cast_categoricals(df: pd.DataFrame, categorical_cols: List[str]) -> pd.DataFrame:
    result = df
    for col in categorical_cols:
        if col in result.columns:
            result[col] = result[col].astype("category")
    return result

def fill_categorical_by_segment(df: pd.DataFrame, categorical_cols: List[str]) -> pd.DataFrame:
    """Fill categorical nulls by per-location mode with global fallback."""
    result = df.copy()
    
    # Handle 'location' column if it exists
    if 'location' in result.columns:
        result['location'].fillna(result['location'].mode()[0], inplace=True)

    cat_cols = [c for c in categorical_cols if c in result.columns and c != 'location']

    for col in cat_cols:
        grouped = result.groupby('location')[col]
        
        for location, group in grouped:
            mode_value = group.mode()
            
            if not mode_value.empty:
                mode_value = mode_value.iloc[0]
            else:
                mode_value = result[col].mode()[0]
            
            result.loc[result['location'] == location, col] = result.loc[result['location'] == location, col].fillna(mode_value)

    return result

def encode_features(df: pd.DataFrame, text_cols: List[str], high_card_cols:List[str], low_card_cols: List[str], max_features = 500, ngram = (1, 2), label_column: str = "policyType") -> pd.DataFrame:
    """ This function deals with encoding categorical and textual data"""
    
    encoded_df = df.copy()
    for col in text_cols:
        encoded_df[col] = df[col].fillna(" ")
        tfidf_vectorizer = TfidfVectorizer(max_features=max_features, ngram_range= ngram)
        tfidf_matrix = tfidf_vectorizer.fit_transform(encoded_df[col])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=tfidf_vectorizer.get_feature_names_out(), index=encoded_df.index)
        encoded_df = pd.concat([encoded_df.drop(columns=[col]), tfidf_df], axis=1)
    
    one_hot_encode = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
    low_encoded_df = one_hot_encode.fit_transform(encoded_df[low_card_cols])
    encoded_column_name = one_hot_encode.get_feature_names_out(low_card_cols)
    one_hot_df = pd.DataFrame(low_encoded_df, columns=encoded_column_name, index=encoded_df.index)
    encoded_df = pd.concat([encoded_df.drop(columns=low_card_cols), one_hot_df], axis=1)
    
    for col in high_card_cols: 
        target_encoder = ce.TargetEncoder(cols=[col])
        temp_df = encoded_df[[col, label_column]].copy()
        temp_df[label_column] = pd.factorize(temp_df[label_column])[0]
        encoded_df[col] = target_encoder.fit_transform(temp_df[[col]], temp_df[label_column])
    
    return encoded_df

def clean_data(csv_path, date_cols, categorical_cols, text_cols, high_card_cols, low_card_cols) -> pd.DataFrame:
    """Runs all functions one at a time"""
    
    X, y = load_data(csv_path)

    X['policyType'] = y

    df = parse_date_columns(X, date_cols)
    df = impute_numeric_with_knn(df)
    df = cast_categoricals(df, categorical_cols)
    df = fill_categorical_by_segment(df, categorical_cols)
    df = encode_features(df=df, label_column='policyType', text_cols=text_cols, high_card_cols=high_card_cols, low_card_cols=low_card_cols)
    
    df = df.drop(columns=['policyType'], axis=1)
    
    return df, y


if __name__ == "__main__":
    csv_path = r"C:\Users\hp\Downloads\insuranceRecommendation\insurance_data.csv"
    
    date_cols = ['claimDate', 'renewalDate', 'issuanceDate', 'expiryDate', 'interactionDate']
    categorical_cols = ['gender', 'maritalStatus', 'claimType', 'renewalStatus', 'interactionType']
    high_card_cols = ['location']
    text_cols = ['claimHistory', 'policyHistory', 'coverageDetails']
    low_card_cols = ['gender', 'maritalStatus', 'claimType', 'renewalStatus', 'interactionType']
    
    clean_data(csv_path, date_cols=date_cols, categorical_cols=categorical_cols, text_cols=text_cols, high_card_cols=high_card_cols, low_card_cols=low_card_cols)





    