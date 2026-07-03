import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Load environment variables (like GROQ_API_KEY)
load_dotenv()

VECTOR_DB_DIR = "./chroma_db"

def get_retriever():
    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    
    vectorstore = Chroma(
        persist_directory=VECTOR_DB_DIR, 
        embedding_function=embeddings
    )
    
    # Retrieve using MMR for diversity to avoid repetitive web boilerplate
    # We increase k to 10 to maximize factual recall while staying within Groq's 12K TPM limit.
    return vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 10, "fetch_k": 40}
    )

def get_rag_chain():
    retriever = get_retriever()
    
    # Initialize Groq LLM using the specified versatile model with retry logic for rate limits
    llm = ChatGroq(
        temperature=0, 
        model_name="llama-3.3-70b-versatile",
        max_tokens=256,
        max_retries=3
    )
    
    system_prompt = """You are a strictly factual Mutual Fund FAQ assistant.
Your ONLY goal is to answer the user's question based EXCLUSIVELY on the provided context.
You MUST follow these strict constraints:
1. Provide a maximum of 3 sentences.
2. You must NOT provide any investment advice, recommendations, or opinions. If the user asks for advice (e.g., "Should I invest?", "Which is better?"), politely refuse, state you can only provide facts, and provide a link to AMFI or SEBI.
3. If the answer is not contained in the context, say: "I do not have that information based on the official sources."

Context:
{context}

You MUST also provide EXACTLY one source link from the context above that justifies your answer.
Finally, your response MUST end with this exact footer on a new line:
"Last updated from sources: {date}"
"""
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{question}")
    ])
    
    def format_docs(docs):
        # Format the retrieved documents into a single string with their source links
        formatted = []
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown source')
            formatted.append(f"Content: {doc.page_content}\nSource: {source}")
        return "\n\n".join(formatted)

    rag_chain = (
        {
            "context": retriever | format_docs, 
            "question": RunnablePassthrough(), 
            "date": lambda _: datetime.now().strftime("%Y-%m-%d")
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

def answer_query(query: str) -> str:
    try:
        chain = get_rag_chain()
        response = chain.invoke(query)
        return response
    except Exception as e:
        error_msg = str(e).lower()
        if "rate_limit" in error_msg or "429" in error_msg or "rate limit" in error_msg:
            return "⚠️ Our servers are currently experiencing high traffic. Please wait a moment and try again."
        return "⚠️ I'm sorry, I encountered an unexpected server error while generating the answer. Please try again later."
