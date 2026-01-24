from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()

llm= ChatGroq(model="llama-3.1-8b-instant",temperature=0)

embedder = HuggingFaceEmbeddings( model_name="sentence-transformers/all-MiniLM-L6-v2")