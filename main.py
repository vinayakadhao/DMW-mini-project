import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data, preprocess_artists
from utils.ui import inject_global_css, render_page_header, card, footer

st.set_page_config(page_title="Music Recommender", layout="wide")
inject_global_css()
render_page_header(
    title="Music Listening Habit Analysis & Personalized Song Recommendation System",
    subtitle="By Vinayak Adhao and Soham Kolte",
    emoji="🎵",
)

with card():
    st.markdown("""
    ### 📘 Project Overview
    Analyze listening habits and get personalized song and playlist suggestions using audio features and your curated choices.

    ### 🚀 Features
    - Pick favorites in Preferences; we’ll use them as centroids for recommendations  
    - kNN-based recommendations:With popularity comparisons  
    - K-Means playlisting: adjustable number of clusters and playlist size, labeled by centroid song  
    - Interactive Dashboard: top artists/albums by popularity and feature distributions  
    """)

import os
from utils.data_loader import load_data

DATA_PATH = os.path.join(os.path.dirname(__file__), "dataset.csv")
df = load_data(DATA_PATH)
df = preprocess_artists(df)

st.markdown("## 🎧 Dataset Insights — Top 10 Only")

tabs = st.tabs(["Artists", "Songs", "Albums"])

with tabs[0]:
    with card("Top 10 Artists"):
        if 'popularity' in df.columns:
            exploded = df[['artists_split','popularity']].explode('artists_split')
            by_artist = exploded.groupby('artists_split', as_index=False)['popularity'].mean().sort_values('popularity', ascending=False)
            top_artists = by_artist.head(10)
            fig2 = px.bar(top_artists, x='artists_split', y='popularity', title="Top 10 Artists (mean popularity)")
        else:
            all_artists = [a.strip() for sublist in df['artists_split'] for a in sublist]
            counts = pd.Series(all_artists).value_counts().head(10)
            fig2 = px.bar(counts, x=counts.index, y=counts.values, title="Top 10 Artists (count)")
        fig2.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0))
        st.plotly_chart(fig2, use_container_width=True)

with tabs[1]:
    with card("Top 10 Songs"):
        top_songs = df.sort_values('popularity', ascending=False).head(10) if 'popularity' in df.columns else df.head(10)
        fig3 = px.bar(top_songs, x='track_name', y='popularity', title="Top 10 Songs by Popularity")
        fig3.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)

with tabs[2]:
    with card("Top 10 Albums"):
        if 'popularity' in df.columns:
            top_albums = df.groupby('album_name', as_index=False)['popularity'].mean().sort_values('popularity', ascending=False).head(10)
            fig4 = px.bar(top_albums, x='album_name', y='popularity', title="Top 10 Albums (mean popularity)")
        else:
            counts = df['album_name'].value_counts().head(10)
            fig4 = px.bar(counts, x=counts.index, y=counts.values, title="Top 10 Albums (count)")
        fig4.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-25)
        st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")
footer("Navigate via the sidebar to explore Preferences, Recommendations, Playlists, and the Dashboard.")

