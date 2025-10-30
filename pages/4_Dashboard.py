# pages/4_Dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data, preprocess_artists
from utils.ui import inject_global_css, render_page_header, card, footer

st.set_page_config(page_title="User Dashboard", layout="wide")
inject_global_css()
render_page_header("Music Listening Dashboard", "Insights from your curated selection.", "📊")

# ---------- Load dataset ----------
DATA_PATH = r"C:\Users\vinay\OneDrive\Desktop\DMW mini project\dataset.csv"

@st.cache_data(show_spinner=False)
def load_prepared_data(path):
    df = load_data(path)
    df = preprocess_artists(df)
    return df

df = load_prepared_data(DATA_PATH)
# --- Handle missing popularity column ---
if "popularity" not in df.columns:
    # Create a pseudo popularity metric using available audio features
    feature_cols = [c for c in ["danceability", "energy", "valence", "tempo"] if c in df.columns]
    if feature_cols:
        df["popularity"] = df[feature_cols].mean(axis=1)
    else:
        df["popularity"] = np.random.uniform(40, 80, len(df))  # fallback random values

# ---------- Check if user has preferences ----------
if "curated_list" not in st.session_state or not st.session_state.curated_list:
    st.warning("⚠️ No user preferences found. Please create your curated list on the Preferences page first.")
    st.stop()

curated_df = pd.DataFrame(st.session_state.curated_list)
# Enrich curated_df with popularity from main df to avoid NA
if 'popularity' not in curated_df.columns or curated_df['popularity'].isna().all():
    # match by track_name (case-insensitive); if duplicates, take max popularity
    pop_map = df.groupby(df['track_name'].str.lower())['popularity'].max()
    curated_df['popularity'] = curated_df['track_name'].str.lower().map(pop_map)
    # fallback if still missing
    if curated_df['popularity'].isna().any():
        # compute from features where possible by joining on track name
        if {'danceability','energy','valence','tempo'}.issubset(set(df.columns)):
            feat_map = df.set_index(df['track_name'].str.lower())[['danceability','energy','valence','tempo']].mean(axis=1)
            curated_df['popularity'] = curated_df['popularity'].fillna(curated_df['track_name'].str.lower().map(feat_map))
        curated_df['popularity'] = curated_df['popularity'].fillna(curated_df['popularity'].median())
st.markdown("### 🎧 Your Selected (Curated) Songs")
# ✅ Safe column display fix
display_cols = ["track_name", "artists", "album_name", "track_genre"]

# Only add popularity if it exists in dataset
if "popularity" in curated_df.columns:
    display_cols.append("popularity")

with card("Curated songs"):
    st.dataframe(curated_df[display_cols])


# ---------- Derive Analytics ----------
st.markdown("## 📈 Listening Habit Insights")

# Handle multi-artist cells (split by ;)
artists_expanded = curated_df.assign(artists=curated_df["artists"].str.split(";"))
artists_exploded = artists_expanded.explode("artists")
artists_exploded["artists"] = artists_exploded["artists"].str.strip()

# Top Artists
top_artists = artists_exploded["artists"].value_counts().head(5)
fig_artists = px.bar(
    x=top_artists.index,
    y=top_artists.values,
    title="🎤 Top Artists You Prefer",
    labels={"x": "Artist", "y": "Count"},
    color=top_artists.values,
)
fig_artists.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0))
with card("Top Artists You Prefer"):
    st.plotly_chart(fig_artists, use_container_width=True)

# Top Genres
top_genres = curated_df["track_genre"].value_counts().head(5)
fig_genres = px.pie(
    names=top_genres.index,
    values=top_genres.values,
    title="🎶 Favorite Genres Distribution",
)
fig_genres.update_layout(height=480, margin=dict(l=10, r=10, t=50, b=0))
with card("Favorite Genres Distribution"):
    st.plotly_chart(fig_genres, use_container_width=True)

# Top Albums
top_albums = curated_df["album_name"].value_counts().head(5)
fig_albums = px.bar(
    x=top_albums.index,
    y=top_albums.values,
    title="💿 Most Frequent Albums in Your List",
    labels={"x": "Album", "y": "Count"},
    color=top_albums.values,
)
fig_albums.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0))
with card("Most Frequent Albums"):
    st.plotly_chart(fig_albums, use_container_width=True)

# ---------- Popularity Trends ----------
if "popularity" in curated_df.columns:
    st.markdown("### 🌟 Popularity Trend of Your Selected Songs")
    pop_df = curated_df.sort_values("popularity", ascending=False)
    fig_pop = px.line(
        pop_df,
        x="track_name",
        y="popularity",
        markers=True,
        title="Song Popularity Across Your Preferences",
        labels={"track_name": "Track Name", "popularity": "Popularity"},
    )
    fig_pop.update_layout(hovermode="x unified", height=460, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-20)
    with card("Popularity trend"):
        st.plotly_chart(fig_pop, use_container_width=True)

# ---------- Audio Feature Distribution ----------
numeric_cols = [col for col in curated_df.select_dtypes(include="number").columns if col not in ["popularity"]]
if numeric_cols:
    st.markdown("### 🎚️ Audio Feature Comparison")
    feature = st.selectbox("Select an audio feature to compare:", numeric_cols)
    fig_feat = px.histogram(
        curated_df,
        x=feature,
        nbins=10,
        title=f"Distribution of {feature} across your curated songs",
        color_discrete_sequence=["#1DB954"],
    )
    fig_feat.update_layout(hovermode="x unified", height=460, margin=dict(l=10, r=10, t=50, b=0))
    with card("Audio feature distribution"):
        st.plotly_chart(fig_feat, use_container_width=True)

# ---------- Insights Summary ----------
st.markdown("## 🧠 Key Insights")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Number of Favorite Songs", value=len(curated_df))
    st.metric(label="Unique Artists", value=artists_exploded['artists'].nunique())
with col2:
    st.metric(label="Unique Genres", value=curated_df['track_genre'].nunique())
st.metric(label="Average Popularity", value=round(curated_df["popularity"].mean(), 2))

st.success("✅ Dashboard generated based on your listening preferences!")
footer("Metrics reflect your currently curated list; adjust it to see changes live.")

