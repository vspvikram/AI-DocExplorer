# pinecone_search_service.py
from services.search_services import SearchServiceClass
import pinecone
import numpy as np

class PineconeSearchService(SearchServiceClass):
    """Pinecone implementation of the SearchServiceClass."""

    def __init__(self, config):
        super().__init__(config, name="PineconeSearchService")
        if 'search_api_key' not in config or 'search_index_name' not in config:
            raise "Config does not have api keys and index names"
        pc = pinecone.Pinecone(api_key=config['search_api_key'])
        self.index_name = config['search_index_name']
        self.index = pc.Index(self.index_name)

    def index_document(self, document_id, vector, metadata=None):
        """Index a document in Pinecone."""
        self.index.upsert(vectors=[(document_id, vector, metadata)])

    def query_index(self, vector, top_k=5):
        """Query the Pinecone index."""
        if isinstance(vector, np.ndarray):
            vector = vector.tolist()
        results = self.index.query(vector=vector, top_k=top_k,  include_metadata=True)
        results = results['matches']

        formatted_results = []

        for item in results:
            # Extract the required information from each item
            formatted_item = {
                "id": item.get('id'),
                "content": item['metadata'].get('content') if item.get('metadata') else None,
                "sourcefile": item['metadata'].get('sourcefile') if item.get('metadata') else None,
                "sourcepage": item['metadata'].get('sourcepage') if item.get('metadata') else None,
                "score": item.get('score')
            }
            formatted_results.append(formatted_item)
        return formatted_results
    


