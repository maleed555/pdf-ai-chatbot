
import streamlit as st
import os
import tempfile
import shutil
from langchain_google_vertexai import ChatVertexAI, VertexAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- GOOGLE CLOUD CONFIG ---
PROJECT_ID = "gen-lang-client-0302219491"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

# --- STREAMLIT CONFIG ---
st.set_page_config(page_title="AI Doc Chat", page_icon="🤖", layout="wide")

st.title("🤖 AI Document Chatbot")
st.markdown("---")

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None
if "vectorstore_dir" not in st.session_state:
    st.session_state.vectorstore_dir = None
if "debug" not in st.session_state:
    st.session_state.debug = False

# --- HELPER FUNCTION: SAFE DELETE ---
def safe_delete(folder_path):
    if folder_path and os.path.exists(folder_path):
        for _ in range(5):
            try:
                shutil.rmtree(folder_path)
                break
            except PermissionError:
                import time
                time.sleep(0.2)

# --- SIDEBAR ---
with st.sidebar:
    st.header("Upload Document")
    st.checkbox("Show retriever context (debug)", key="debug")
    uploaded_file = st.file_uploader("PDF / DOCX / TXT", type=["pdf", "docx", "txt"])

    if uploaded_file:
        with st.spinner("Processing document..."):
            # Delete old vectorstore safely
            safe_delete(st.session_state.vectorstore_dir)

            # Temp folder per upload
            persist_dir = tempfile.mkdtemp(prefix="vectorstore_")
            st.session_state.vectorstore_dir = persist_dir

            # Temp file
            suffix = f".{uploaded_file.name.split('.')[-1]}"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            # --- LOAD DOCUMENT ---
            if suffix == ".pdf":
                loader = PyPDFLoader(tmp_path)
            elif suffix == ".docx":
                loader = Docx2txtLoader(tmp_path)
            else:
                loader = TextLoader(tmp_path)

            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
            splits = text_splitter.split_documents(docs)

            # --- VECTORSTORE ---
            embeddings = VertexAIEmbeddings(model_name="text-embedding-004")
            vectorstore = Chroma.from_documents(
                documents=splits,
                embedding=embeddings,
                persist_directory=persist_dir
            )
            vectorstore.persist()
            retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})

            # --- LLM CHAIN WITH LONGER OUTPUT AND BETTER CONTEXT ---
            llm = ChatVertexAI(
                model_name="publishers/google/models/gemini-2.5-flash",
                temperature=0.7,                  # small randomness for natural answers
                max_output_tokens=1024            # allow long answers
            )

            template = """You are a helpful assistant. Answer ONLY based on the context.
If you don't find it in the context, say 'Mujhe document mein iska jawab nahi mila'.

Context: {context}
Question: {question}
"""
            prompt = ChatPromptTemplate.from_template(template)

            st.session_state.qa_chain = (
                {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
            )

            st.success("File ready! Ask your questions now.")
            os.remove(tmp_path)

# --- MAIN CHAT INTERFACE ---
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role, avatar="👤" if role == "user" else "🤖"):
        st.markdown(content, unsafe_allow_html=True)

# --- USER INPUT ---
if prompt_text := st.chat_input("Ask your question..."):
    if not st.session_state.qa_chain:
        st.error("Please upload a document first!")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt_text})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt_text)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                # Debug context
                if st.session_state.debug:
                    context_docs = st.session_state.qa_chain["context"].get_relevant_documents(prompt_text)
                    st.subheader("Retriever Context")
                    for doc in context_docs:
                        st.code(doc.page_content[:300] + "...", language="text")

                # Invoke LLM and replace newlines for multi-line display
                response = st.session_state.qa_chain.invoke(prompt_text)
                response_display = response.replace('\n', '<br>')
                st.markdown(response_display, unsafe_allow_html=True)
                st.session_state.messages.append({"role": "assistant", "content": response_display})

# --- RESET CHAT BUTTON ---
if st.button("Reset Chat"):
    safe_delete(st.session_state.vectorstore_dir)
    st.session_state.vectorstore_dir = None
    st.session_state.qa_chain = None
    st.session_state.messages = []
    st.success("Chat reset successfully!")