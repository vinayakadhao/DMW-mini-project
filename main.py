import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import load_data, preprocess_artists
from utils.ui import inject_global_css, render_page_header, card, footer

# ---- PAGE CONFIG ----
st.set_page_config(page_title="Music Recommender", layout="wide")
inject_global_css()
render_page_header(
    title="Music Listening Habit Analysis & Personalized Song Recommendation System",
    subtitle="By Vinayak Adhao and Soham Kolte",
    emoji="🎵",
)

# ---- PROJECT OVERVIEW ----
with card():
    st.markdown("""
    ### 📘 Project Overview
    Analyze listening habits and get personalized song and playlist suggestions using audio features and your curated choices.

    ### 🚀 Features
    - Pick favorites in Preferences; we’ll use them as centroids for recommendations  
    - kNN-based recommendations: “Songs like <your song>” with popularity comparisons  
    - K-Means playlisting: adjustable number of clusters and playlist size, labeled by centroid song  
    - Interactive Dashboard: top artists/albums by popularity and feature distributions  
    """)

# ---- LOAD DATA ----
df = load_data(r"C:\Users\vinay\OneDrive\Desktop\DMW mini project\dataset.csv")
df = preprocess_artists(df)

# ---- TOP INSIGHTS ----
st.markdown("## 🎧 Dataset Insights")

tabs = st.tabs(["Artists", "Songs", "Albums"])

with tabs[0]:
    with card("Top Artists"):
        if 'popularity' in df.columns:
            exploded = df[['artists_split','popularity']].explode('artists_split')
            by_artist = exploded.groupby('artists_split', as_index=False)['popularity'].mean().sort_values('popularity', ascending=False)
            top_artists = by_artist.head(5)
            fig2 = px.bar(top_artists, x='artists_split', y='popularity', title="Top 5 Artists (by mean popularity)")
        else:
            all_artists = [a.strip() for sublist in df['artists_split'] for a in sublist]
            counts = pd.Series(all_artists).value_counts().head(5)
            fig2 = px.bar(counts, x=counts.index, y=counts.values, title="Top 5 Artists (count)")
        fig2.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0))
        st.plotly_chart(fig2, use_container_width=True)
        with st.expander("Show all artists"):
            if 'popularity' in df.columns:
                fig_full = px.bar(by_artist, x='artists_split', y='popularity', title="All Artists by Mean Popularity")
            else:
                all_artists = [a.strip() for sublist in df['artists_split'] for a in sublist]
                fig_full = px.bar(pd.Series(all_artists).value_counts(), title="All Artists (count)")
            fig_full.update_layout(hovermode="x unified", height=520, margin=dict(l=10, r=10, t=50, b=0))
            st.plotly_chart(fig_full, use_container_width=True)

with tabs[1]:
    with card("Top Songs"):
        top_songs = df.sort_values('popularity', ascending=False).head(5) if 'popularity' in df.columns else df.head(5)
        fig3 = px.bar(top_songs, x='track_name', y='popularity', title="Top 5 Songs by Popularity")
        fig3.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-30)
        st.plotly_chart(fig3, use_container_width=True)
        with st.expander("Show more songs"):
            fig_full = px.bar(df.sort_values('popularity', ascending=False), x='track_name', y='popularity', title="All Songs by Popularity")
            fig_full.update_layout(hovermode="x unified", height=520, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-30)
            st.plotly_chart(fig_full, use_container_width=True)

with tabs[2]:
    with card("Top Albums"):
        if 'popularity' in df.columns:
            top_albums = df.groupby('album_name', as_index=False)['popularity'].mean().sort_values('popularity', ascending=False).head(5)
            fig4 = px.bar(top_albums, x='album_name', y='popularity', title="Top 5 Albums (by mean popularity)")
        else:
            counts = df['album_name'].value_counts().head(5)
            fig4 = px.bar(counts, x=counts.index, y=counts.values, title="Top 5 Albums (count)")
        fig4.update_layout(hovermode="x unified", height=480, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-25)
        st.plotly_chart(fig4, use_container_width=True)
        with st.expander("Show all albums"):
            if 'popularity' in df.columns:
                all_albums = df.groupby('album_name', as_index=False)['popularity'].mean().sort_values('popularity', ascending=False)
                fig_full = px.bar(all_albums, x='album_name', y='popularity', title="All Albums by Mean Popularity")
            else:
                counts_all = df['album_name'].value_counts()
                fig_full = px.bar(counts_all, x=counts_all.index, y=counts_all.values, title="All Albums (count)")
            fig_full.update_layout(hovermode="x unified", height=520, margin=dict(l=10, r=10, t=50, b=0), xaxis_tickangle=-25)
            st.plotly_chart(fig_full, use_container_width=True)

st.markdown("---")
footer("Navigate via the sidebar to explore Preferences, Recommendations, Playlists, and the Dashboard.")
