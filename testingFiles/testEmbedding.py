#cursor slop code for testing embedding to make sure env is working and to test the api call

import os
import time
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

print("🔄 Starting timing test...")
start_total = time.time()

# Initialize Azure OpenAI client
print("🔄 Initializing client...")
start_init = time.time()
try:
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )
    init_time = time.time() - start_init
    print(f"✅ Client initialized in {init_time:.2f} seconds")
except Exception as e:
    print(f"❌ Client initialization failed: {e}")
    exit(1)

def test_embedding():
    try:
        print("🔄 Making API call...")
        start_api = time.time()
        
        response = client.embeddings.create(
            input="This is a test sentence for embedding.",
            model=os.getenv("AZURE_OPENAI_MODEL_NAME")
        )
        
        api_time = time.time() - start_api
        print(f"✅ API call completed in {api_time:.2f} seconds")
        
        # Process response
        embedding = response.data[0].embedding
        print(f"✅ Success! Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_embedding()
    total_time = time.time() - start_total
    print(f"\n⏱️ Total execution time: {total_time:.2f} seconds")