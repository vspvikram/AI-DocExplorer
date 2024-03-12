# doc_storage_service.py
class DocStorageService:
    """Parent class for all document storage services."""
    
    def __init__(self, config, name):
        self.config = config
        self.type = name

    def upload_document(self, document, path):
        """Upload a document to a storage service."""
        raise NotImplementedError

    def download_document(self, path):
        """Download a document from a storage service."""
        raise NotImplementedError
