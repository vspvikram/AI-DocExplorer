

class LlmServiceClass:
    """Parent class for all LLM service classes"""

    def __init__(self, config, name):
        self.config = config
        self.type = name

    def query(self, prompt, **kwargs):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def additional_params(self, **kwargs):
        """Optional method to handle additional parameters for LLM queries"""
        pass


class EmbeddingModelClass:
    """Parent class for all embedding LLM models."""

    def __init__(self, config, name):
        self.config = config
        self.type = name

    def generate_embeddings(self, text):
        """Generate embeddings from the input text."""
        raise NotImplementedError("This method should be implemented by subclasses.")
