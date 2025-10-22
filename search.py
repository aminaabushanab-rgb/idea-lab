from src.index.faiss_store import FAISSStore

if __name__ == "__main__":
    q = input("🔎 Enter your query: ") or "What is LangChain used for?"
    store = FAISSStore()
    store.load()
    results = store.search(q, k=5)

    print(f"\nTop results for: {q}\n")
    for i, r in enumerate(results, 1):
        snippet = r["text"][:200].replace("\n", " ")
        source = r.get("meta", {}).get("source", "unknown")
        print(f"{i}. ({source}) {snippet}...\n")

