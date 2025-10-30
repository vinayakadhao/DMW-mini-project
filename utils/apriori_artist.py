from mlxtend.frequent_patterns import apriori, association_rules
import pandas as pd

def build_artist_rules(df, min_support=0.005, metric='lift', min_threshold=1.0):
    artist_lists = df['artists_split']
    unique_artists = sorted(set(a for sub in artist_lists for a in sub))
    encoded_df = pd.DataFrame(0, index=range(len(artist_lists)), columns=unique_artists)
    
    for i, artists in enumerate(artist_lists):
        for a in artists:
            encoded_df.loc[i, a] = 1
    
    freq_items = apriori(encoded_df, min_support=min_support, use_colnames=True)
    rules = association_rules(freq_items, metric=metric, min_threshold=min_threshold)
    return rules
