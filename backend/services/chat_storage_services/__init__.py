class ChatStorageService:
    """Parent class for chat storage services."""
    
    def __init__(self, config, name):
        self.config = config
        self.type = name
    
    def read_item(self, session_id, user_id):
        """Read a chat session document."""
        raise NotImplementedError
    
    def upsert_item(self, chat_session):
        """Insert or update a chat session document."""
        raise NotImplementedError
    
    def query_items(self, user_id):
        """Query all chat session documents for a given user."""
        raise NotImplementedError
