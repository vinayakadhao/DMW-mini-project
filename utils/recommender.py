from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from scipy.sparse import hstack, csr_matrix
import numpy as np

def build_feature_matrix(df):
    text_col = "text_blob"
    tfidf = TfidfVectorizer(max_features=4000, ngram_range=(1, 2))
    tfidf_matrix = tfidf.fit_transform(df[text_col])
    
    audio_cols = ["danceability","energy","loudness","speechiness","acousticness",
                  "instrumentalness","liveness","valence","tempo"]
    scaler = StandardScaler()
    audio_matrix = scaler.fit_transform(df[audio_cols])
    combined = hstack([tfidf_matrix, csr_matrix(audio_matrix)], format="csr")
    return combined, tfidf, scaler

def recommend_songs(idx, df, feature_matrix, n=10):
    song_vec = feature_matrix[idx]
    sim_scores = cosine_similarity(song_vec, feature_matrix).flatten()
    sim_scores[idx] = -1
    top_idx = np.argsort(sim_scores)[::-1][:n]
    recs = df.iloc[top_idx].copy()
    recs['similarity'] = sim_scores[top_idx]
    return recs
