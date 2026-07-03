# Project Context: Mutual Fund FAQ Assistant (Facts-Only Q&A)

## 1. Overview
The project involves building a lightweight Retrieval-Augmented Generation (RAG) assistant specifically designed for answering factual mutual fund queries. The system is modeled with Groww as a reference context but focuses strictly on verified, public facts.

## 2. Core Objectives
- **Factual Answers:** Answer objective queries about mutual fund schemes.
- **Verified Corpus:** Ensure all responses are backed by a curated corpus of official documents.
- **Concise & Source-Backed:** Provide concise, source-backed responses without any subjective, advisory, or speculative content.

## 3. Scope & Corpus
- **AMC & Schemes:** HDFC Asset Management Company (AMC) with the following 5 selected schemes:
  - [HDFC Gold ETF Fund of Fund Direct Plan Growth](https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth)
  - [HDFC Large Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth)
  - [HDFC Small Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth)
  - [HDFC Silver ETF FoF Direct Growth](https://groww.in/mutual-funds/hdfc-silver-etf-fof-direct-growth)
  - [HDFC Mid Cap Fund Direct Growth](https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth)
- **Data Sources:** The corpus consists of the specific URLs provided for the 5 selected HDFC schemes. Information will be retrieved from these sources to answer factual queries.

## 4. Key Assistant Features & Constraints
- **Capabilities:** Answers queries regarding expense ratios, exit loads, minimum SIP amounts, ELSS lock-in periods, riskometers, benchmarks, and processes to download statements.
- **Output Limitations:**
  - Maximum of **3 sentences** per response.
  - Exactly **one citation link** per response.
  - Must include a footer: `"Last updated from sources: <date>"`
- **Refusal Handling:** Must politely refuse non-factual, speculative, or advisory queries (e.g., "Which fund is better?"). The refusal must reinforce the facts-only limitation and provide a relevant educational link (AMFI/SEBI).
- **UI Interface:** A minimal interface featuring a welcome message, 3 example questions, and a visible disclaimer: `"Facts-only. No investment advice."`

## 5. Security & Compliance
- **No PII Collection:** The system must not collect, store, or process PAN, Aadhaar, account numbers, OTPs, email addresses, or phone numbers.
- **No Financial Advice:** No investment advice, recommendations, performance comparisons, or return calculations are allowed. For performance-related queries, the assistant should simply provide a link to the official factsheet.

## 6. Success Criteria
- Highly accurate retrieval of factual mutual fund information.
- Strict adherence to facts-only responses and the ability to properly refuse advisory queries.
- Consistent inclusion of valid source citations and date footers.
- A clean, minimal, and user-friendly interface.
