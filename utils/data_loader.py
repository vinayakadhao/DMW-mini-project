import pandas as pd
import numpy as np

def load_data(path):
    df = pd.read_csv(path, low_memory=False)
    # Normalize columns
    df.columns = [c.strip() for c in df.columns]
    # Basic cleaning
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)
    # Ensure expected columns exist
    for col in ["track_name", "artists", "album_name"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
    # Coerce numeric columns safely
    numeric_cols = [
        "danceability","energy","loudness","speechiness","acousticness",
        "instrumentalness","liveness","valence","tempo","popularity"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def preprocess_artists(df):
    # Split multiple artists by ';'
    df['artists_split'] = df['artists'].apply(lambda x: [a.strip() for a in str(x).split(';') if a.strip()])
    # Fill missing values with column medians for numeric cols
    num_cols = ["danceability","energy","loudness","speechiness","acousticness",
                "instrumentalness","liveness","valence","tempo","popularity"]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    # Popularity fallback if missing or entirely NaN
    if 'popularity' not in df.columns or df['popularity'].isna().all():
        feature_cols = [c for c in ["danceability","energy","valence","tempo"] if c in df.columns]
        if feature_cols:
            df['popularity'] = df[feature_cols].mean(axis=1)
        else:
            df['popularity'] = 50.0
    # Skip building large text blobs to reduce preprocessing time
    return df
