import streamlit as st
import pandas as pd
from utils.data_loader import load_data, preprocess_artists
from pathlib import Path
from utils.ui import inject_global_css, render_page_header, card, footer

st.set_page_config(page_title="Preferences - Music Recommender", layout="wide")
inject_global_css()
render_page_header(
    title="Preferences — Build your curated list",
    subtitle="Filter songs by Artist, Album, or Genre and craft your base.",
    emoji="🛠️",
)

import os
from utils.data_loader import load_data

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset.csv")


@st.cache_data(show_spinner=False)
def load_and_prep(path):
    df = load_data(path)
    df = preprocess_artists(df)
    return df

df = load_and_prep(DATA_PATH)

if "curated_list" not in st.session_state:
    st.session_state.curated_list = []  

def add_to_curated(selected_indices):
    """Add selected DataFrame indices to curated list in session_state"""
    added = 0
    for i in selected_indices:
        row = df.iloc[i]
        item = {
            "track_id": row.get("track_id", f"{row['track_name']}|{row['artists']}"),
            "track_name": row["track_name"],
            "artists": row["artists"],
            "album_name": row.get("album_name", ""),
            "track_genre": row.get("track_genre", "")
        }
        if all(ci["track_id"] != item["track_id"] for ci in st.session_state.curated_list):
            st.session_state.curated_list.append(item)
            added += 1
    return added

def remove_from_curated(track_id):
    st.session_state.curated_list = [c for c in st.session_state.curated_list if c["track_id"] != track_id]

left_col, right_col = st.columns([2,1])

with left_col:
    with card("Create your curated list"):
        st.markdown("Use filters to narrow songs and add the ones you like to your curated list (used later by recommendation / playlist pages).")

    filter_type = st.selectbox("Choose filter type", ["Artist", "Album", "Genre"]) 
    if filter_type == "Artist":
        all_artists = [a for sub in df["artists_split"] for a in sub]
        options = sorted(set(all_artists))
    elif filter_type == "Album":
        options = sorted(df["album_name"].dropna().unique().tolist())
    else:
        options = sorted(df["track_genre"].dropna().unique().tolist())

    selected_filter_values = st.multiselect(f"Select {filter_type}(s)", options, default=None)


    if selected_filter_values:
        if filter_type == "Artist":
           
            mask = df["artists_split"].apply(lambda lst: any(a in selected_filter_values for a in lst))
            filtered = df[mask].reset_index(drop=True)
        elif filter_type == "Album":
            filtered = df[df["album_name"].isin(selected_filter_values)].reset_index(drop=True)
        else:
            filtered = df[df["track_genre"].isin(selected_filter_values)].reset_index(drop=True)
    else:
        filtered = df.copy().reset_index(drop=True)

    st.markdown(f"**Matching songs: {len(filtered):,}** (showing top 200 rows)")
    display_df = filtered[["track_name", "artists", "album_name", "track_genre", "popularity"]].head(200).copy()
    display_df = display_df.reset_index() 
    display_df.rename(columns={"index": "df_index"}, inplace=True)

   
    st.write("Select rows to add to curated list:")
    selected_rows = st.multiselect(
        "Choose songs from this list (multi-select)",
        options=display_df.index.tolist(),
        format_func=lambda x: f"{display_df.loc[x,'track_name']} — {display_df.loc[x,'artists']}"
    )

    if st.button("Add selected songs to curated list"):
        idxs = []
        for sel in selected_rows:
            filtered_row = display_df.loc[sel]
            cond = (
                (df["track_name"] == filtered_row["track_name"]) &
                (df["artists"] == filtered_row["artists"]) &
                (df["album_name"] == filtered_row["album_name"])
            )
            original_indices = df[cond].index.tolist()
            if original_indices:
                idxs.append(original_indices[0])
        added = add_to_curated(idxs)
        st.success(f"Added {added} song(s) to your curated list.")

    if st.button("Clear filters (show all)"):
        st.experimental_rerun()


with right_col:
    with card("Your Curated List"):
        if st.session_state.curated_list:
            curated_df = pd.DataFrame(st.session_state.curated_list)
            st.dataframe(curated_df[["track_name", "artists", "album_name", "track_genre"]])
            to_remove = st.selectbox("Select a track to remove (by name)", ["--"] + [f"{c['track_name']} — {c['artists']}" for c in st.session_state.curated_list])
            if to_remove != "--":
                if st.button("Remove selected track"):
                    track_name = to_remove.split(" — ")[0]
                    found = None
                    for c in st.session_state.curated_list:
                        if c["track_name"] == track_name:
                            found = c["track_id"]
                            break
                    if found:
                        remove_from_curated(found)
                        st.success("Removed.")
                        st.experimental_rerun()
            if st.button("Clear curated list"):
                st.session_state.curated_list = []
                st.experimental_rerun()
        else:
            st.info("Your curated list is empty. Add songs from the left panel.")

    st.markdown("---")
    st.markdown("### Small utility: Find songs by typing")
    q = st.text_input("Quick search (type song title or artist fragment):", "")
    if q:
        qmask = df["track_name"].str.contains(q, case=False, na=False) | df["artists"].str.contains(q, case=False, na=False)
        quick = df[qmask][["track_name", "artists", "album_name", "track_genre", "popularity"]].head(50)
        st.table(quick)


st.markdown("---")
with card("Hints"):
    st.markdown("""
    - Use the filters to narrow your choices. For artists, names are split by `;` in the dataset and listed individually.
    - After you add songs to the curated list, go to **Recommendations** or **Playlist Recommendation** pages to generate suggestions based on your selection.
    - If the dataset is large, filtering may take a few seconds.
    """)
footer("Tip: Use the quick search to jump to specific tracks or artists.")
