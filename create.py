import os
import random
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch, # needed?
    VectorSearch,
    HnswAlgorithmConfiguration,
    ExhaustiveKnnAlgorithmConfiguration,
    HnswParameters,
    ExhaustiveKnnParameters,
    VectorSearchAlgorithmMetric,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    VectorSearchAlgorithmConfiguration,
)
import logging
#from azure.search.documents import SearchServiceClient

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_file_index(): 
    required_vars = [
        "AZURE_AISEARCH_KEY",
        "AZURE_AISEARCH_INDEX",
        "AZURE_EMBEDDING_DIMENSIONS",
    ]

    # service_endpoint = os.getenv("AZURE_AISEARCH_ENDPOINT")
    endpoint = os.getenv("AZURE_AISEARCH_ENDPOINT")
    admin_key = os.getenv("AZURE_AISEARCH_ADMIN_KEY")
    index_name = os.getenv("AZURE_AISEARCH_CREATE_INDEX")
    random_suffix = random.randint(1000, 9999)
    index_name = index_name.replace("-file", f"-file-{random_suffix}")

    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            raise ValueError(f"Missing required environment variable: {var}")

    credential = AzureKeyCredential(admin_key)

    # Define the semantic configuration
    semantic_config = SemanticConfiguration(
        name="default",
        prioritized_fields=SemanticPrioritizedFields(
            prioritized_content_fields=[SemanticField(field_name="chunk")]
        )
    )

    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="title", type=SearchFieldDataType.String),
        # SearchableField(name="drug", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=True), # keep sortable? idk
        # SearchableField(name="comorbidity", type=SearchFieldDataType.String, searchable=True, sortable=True),
        # SearchableField(name="safety", type=SearchFieldDataType.String, searchable=True, sortable=True),
        # SearchableField(name="date", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=True),
        # SearchableField(name="keywords", type=SearchFieldDataType.String, searchable=True, filterable=True, sortable=True),    
        # SearchableField(name="document_num", type=SearchFieldDataType.String), 
        # SearchableField(name="page_num", type=SearchFieldDataType.String), # more related to pdfs? thought we were looking at word docs
        # SearchableField(name="chunk_num", type=SearchFieldDataType.String), # more related to pdfs? thought we were looking at word docs
        # SearchableField(name="chunk_begin", type=SearchFieldDataType.String), # more related to pdfs? thought we were looking at word docs
        # SearchableField(name="chunk_end", type=SearchFieldDataType.String), # more related to pdfs? thought we were looking at word docs
        SearchableField(name="chunk", type=SearchFieldDataType.String),
        
        SearchField(
            name="embeddings",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            vector_search_dimensions=3072,
            vector_search_configuration="vector-config",
            vector_search_profile_name="default"
        )
    ]

    # Define VectorSearch configuration
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="default-HNSW",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE
                ),
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="default",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(
                    metric=VectorSearchAlgorithmMetric.COSINE
                ),
            ),
        ],
        profiles=[
            VectorSearchProfile(
                name="default",
                algorithm_configuration_name="default",
            ),
            VectorSearchProfile(
                name="default-HNSW",
                algorithm_configuration_name="default-HNSW",
            ),
        ],
    )

    index = SearchIndex(
        name=index_name,
        fields=fields,
        vector_search=vector_search
    )

    try:        
        # Create or update the index
        index_client.create_or_update_index(index)
        logger.info(f"Index {index_name} created")
    except Exception as e:
        logger.error(f"Error creating index: {e}")
        raise e

    

    '''

    # Initialize Search Service Client to manage service-level settings
    service_client = SearchServiceClient(endpoint=service_endpoint, credential=credential)

    # Get the current service settings
    service_settings = service_client.get_service_statistics()

    # Update CORS settings
    service_settings.cors_options = {
        "allowed_origins": ["*"],  # Replace with specific origins if needed
        "max_age_in_seconds": 3600,
        "allowed_methods": ["GET", "POST", "PUT", "OPTIONS"],
        "allowed_headers": ["*"],
        "exposed_headers": ["*"]
    }

    # Apply the updated settings
    service_client.update_service_statistics(service_settings)

    print("CORS settings updated successfully.")

    '''
if __name__ == "__main__":
    create_file_index()