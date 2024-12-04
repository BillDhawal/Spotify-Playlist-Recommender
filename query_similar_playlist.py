from embeddings import get_embedding
import faiss

def search_similar_playlists(query, k=5):
    # Create embedding for the query
    query_embedding = get_embedding(query).reshape(1, -1)
    faiss.normalize_L2(query_embedding)  # Normalize the query embedding

    # Search in the FAISS index
    _, indices = index.search(query_embedding, k)

    # Retrieve similar playlists based on indices
    results = df.iloc[indices[0]]
    return results[['track_name', 'artist_name', 'genre', 'description', 'playlist_name']]


# Example usage:
query = "relaxing chill beats on a beach"
similar_playlists = search_similar_playlists(query)
print(similar_playlists)