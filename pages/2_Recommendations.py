import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from utils.data_loader import load_data, preprocess_artists
from utils.ui import inject_global_css, render_page_header, card, footer

st.set_page_config(page_title="Song Recommendations", layout="wide")
inject_global_css()
render_page_header("Personalized Song Recommendations (kNN)", "Find tracks similar to your curated choices.", "🎧")

import os
from utils.data_loader import load_data

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset.csv")


@st.cache_data(show_spinner=False)
def load_prepared_data(path):
    df = load_data(path)
    df = preprocess_artists(df)
    return df

df = load_prepared_data(DATA_PATH)

if "curated_list" not in st.session_state or not st.session_state.curated_list:
    st.warning("⚠️ You don't have any songs in your curated list yet. Go to the 'Preferences' page first.")
    st.stop()

curated_df = pd.DataFrame(st.session_state.curated_list)
with card("Your current curated songs"):
    st.table(curated_df[["track_name", "artists", "album_name", "track_genre"]])

numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
if not numeric_cols:
    st.error("No numeric features found in dataset for similarity computation.")
    st.stop()

@st.cache_resource(show_spinner=False)
def get_knn_artifacts(df_sig_cols, df_vals):
    scaler_local = StandardScaler()
    features32 = df_vals.astype("float32", copy=False)
    scaled_local = scaler_local.fit_transform(features32)
    model_local = NearestNeighbors(metric="cosine", algorithm="brute")
    model_local.fit(scaled_local)
    return scaler_local, scaled_local, model_local

df_signature = (tuple(numeric_cols), float(df[numeric_cols].sum(numeric_only=True).sum()))
scaler, scaled_features, model = get_knn_artifacts(df_signature, df[numeric_cols].values)

st.markdown("### Configure Recommendation Settings")

num_centroids = st.slider("How many curated songs to use as centroids", min_value=1, max_value=min(10, len(curated_df)), value=min(3, len(curated_df)), step=1)
num_neighbors = st.slider("Number of recommendations per centroid", min_value=5, max_value=20, value=10, step=1)

centroid_choices = st.multiselect(
    "Choose centroid songs (used to find similar tracks)",
    options=curated_df["track_name"].tolist(),
    default=curated_df["track_name"].tolist()[:num_centroids],
    max_selections=num_centroids
)
if len(centroid_choices) > num_centroids:
    st.warning("You selected more songs than the chosen centroid count; only the first N will be used.")
    centroid_choices = centroid_choices[:num_centroids]


recommendations = []

for source_name in centroid_choices:
    matches = df[df["track_name"].str.lower() == source_name.lower()]
    if matches.empty:
        continue
    idx = matches.index[0]
    distances, indices = model.kneighbors([scaled_features[idx]], n_neighbors=num_neighbors + 1)
    rec_indices = indices.flatten()[1:]
    rec_songs = df.iloc[rec_indices]
    rec_songs = rec_songs[~rec_songs["track_name"].isin(curated_df["track_name"])]
    rec_songs["source_song"] = source_name
    recommendations.append(rec_songs.head(num_neighbors))

if recommendations:
    rec_df = pd.concat(recommendations).reset_index(drop=True)
    st.success(f"Generated {len(rec_df)} total recommended songs across {len(curated_df)} curated songs.")
else:
    st.warning("No matching songs found for your curated list in the dataset.")
    st.stop()

st.markdown("### Recommended Songs Overview")

for source_name in centroid_choices:
    subset = rec_df[rec_df["source_song"] == source_name].head(num_neighbors)
    if subset.empty:
        continue
    with card(f"Songs like {source_name}"):
        display = subset[["track_name", "artists", "album_name", "track_genre", "popularity"]].copy()
        display.insert(0, "No.", range(1, len(display) + 1))
        st.dataframe(display)

st.markdown("#### Popularity comparison")
import plotly.express as px
for source_name in centroid_choices:
    subset = rec_df[rec_df["source_song"] == source_name].head(num_neighbors)
    if subset.empty:
        continue
    source_pop = df.loc[df["track_name"].str.lower() == source_name.lower(), "popularity"].mean()
    bar_df = subset.copy().assign(kind="Recommendation")
    source_row = {"track_name": source_name, "popularity": source_pop, "kind": "Source"}
    bar_df = pd.concat([pd.DataFrame([source_row]), bar_df[["track_name", "popularity", "kind"]]])
    fig_pop = px.bar(bar_df, x="track_name", y="popularity", color="kind", title=f"Popularity comparison for '{source_name}'")
    fig_pop.update_layout(hovermode="x unified", height=420, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-25)
    st.plotly_chart(fig_pop, use_container_width=True)

if not rec_df.empty:
    csv = rec_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 Download all recommendations as CSV",
        data=csv,
        file_name="recommendations_by_centroids.csv",
        mime="text/csv",
    )
footer("Pro tip: Tweak number of recommendations to broaden or focus results.")

