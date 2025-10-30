# pages/5_About.py
import streamlit as st
from PIL import Image
from utils.ui import inject_global_css, render_page_header, card, footer

st.set_page_config(page_title="About Project", layout="centered")
inject_global_css()

# ---- HEADER ----
render_page_header("About the Project", "Overview, team, and how it works.", "🎓")

# ---- PROJECT INFO ----
st.header("🎵 Music Listening Habit Analysis & Personalized Song Recommendation System")

with card():
    st.markdown("""
    This project explores **music listening patterns** and builds a **personalized recommendation system** using data analytics and machine learning.
    It combines **data visualization** and **intelligent recommender systems** to enhance user experience.

    Through this platform, users can:
    - Analyze their music listening habits  
    - Discover new artists and songs based on preferences  
    - Automatically generate curated playlists using **K-Means clustering** (adjust clusters and playlist size)  
    - Receive intelligent recommendations using **KNN** similarity (per-centroid "Songs like <track>")  
    """)

# ---- TEAM DETAILS ----
st.markdown("---")
st.subheader("👨‍💻 Project Developers")

col1, col2 = st.columns(2)
with col1:
    with card("Vinayak Adhao"):
        st.markdown("📧 *vinayak.adhao23@pccoepune.org*")
with col2:
    with card("Soham Kolte"):
        st.markdown("📧 *soham.kolte23@pccoepune.org*")

st.markdown("---")

# ---- TECHNOLOGIES USED ----
st.header("🧰 Technologies & Tools Used")
with card():
    st.markdown("""
    | Category | Tools / Libraries |
    |-----------|------------------|
    | **Frontend / UI** | Streamlit |
    | **Data Analysis** | Pandas, NumPy |
    | **Visualization** | Plotly, Matplotlib |
    | **Recommendation Engine** | KNN (Scikit-learn)|
    | **Clustering** | K-Means (Scikit-learn) |
    | **Development Environment** | Python, Spyder / VS Code |
    """)

st.markdown("---")

# ---- PROJECT STRUCTURE ----
st.header("📂 Project Structure")
with card():
    st.code("""
DMW mini project/
|
├── Home.py
├── dataset.csv
├── utils/
│   ├── data_loader.py
│   ├── apriori_artist.py
│   ├── recommender.py
│   └── playlist_cluster.py
└── pages/
    ├── 1_Preferences.py
    ├── 2_Recommendations.py
    ├── 3_Playlist_Recommendations.py
    ├── 4_Dashboard.py
    └── 5_About.py
""", language="bash")

st.markdown("---")

# ---- HOW IT WORKS ----
st.header("⚙️ How the System Works")
with card():
    st.markdown("""
    1. **User selects favorite songs or artists** (via Preferences page).  
    2. **System generates recommendations** using:
       - *KNN Algorithm* → for similar track recommendations  
    3. **K-Means Clustering** forms **playlists** with songs of similar audio profiles.  
    4. **Dashboard** visualizes insights such as top artists, genres, and popularity trends.  
    """)

st.markdown("---")

# ---- CREDITS ----
st.success("""
Made by **Vinayak Adhao** and **Soham Kolte**

This project was developed as part of the **Data Mining & Warehousing Mini Project**.
""")
footer("Thanks for exploring our project! 🎶")

