# search_service.py
class SearchServiceClass:
    """Parent class for all search services."""
    
    def __init__(self, config, name):
        self.config = config
        self.type = name

    def index_document(self, document_id, vector):
        """Index a document in the search service."""
        raise NotImplementedError

    def query_index(self, vector, top_k):
        """Query the search index."""
        raise NotImplementedError
