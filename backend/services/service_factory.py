
# Get the LLM service model class
def get_llm_service(config):
    if config['llm_service_name'] == 'openai':
        from services.llm_services.openai.openai_chatapi import OpenAIChatService
        return OpenAIChatService(config)
    elif config['llm_service_name'] == 'huggingface':
        from services.llm_services.huggingface.huggingface_tinyllama2 import HuggingfaceTinyLlama
        return HuggingfaceTinyLlama(config)

# Get the LLM Embedding model class
def get_llm_embed_service(config):
    if config['llm_embed_service_name'] == 'sentence_transformer':
        from services.llm_services.sentence_transformers.sentence_transformers_service import SentenceTransformerModel
        return SentenceTransformerModel(config)
    
# Get the Search service class
def get_search_service(config):
    if config['search_service_name'] == 'elastic':
        from services.search_services.elastic_search.elastic_search_service import ElasticSearchService
        return ElasticSearchService(config)
    elif config['search_service_name'] == 'pinecone':
        from services.search_services.pinecone.pinecone_search_service import PineconeSearchService
        return PineconeSearchService(config)

# Get the document storage service class
def get_doc_storage_service(config):
    if config['doc_storage_service_name'] == 's3':
        from services.doc_storage_services.s3_storage.s3_storage_service import S3StorageService
        return S3StorageService(config)

# Get the chat sessions storage service class
def get_chat_storage_service(config):
    if config['chat_storage_service_name'] == 'dynamodb':
        from services.chat_storage_services.dynamo_db.dynamo_db_service import DynamoDBChatStorageService
        return DynamoDBChatStorageService(config)