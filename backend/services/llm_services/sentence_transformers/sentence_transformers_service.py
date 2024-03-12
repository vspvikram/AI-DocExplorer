from sentence_transformers import SentenceTransformer
from services.llm_services import EmbeddingModelClass

class SentenceTransformerModel(EmbeddingModelClass):
    """Implementation of EmbeddingModel using Sentence Transformers."""

    def __init__(self, config):
        super().__init__(config, name="SentenceTransformerModel")
        if 'llm_embed_model_name' not in config:
            raise "Embedding model name not in the config file"
        self.model = SentenceTransformer(config['llm_embed_model_name'])

    def generate_embeddings(self, text):
        """Generate embeddings from the input text using Sentence Transformers."""
        embeddings = self.model.encode(text)
        return embeddings
