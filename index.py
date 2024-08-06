from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import UnstructuredExcelLoader


load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")

def load_pdfs(folder_path):
    loader=PyPDFDirectoryLoader(folder_path)
    documents = loader.load()
    return  documents

def load_excel(file_path):
    loader = UnstructuredExcelLoader(file_path, mode="elements")
    docs = loader.load()


def chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_documents(text)
    return chunks



def index(text_chunks):
    embeddings = OpenAIEmbeddings()
    vector = FAISS.from_documents(text_chunks, embeddings)
    vector.save_local("faiss_index")



def add_(text_chunks):
    embeddings = OpenAIEmbeddings()
    vector = FAISS.load_local("faiss_index", OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    vector.add_documents(text_chunks)
    vector.save_local("faiss_index")


def new_index(folder_path):
    docs = load_pdfs(folder_path) 
    doc_chunks = chunks(docs)
    index(doc_chunks)

def add_index(folder_path):
    docs = load_pdfs(folder_path) 
    doc_chunks = chunks(docs)
    add_(doc_chunks)


def add_excel(file_path):
    docs = load_excel(file_path) 
    doc_chunks = chunks(docs)
    add_(doc_chunks)

new_index("./data")