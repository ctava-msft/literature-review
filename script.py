import os
import requests

from dotenv import load_dotenv
from upload import upload_file_to_blob
from create import create_file_index
from ingest import add_file_embeddings
from query import query_azure_search

# Load the environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
ENDPOINT = os.getenv("ENDPOINT")

# Function to call Azure OpenAI endpoint
def call_azure_openai(input):
    url = f"{ENDPOINT}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    data = {
        "question": input,
        "chat_history": []
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

if __name__ == "__main__":
    # input = "tell me a joke"
    # results = call_azure_openai(input)
    while True:
        print("\nEnter an option:")
        print("1. Upload a file to storage")        
        print("2. Enter a drug to query")
        print("3. Exit")
        # print("1. Upload a drug safety file to storage")
        # print("2. Upload an abstracts file to storage")
        # print("3. Enter a drug to query")
        # print("4. Exit")

        answer = input("Enter your choice: ").strip()
        if answer == "1":
            input = input("Enter the file path: ")
            container_name = os.getenv("AZURE_STORAGE_CONTAINER")
            if os.path.isfile(input):
                try:
                    upload_file_to_blob(input)
                    create_file_index()
                    add_file_embeddings(input)
                except Exception as e:
                    print(f"Error uploading file: {e}")
            results = call_azure_openai(input)
            print(results)
        elif answer == "2":
            input = input("Enter the drug name: ")
            # results = call_azure_openai(input)
            query_azure_search(input)
            print(results)
        elif answer == "3":
            print("Exiting...")
            break
        # elif answer == "2":
        #     if os.path.isfile(input):
        #         try:
        #             upload_file_to_blob(input)
        #             create_file_index()
        #             add_file_embeddings()
        #         except Exception as e:
        #             print(f"Error uploading file: {e}")
        #     results = call_azure_openai(input)
        #     print(results)
        else:
            print("Invalid option. Please try again.")
            continue
    print(results)