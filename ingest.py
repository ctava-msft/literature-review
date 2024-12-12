import re
import uuid
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

import logging
import os
import tiktoken
from docx import Document
import requests
import time
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
import fitz  # PyMuPDF

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Function to get pages from PDF
def extract_pages_from_pdf(pdf_path):    
    pdf_document = fitz.open(pdf_path)
    pages_text = []
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        text = page.get_text("text")
        pages_text.append(text)
    pdf_document.close()
    return pages_text


# Function to get pages from Docx
def extract_pages_from_docx(docx_path, max_tokens=7000):
    doc = Document(docx_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    words = text.split()
    pages = []
    current_page = []
    for word in words:
        if len(current_page) + len(word.split()) > max_tokens:
            pages.append(" ".join(current_page))
            current_page = []
        current_page.append(word)
    if current_page:
        pages.append(" ".join(current_page))
    return pages


# Main function
def add_file_embeddings(index_name, file_path):
    
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_KEY",
        "AZURE_AISEARCH_ENDPOINT",
        "AZURE_AISEARCH_KEY",
        "AZURE_AISEARCH_INDEX",
        "MODEL_EMBEDDINGS_DEPLOYMENT_NAME",
        "AZURE_STORAGE_ACCOUNT",
        "AZURE_STORAGE_ACCOUNT_KEY",
        "AZURE_STORAGE_CONTAINER",

    ]
    
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            raise ValueError(f"Missing required environment variable: {var}")
    
    # Configuration
    BLOB_CONNECTION_STRING = f"DefaultEndpointsProtocol=https;AccountName={os.getenv("AZURE_STORAGE_ACCOUNT")};AccountKey={os.getenv("AZURE_STORAGE_ACCOUNT_KEY")};EndpointSuffix=core.windows.net"
    BLOB_CONTAINER_NAME = f"{os.getenv("AZURE_STORAGE_CONTAINER")}"
  

    SEARCH_SERVICE_ENDPOINT = os.getenv("AZURE_AISEARCH_ENDPOINT")
    SEARCH_API_KEY = f"{os.getenv("AZURE_AISEARCH_KEY")}"
    SEARCH_INDEX_NAME = f"{os.getenv("AZURE_AISEARCH_INDEX")}"
    print(SEARCH_INDEX_NAME)

    # Initialize Blob Service Client
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=BLOB_CONTAINER_NAME, blob=file_path)

    # Download file from Blob Storage
    download_file_path = os.path.join(os.getcwd(), file_path)
    with open(download_file_path, "wb") as download_file:
        download_file.write(blob_client.download_blob().readall())

    file_extension = os.path.splitext(download_file_path)[-1].lower()
    if file_extension == ".pdf":
        # Extract text pages from the downloaded PDF 
        pages_text = extract_pages_from_pdf(download_file_path)    
    if file_extension == ".docx":
        # Extract text pages from downloaded docx
        pages_text = extract_pages_from_docx(download_file_path)


    # Document UUID
    document_uuid = str(uuid.uuid4())

    def generate_embeddings(text):
        headers = {
            "Content-Type": "application/json",
            "api-key": os.getenv("AZURE_OPENAI_KEY")
        }
        payload = {
            "input": text,
            "model": os.getenv("MODEL_EMBEDDINGS_DEPLOYMENT_NAME")
        }
        try:
            response = requests.post(
                f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/deployments/{os.getenv('MODEL_EMBEDDINGS_DEPLOYMENT_NAME')}/embeddings?api-version=2023-05-15",
                headers=headers,
                json=payload
            )
            # print(response.json())
            response.raise_for_status()
            return response.json()['data'][0]['embedding']
        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating embeddings: {e.response.text}")
            raise

    # Split text into sections

    def count_tokens(text):
        return len(text.split())

    documents = []

    for i, chunk in enumerate(pages_text):
        if chunk.strip():  # Skip empty sections
            logger.info(f"Processing chunk {i + 1}/{len(pages_text)}")
            embeddings = generate_embeddings(chunk)
            time.sleep(0.5)
            document = {
                "@search.action": "upload",
                "id": str(document_uuid),
                "title": str(file_path),
                "chunk": str(chunk),
                "embeddings": embeddings
            }
            documents.append(document)
            if (i > 100):
                break

    # Initialize Search Client
    search_client = SearchClient(endpoint=SEARCH_SERVICE_ENDPOINT, index_name=index_name, credential=AzureKeyCredential(SEARCH_API_KEY))

    # Upload documents to Azure Cognitive Search
    search_client.upload_documents(documents=documents)

    print("Documents uploaded successfully.")


if __name__ == "__main__":
    add_file_embeddings(index_name = "poc-input-file-2739", file_path="Paracetamol SmPC.pdf")