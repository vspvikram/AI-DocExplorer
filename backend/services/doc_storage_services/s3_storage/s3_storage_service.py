# s3_storage_service.py
from services.doc_storage_services import DocStorageService
import boto3

class S3StorageService(DocStorageService):
    """S3 implementation of the DocStorageService."""

    def __init__(self, config):
        super().__init__(config, name="S3StorageService")
        self.s3_client = boto3.client('s3', aws_access_key_id=config['doc_storage_access_key_id'], aws_secret_access_key=config['doc_storage_secret_access_key'])
        self.bucket_name = config['doc_storage_bucket_name']

    def upload_document(self, document, path):
        """Upload a document to S3."""
        self.s3_client.put_object(Body=document, Bucket=self.bucket_name, Key=path)

    def download_document(self, path):
        """Download a document from S3."""
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=path)
        document_content = response['Body'].read()
        return document_content

