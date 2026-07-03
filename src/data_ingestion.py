import os
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
import shutil
import warnings

warnings.filterwarnings("ignore")

# The 5 HDFC scheme URLs
URLS = [
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth",
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
]

VECTOR_DB_DIR = "./chroma_db"
RAW_DATA_DIR = "./data"

def scrape_url(url):
    print(f"Scraping {url}...")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Extract JSON-LD FAQs to capture hidden data like Expense Ratios
        structured_text = ""
        import json
        ld_jsons = soup.find_all("script", type="application/ld+json")
        for script in ld_jsons:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and data.get("@type") == "FAQPage":
                    for item in data.get("mainEntity", []):
                        if item.get("@type") == "Question":
                            q = item.get("name", "")
                            a_html = item.get("acceptedAnswer", {}).get("text", "")
                            a = BeautifulSoup(a_html, "html.parser").get_text(separator=' ', strip=True)
                            structured_text += f"\nQ: {q}\nA: {a}\n"
            except Exception:
                pass
        
        # 2. Extract standard visible text
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        return structured_text + "\n\n" + text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def main():
    if os.path.exists(VECTOR_DB_DIR):
        print(f"Removing existing {VECTOR_DB_DIR}...")
        try:
            shutil.rmtree(VECTOR_DB_DIR)
        except Exception as e:
            print(f"Failed to remove DB (might be locked by Streamlit). Error: {e}")
            return
            
    all_chunks = []
    
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""],
        length_function=len
    )
    
    for i, url in enumerate(URLS):
        content = scrape_url(url)
        if content:
            fund_title = content.split(' - NAV')[0] if ' - NAV' in content else url.split('/')[-1].replace('-', ' ').title()
            
            file_chunks = text_splitter.create_documents(
                [content], 
                metadatas=[{"source": url}]
            )
            
            for chunk in file_chunks:
                chunk.page_content = f"Fund Name: {fund_title}\n\n{chunk.page_content}"
                
            all_chunks.extend(file_chunks)
            
            scheme_name = url.split('/')[-1]
            file_path = os.path.join(RAW_DATA_DIR, f"{scheme_name}.txt")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Saved raw data to {file_path}")
            
    if not all_chunks:
        print("No documents were scraped. Exiting.")
        return

    print(f"Created {len(all_chunks)} chunks with injected fund metadata.")

    print("Loading BGE Embedding model...")
    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    print(f"Storing into ChromaDB at {VECTOR_DB_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=all_chunks, 
        embedding=embeddings, 
        persist_directory=VECTOR_DB_DIR
    )
    print("Data ingestion and vector storage complete!")

if __name__ == "__main__":
    main()
