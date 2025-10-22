from src.ingest.web_loader import fetch_clean_text
from src.rag.chunk import chunk_text
from src.index.faiss_store import FAISSStore

def read_urls(path="data/urls.txt"):
    """Reads a simple text file of URLs, one per line."""
    with open(path) as f:
        return [ln.strip() for ln in f if ln.strip()]

if __name__ == "__main__":
    urls = read_urls()
    all_chunks = []

    for u in urls:
        try:
            txt = fetch_clean_text(u)
            chunks = chunk_text(txt, size=1000, overlap=150)
            all_chunks.extend(chunks)
            print(f"✅ {u}: {len(chunks)} chunks")
        except Exception as e:
            print(f"⚠️  Skipped {u}: {e}")

    store = FAISSStore()
    store.build(all_chunks)
    store.save()

    print(f"\n🎉 Built index with {len(all_chunks)} total chunks.")

