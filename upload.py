import logging
import os
import requests
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



def upload_files(file_path):
    required_vars = [
        "AZURE_STORAGE_ACCOUNT",
        "AZURE_STORAGE_ACCOUNT_KEY",
        "AZURE_STORAGE_CONTAINER",
        ]
 
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            raise ValueError(f"Missing required environment variable: {var}")
        
    try:        
        # Step 4: Connect to Azure Storage Account
        # Replace with your actual connection string and container name
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={os.getenv('AZURE_STORAGE_ACCOUNT')};AccountKey={os.getenv('AZURE_STORAGE_ACCOUNT_KEY')};EndpointSuffix=core.windows.net"        
        container_name = f"{os.getenv('AZURE_STORAGE_CONTAINER')}"
        blob_name = file_path

        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Step 5: Upload the extracted content to a blob in the storage account
        file_name = os.path.basename(file_path)
        with open(file_path, "rb") as data:
            blob_client = container_client.get_blob_client(blob_name)        
            blob_client.upload_blob(data, overwrite=True)
            print(f"Content uploaded to blob '{blob_name}' in container '{container_name}' successfully.")
        # return file_name
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        raise e

if __name__ == "__main__":    
    file_path = "file.txt"
    upload_files(file_path)