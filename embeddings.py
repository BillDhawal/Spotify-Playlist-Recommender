import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np

# Load data from CSV file
df = pd.read_csv('all_tracks.csv')
df.head()

# Fill NaN values in columns with empty strings to avoid concatenation issues
df = df.fillna('')

# track_name,artist_name,genre,description,playlist_name,playlist_id,owner
# Concatenate metadata to create a single text field for embedding
df['combined_text'] = df['playlist_name']+ ' ' + df['track_name'] + ' ' + df['artist_name'] + ' ' + df['genre'] + ' ' + df['description'] + ' ' + df['owner']

# Load pretrained model and tokenizer
model_name = 'sentence-transformers/all-MiniLM-L6-v2'  # Or other model suited for embeddings
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
    # Tokenize and create embeddings
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        embeddings = model(**inputs).last_hidden_state.mean(dim=1)
    return embeddings.squeeze().cpu().numpy()

# Generate embeddings for each combined text in DataFrame
df['embedding'] = df['combined_text'].apply(get_embedding)

# Convert embeddings to numpy array
embeddings = np.array(df['embedding'].tolist()).astype('float32')

# Initialize FAISS index
index = faiss.IndexFlatIP(embeddings.shape[1])  # Inner product for cosine similarity
faiss.normalize_L2(embeddings)  # Normalize embeddings for cosine similarity
index.add(embeddings)  # Add embeddings to the index

# Save FAISS index (optional)
faiss.write_index(index, 'playlist_embeddings.index')


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