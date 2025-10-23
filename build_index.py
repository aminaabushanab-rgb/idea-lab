import yaml
from src.ingest.web_loader import fetch_clean_text
from src.rag.chunk import chunk_text
from src.index.faiss_store import FAISSStore
from src.ingest.scrape_links import scrape_article_links

with open("config.yaml", "r") as f:
    CONFIG = yaml.safe_load(f)

if __name__ == "__main__":
    
    print("Gathering all URLs...")
    all_article_urls = set()

    direct_urls = CONFIG.get("direct_urls", [])
    all_article_urls.update(direct_urls)
    print(f"Loaded {len(direct_urls)} direct URLs from config.")

    for source in CONFIG.get("sources_to_scrape", []):
        print(f"Scraping {source['url']} for more links...")
        links = scrape_article_links(source['url'], source['prefix'])
        all_article_urls.update(links)
        print(f"  > Found {len(links)} new links.")
            
    print(f"Processing {len(all_article_urls)} total unique articles...")
    
    all_chunks = []
    all_metadata = [] 

    for url in sorted(list(all_article_urls)):
        try:
            txt = fetch_clean_text(url)
            chunks = chunk_text(txt, size=1000, overlap=150)
            
            if not chunks:
                print(f"🟡 {url}: 0 chunks found.")
                continue

            for i, chunk in enumerate(chunks):
                all_metadata.append({
                    "source_url": url,
                    "chunk_number": i
                })
            
            all_chunks.extend(chunks)
            print(f"✅ {url}: {len(chunks)} chunks")
            
        except Exception as e:
            print(f"⚠️  Skipped {url}: {e}")

    print("\nBuilding and saving index...")
    if all_chunks:
        store = FAISSStore()
        store.build(texts=all_chunks, meta=all_metadata) 
        store.save()
        print(f"\n🎉 Built index with {len(all_chunks)} total chunks.")
    else:
        print("\nNo chunks found. Index not built.")
