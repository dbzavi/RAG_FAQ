import streamlit as st
from rag_pipeline import answer_query

def main():
    st.set_page_config(page_title="Mutual Fund FAQ Assistant", page_icon="📈", layout="centered")

    custom_css = """
    <style>
    @keyframes panBackground {
        0% { background-position: 0% 0%; }
        100% { background-position: 100% 100%; }
    }

    /* Galaxy Background */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1506318137071-a8e063b4bec0?q=80&w=2070&auto=format&fit=crop");
        background-size: cover;
        background-attachment: fixed;
        animation: panBackground 120s linear infinite alternate;
    }
    
    /* Main container glassmorphism for contrast */
    .block-container {
        background-color: rgba(10, 15, 30, 0.75);
        border-radius: 15px;
        padding: 2rem !important;
        margin-top: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* High contrast text */
    h1, h2, h3, h4, p, li, span, div {
        color: #f0f4f8 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    
    /* Distinct Chat Bubbles */
    div[data-testid="stChatMessage"] {
        background-color: rgba(30, 40, 60, 0.8);
        border-radius: 10px;
        border: 1px solid rgba(0, 240, 255, 0.3);
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(0,240,255,0.1);
    }
    
    /* Chat Input Styling */
    div[data-testid="stChatInput"] {
        background-color: rgba(10, 15, 30, 0.9) !important;
        border: 1px solid #00f0ff !important;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0,240,255,0.2);
    }
    
    /* Make the disclaimer pop */
    h3 {
        color: #ff4b4b !important;
        text-shadow: 0px 0px 10px rgba(255, 75, 75, 0.5) !important;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

    st.title("Mutual Fund FAQ Assistant")
    st.markdown("### **Facts-only. No investment advice.**")
    
    st.markdown("Welcome! I can answer factual questions about these HDFC Mutual Funds:")
    st.markdown("""
    - HDFC Gold ETF Fund of Fund Direct Plan Growth
    - HDFC Large Cap Fund Direct Growth
    - HDFC Small Cap Fund Direct Growth
    - HDFC Silver ETF FoF Direct Growth
    - HDFC Mid Cap Fund Direct Growth
    """)

    st.markdown("#### Example Questions")
    st.markdown("1. What is the expense ratio for the HDFC Small Cap Fund?")
    st.markdown("2. What is the exit load for the HDFC Mid Cap Fund?")
    st.markdown("3. What is the minimum SIP investment for the HDFC Gold ETF?")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a factual question about the supported mutual funds..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner("Retrieving facts..."):
                response = answer_query(prompt)
            message_placeholder.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()
