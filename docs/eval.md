# Evaluation Criteria (eval.md)

This document contains the evaluation rubrics and checklists for each phase of the implementation plan defined in `ImplementationPlan.md`. Use this as a QA checklist to ensure all project requirements are met.

## Phase 1: Data Ingestion Pipeline
- [ ] **Web Scraping**: Successfully fetches HTML from all 5 specified HDFC Mutual Fund URLs.
- [ ] **Structured Data Extraction**: Correctly parses `<script type="application/ld+json">` tags to extract hidden facts (like Expense Ratio, AUM) and Q&A pairs.
- [ ] **Text Chunking**: Utilizes `RecursiveCharacterTextSplitter` with 1500 character chunks and 300 overlap.
- [ ] **Metadata Tagging**: Injects the Fund Name into the raw text of each chunk for semantic context retention.
- [ ] **Vector Database**: Successfully embeds text using `BAAI/bge-small-en-v1.5` and persists the data to a local ChromaDB folder.

## Phase 2: Retrieval & Generation Pipeline (RAG)
- [ ] **Retriever Mechanism**: Uses Maximal Marginal Relevance (MMR) with `k=10` and `fetch_k=40` to maximize contextual diversity.
- [ ] **Prompt Constraints**: Enforces a strict 3-sentence maximum limit for all outputs.
- [ ] **Citation Enforcement**: Returns exactly 1 source link with the footer `"Last updated from sources: <date>"`.
- [ ] **Advisory Refusal**: Gracefully refuses subjective/advisory queries and directs users to AMFI/SEBI.
- [ ] **LLM Integration**: Successfully communicates with the Groq API (`llama-3.3-70b-versatile`) and handles API rate limit exceptions cleanly.

## Phase 3: User Interface Development (Streamlit)
- [ ] **UI Initialization**: Application runs flawlessly via `streamlit run src/app.py`.
- [ ] **Aesthetics & Styling**: Implements custom high-contrast CSS, glassmorphism chat bubbles, and an animated galaxy/space background.
- [ ] **Compliance Disclaimer**: Prominently displays `"Facts-only. No investment advice."` on the sidebar.
- [ ] **Interactivity**: Chat interface correctly handles user input, displays a loading spinner during inference, and accurately renders the RAG markdown response.

## Phase 4: Testing & Validation
- [ ] **Factual Edge-Cases**: Successfully extracts hidden numbers (e.g. 0.77% expense ratio for the Small Cap Fund).
- [ ] **Missing Information Handling**: Politely declines to hallucinate if data (e.g., Fund Manager CEO) is missing from the scraped context.
- [ ] **Performance Queries**: Correctly retrieves and formats historical return data explicitly found in the text.
- [ ] **Advisory Validation**: Repeatedly passes adversarial tests designed to trick the bot into giving investment advice.

## Phase 5: Daily Data Scheduler (GitHub Actions)
- [ ] **Workflow Setup**: `.github/workflows/data_ingestion.yml` is correctly formatted and syntax-valid.
- [ ] **Cron Trigger**: Configured to run automatically at `0 5 * * *` (10:30 AM IST).
- [ ] **Environment Execution**: The GitHub runner correctly sets up Python 3.10, installs dependencies, and executes `src/data_ingestion.py`.
- [ ] **Repository Sync**: Utilizes `git-auto-commit-action` to successfully push the newly generated `chroma_db` folder back to the main branch.
