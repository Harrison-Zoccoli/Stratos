import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load the embeddings
with open('embeddings/exampleStarbucks_embeddings.json', 'r') as f:
    data = json.load(f)

chunks = data['chunks']

# Test 1: Check if embeddings are different (not all zeros)
print("=== EMBEDDING VERIFICATION TEST ===")
print(f"Total chunks: {len(chunks)}")
print(f"Embedding dimension: {len(chunks[0]['embedding'])}")

# Test 2: Check if embeddings are unique
embeddings = [chunk['embedding'] for chunk in chunks]
embeddings_array = np.array(embeddings)

print(f"\nEmbedding shape: {embeddings_array.shape}")
print(f"All embeddings unique: {len(set(map(tuple, embeddings_array))) == len(embeddings)}")

# Test 3: Check similarity between chunks
similarities = cosine_similarity(embeddings_array)
print(f"\nSimilarity matrix shape: {similarities.shape}")

# Test 4: Find most similar chunks
for i in range(min(3, len(chunks))):
    # Get similarities for chunk i (excluding self-similarity)
    chunk_similarities = similarities[i]
    chunk_similarities[i] = -1  # Exclude self
    most_similar_idx = np.argmax(chunk_similarities)
    
    print(f"\nChunk {i+1} most similar to Chunk {most_similar_idx+1}")
    print(f"Similarity score: {chunk_similarities[most_similar_idx]:.4f}")
    print(f"Chunk {i+1} text preview: {chunks[i]['text'][:100]}...")
    print(f"Chunk {most_similar_idx+1} text preview: {chunks[most_similar_idx]['text'][:100]}...")

# Test 5: Check if embeddings are reasonable
print(f"\n=== EMBEDDING STATISTICS ===")
print(f"Mean embedding value: {embeddings_array.mean():.6f}")
print(f"Std embedding value: {embeddings_array.std():.6f}")
print(f"Min embedding value: {embeddings_array.min():.6f}")
print(f"Max embedding value: {embeddings_array.max():.6f}")