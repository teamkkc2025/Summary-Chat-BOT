import streamlit as st
from langchain_ollama import ChatOllama
import PyPDF2
import pandas as pd

# Set dark theme and wide layout
st.set_page_config(
    page_title="Chat App",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Apply dark theme through custom CSS
st.markdown(
    """
    <style>
        body {
            background-color: #0e1117;
            color: #f0f0f0;
        }
        .stButton button {
            background-color: #3b3b3b;
            color: white;
            border-radius: 5px;
        }
        .stTextInput > div > div > input {
            background-color: #222;
            color: #FAFAFA;
            border: 1px solid #555555;
        }
        .block-container {
            padding: 2rem 3rem;
        }
        .css-1d391kg {
            max-width: 95%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧠 Document & Code Assistant !!!")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
    return extracted_text

# Function to read Excel file
def extract_data_from_excel(excel_file):
    df = pd.read_excel(excel_file, sheet_name=None)  # Read all sheets
    return df

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.pdf_text = ""
    st.session_state.excel_data = None
    st.session_state.file_type = ""

# File upload section
uploaded_file = st.file_uploader("Upload a PDF or Excel file", type=["pdf", "xlsx"])

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1]
    if file_extension == "pdf":
        with st.spinner("Processing PDF..."):
            st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)
            st.session_state.file_type = "pdf"
            st.success("PDF processed successfully!")
    elif file_extension == "xlsx":
        with st.spinner("Processing Excel..."):
            st.session_state.excel_data = extract_data_from_excel(uploaded_file)
            st.session_state.file_type = "excel"
            st.success("Excel processed successfully!")
else:
    st.session_state.file_type = ""

# Function to generate response using appropriate model
def generate_response(input_text, query_type):
    if query_type == "pdf":
        model = ChatOllama(model="llama3.2:1b", base_url="http://localhost:11434/")
    elif query_type == "code":
        model = ChatOllama(model="codellama", base_url="http://localhost:11434/")
    elif query_type == "general":
        model = ChatOllama(model="llama3.2:1b", base_url="http://localhost:11434/")
    else:
        model = ChatOllama(model="llama3.2:1b", base_url="http://localhost:11434/")
    
    response = model.invoke(input_text)
    return response.content

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Display Excel data if uploaded
if st.session_state.file_type == "excel" and st.session_state.excel_data:
    selected_sheet = st.selectbox("Select sheet", list(st.session_state.excel_data.keys()))
    st.dataframe(st.session_state.excel_data[selected_sheet])

# Always show chat input
query = st.chat_input("Ask a question about the uploaded file, code errors, or general queries...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.spinner("Generating response..."):
        if any(keyword in query.lower() for keyword in ["error", "code", "debug", "program"]):
            query_type = "code"
            combined_input = query
        elif st.session_state.file_type == "pdf":
            query_type = "pdf"
            combined_input = f"{st.session_state.pdf_text}\n\n{query}"
        elif st.session_state.file_type == "excel":
            query_type = "pdf"
            combined_input = f"Data: {st.session_state.excel_data}\n\n{query}"
        elif "difference" in query.lower() or "compare" in query.lower() or "what is" in query.lower():
            query_type = "general"
            combined_input = query
        else:
            query_type = "general"
            combined_input = query

        response = generate_response(combined_input, query_type)

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
