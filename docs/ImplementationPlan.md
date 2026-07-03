# Implementation Plan: Mutual Fund FAQ Assistant

## 1. Environment Setup & Dependencies
- Initialize a Python virtual environment.
- Install necessary libraries:
  - `langchain` / `llama-index` for orchestration.
  - `chromadb` / `faiss-cpu` for the vector database.
  - `groq` for LLM inference (using Groq API).
  - `sentence-transformers` / `huggingface-hub` for the BGE embedding model.
  - `streamlit` for the frontend UI.
  - `beautifulsoup4`, `requests` for web scraping/document loading.

## 2. Data Ingestion Pipeline (Phase 1)
- **Scraping**: Write a script to fetch the content from the 5 specified HDFC Mutual Fund URLs on Groww.
- **Preprocessing**: Clean the HTML to extract only relevant text (e.g., expense ratios, exit loads, fund objectives).
- **Chunking**: Use LangChain's `RecursiveCharacterTextSplitter` with a larger chunk size (1500 characters) and overlap (300 characters), prioritizing newline separators `["\n\n", "\n", " ", ""]`. This strategy ensures that densely packed financial facts (like NAV, Expense Ratio, and Exit Load) extracted from the web pages remain intact and are not broken across chunks. Source URL metadata is attached to each chunk.
- **Embedding & Storage**: 
  - Load the **BGE model** (`BAAI/bge-small-en-v1.5`) via HuggingFace embeddings. Because we are using larger chunks (1500 characters, ~300-400 tokens), this small but highly efficient model is ideal as its context window natively supports up to 512 tokens while keeping the vector database lightweight.
  - **Normalization**: Set `normalize_embeddings=True` to ensure optimal accuracy when calculating cosine similarity for dense financial facts.
  - Embed the chunks and store them in the local vector database (e.g., ChromaDB).

## 3. Retrieval & Generation Pipeline (Phase 2)
- **Retrieval**: 
  - Set up a retriever to take a user query, embed it using the **BGE model**, and fetch the top-k most relevant chunks.
  - **Strategy**: Because the larger 1500-character chunks contain repetitive web-scraped boilerplate across the 5 URLs (e.g., site navigation, footers), standard similarity search might retrieve redundant noisy chunks. We will use **Maximal Marginal Relevance (MMR)** as the `search_type` with `k=5` (and `fetch_k=20`) to ensure the retrieved context is both highly relevant to the query and diverse. This prevents the LLM from receiving duplicate boilerplate and maximizes the chance of capturing the precise factual data.
- **Prompt Engineering**:
  - Design a strict system prompt to enforce the project constraints:
    - Answer using *only* the retrieved context.
    - Max 3 sentences.
    - Exactly 1 citation link (from chunk metadata).
    - Footer: `"Last updated from sources: <date>"`.
    - Polite refusal for advisory/subjective queries.
- **LLM Integration**:
  - Integrate **Groq** via its API using the `llama-3.3-70b-versatile` model.
  - **Rate Limit Handling**: Account for Groq's limits (30 RPM, 1K RPD, 12K TPM, 100K TPD). We will configure the `ChatGroq` client with built-in retries (`max_retries`) and gracefully catch rate limit exceptions to notify the user, ensuring the app remains stable when hitting the 12K TPM ceiling.

## 4. User Interface Development (Phase 3)
- Build a lightweight Streamlit app.
  - **Architecture Note:** The backend RAG logic and the Streamlit frontend UI are currently tightly coupled in a monolithic architecture. `app.py` directly executes the pipeline from `rag_pipeline.py`. If future scaling or alternate frontends (e.g., React, Mobile) are required, the backend will need to be decoupled into a standalone REST API (e.g., using FastAPI).
- Include a welcome message and a visible disclaimer: `"Facts-only. No investment advice."`
- Add 3 pre-populated example questions.
- Implement the chat interface to receive user queries, run the RAG pipeline, and display the response.

## 5. Testing & Validation (Phase 4)
- **Factual Queries**: Test questions like "What is the expense ratio of the HDFC Small Cap Fund?" to ensure accurate retrieval and 3-sentence limit.
- **Advisory Queries**: Test queries like "Should I invest in this?" to ensure the refusal handling works perfectly.
- **Citation Check**: Verify that every successful response includes exactly one source link and the correct footer.

## 6. Daily Data Scheduler (Phase 5)
- **Objective**: Ensure the vector database is refreshed daily with the latest Mutual Fund data (e.g., NAV updates).
- **Implementation**: Create a GitHub Actions workflow (`.github/workflows/data_ingestion.yml`).
- **Workflow**: 
  - The workflow will be triggered on a daily cron schedule (`0 5 * * *` which is 10:30 AM IST).
  - It spins up a runner, installs dependencies, and executes `data_ingestion.py` to scrape the URLs, extract structured JSON-LD data, and rebuild the ChromaDB vector store.
  - The action will then automatically commit and push the updated `chroma_db` folder back to the repository.
  - Any deployed frontend syncing with the repository will automatically inherit the freshly built database.
