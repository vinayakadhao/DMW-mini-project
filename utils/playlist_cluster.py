from sklearn.cluster import KMeans
import pandas as pd

def build_clusters(df, n_clusters=3, audio_cols=None):
    if audio_cols is None:
        audio_cols = ["danceability","energy","loudness","speechiness","acousticness",
                      "instrumentalness","liveness","valence","tempo"]
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    df['cluster'] = kmeans.fit_predict(df[audio_cols])
    centroids = pd.DataFrame(kmeans.cluster_centers_, columns=audio_cols)
    return df, centroids
