# pages/3_Playlist_Recommendation.py
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import plotly.express as px
from utils.data_loader import load_data, preprocess_artists
from utils.ui import inject_global_css, render_page_header, card, footer

st.set_page_config(page_title="Playlist Recommendation", layout="wide")
inject_global_css()
render_page_header("Playlist Recommendation using K-Means Clustering", "Group songs with similar audio profiles into playlists.", "🎶")

# ---------- Load dataset ----------
DATA_PATH = r"C:\Users\vinay\OneDrive\Desktop\DMW mini project\dataset.csv"

@st.cache_data(show_spinner=False)
def load_prepared_data(path):
    df = load_data(path)
    df = preprocess_artists(df)
    return df

df = load_prepared_data(DATA_PATH)

# ---------- Check curated list ----------
if "curated_list" not in st.session_state or not st.session_state.curated_list:
    st.warning("⚠️ You don't have any songs in your curated list yet. Please go to the 'Preferences' page first.")
    st.stop()

curated_df = pd.DataFrame(st.session_state.curated_list)
with card("Your current curated songs"):
    st.table(curated_df[["track_name", "artists", "album_name", "track_genre"]])

# ---------- Prepare numeric features ----------
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not numeric_cols:
    st.error("No numeric features found for clustering.")
    st.stop()

@st.cache_resource(show_spinner=False)
def get_scaled_features(df_sig_cols, df_vals):
    scaler_local = StandardScaler()
    features32 = df_vals.astype("float32", copy=False)
    scaled_local = scaler_local.fit_transform(features32)
    return scaler_local, scaled_local

df_signature = (tuple(numeric_cols), float(df[numeric_cols].sum(numeric_only=True).sum()))
scaler, scaled_features = get_scaled_features(df_signature, df[numeric_cols].values)

# ---------- Playlist Clustering ----------
st.markdown("### Configure Playlist Creation Settings")
max_clusters = max(1, min(50, max(1, len(curated_df) - 1)))
num_clusters = st.slider("Number of playlists (clusters)", min_value=1, max_value=max_clusters, value=min(3, max_clusters), step=1)
playlist_size = st.slider("Playlist size per cluster", min_value=10, max_value=50, value=10, step=1)

@st.cache_resource(show_spinner=False)
def fit_kmeans(sig, n_clusters):
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = km.fit_predict(sig)
    return km, labels

_, labels = fit_kmeans(scaled_features, num_clusters)
df["cluster"] = labels

# Assign curated songs to clusters
cluster_assignments = []
for _, row in curated_df.iterrows():
    match = df[df["track_name"].str.lower() == row["track_name"].lower()]
    if not match.empty:
        cluster_assignments.append(int(match["cluster"].iloc[0]))
curated_df["cluster"] = cluster_assignments if cluster_assignments else [None] * len(curated_df)

# ---------- Generate cluster-based recommendations ----------
playlist_recs = []
for c in curated_df["cluster"].dropna().unique():
    cluster_songs = df[df["cluster"] == c]
    cluster_songs = cluster_songs[~cluster_songs["track_name"].isin(curated_df["track_name"])]
    cluster_songs["playlist_cluster"] = c
    n_pick = min(playlist_size, len(cluster_songs))
    if n_pick == 0:
        continue
    sampled = cluster_songs.sample(n=n_pick, random_state=42)
    playlist_recs.append(sampled)

if playlist_recs:
    rec_df = pd.concat(playlist_recs).reset_index(drop=True)
    st.success(f"✅ Generated {len(rec_df)} playlist recommendations across {num_clusters} clusters.")
else:
    st.warning("No cluster-based recommendations could be generated.")
    st.stop()

# ---------- Visualization ----------
st.markdown("### Playlist Visualization")
fig = px.scatter_3d(
    df.sample(min(len(df), 1000)),
    x="danceability" if "danceability" in df.columns else numeric_cols[0],
    y="energy" if "energy" in df.columns else numeric_cols[1],
    z="valence" if "valence" in df.columns else numeric_cols[2],
    color="cluster",
    hover_data=["track_name", "artists", "album_name"],
    title="K-Means Clusters of Songs (based on audio features)"
)
fig.update_layout(height=620, margin=dict(l=10, r=10, t=50, b=0))
st.plotly_chart(fig, use_container_width=True)

# Show playlists one by one
st.markdown("### Playlist Details")
for cluster_id in sorted(rec_df["playlist_cluster"].unique()):
    playlist = rec_df[rec_df["playlist_cluster"] == cluster_id]
    # Find a centroid label from curated songs assigned to this cluster
    centroid_label = None
    match_curated = curated_df[curated_df["cluster"] == cluster_id]
    if not match_curated.empty:
        centroid_label = match_curated["track_name"].iloc[0]
    title = f"🎵 Playlist of songs similar to {centroid_label}" if centroid_label else f"🎵 Playlist for cluster {int(cluster_id)+1}"
    with st.expander(title):
        st.dataframe(playlist[["track_name", "artists", "album_name", "track_genre", "popularity"]].head(10))

# ---------- Download playlists ----------
csv = rec_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Download all playlists as CSV",
    data=csv,
    file_name="playlist_recommendations.csv",
    mime="text/csv",
)
footer("Note: Increase clusters for more granular playlists; decrease for broader grouping.")
