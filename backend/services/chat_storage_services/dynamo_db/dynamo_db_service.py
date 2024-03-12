import boto3
from botocore.exceptions import ClientError
from services.chat_storage_services import ChatStorageService

class DynamoDBChatStorageService(ChatStorageService):
    def __init__(self, config):
        super().__init__(config, name="DynamoDBChatStorageService")
        self.client = boto3.client('dynamodb', 
                                   aws_access_key_id=config['chat_storage_access_key_id'], 
                                   aws_secret_access_key=config['chat_storage_secret_access_key'], 
                                   region_name=config['chat_storage_region_name'])
        self.table_name = config['chat_storage_table_name']
    
    def read_item(self, session_id, user_id):
        try:
            response = self.client.get_item(
                TableName=self.table_name,
                Key={
                    'userId': {'S': user_id},
                    'id': {'S': session_id}
                }
            )
            if 'Item' in response:
                item = {k: list(v.values())[0] for k, v in response['Item'].items()}
                return item
            else:
                return None
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None

    def upsert_item(self, chat_session):
        try:
            self.client.put_item(
                TableName=self.table_name,
                Item={k: {'S': str(v)} for k, v in chat_session.items()}
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False
        return True

    def query_items(self, query):
        try:
            response = self.client.execute_statement(
                Statement=query
            )
            items = [dict(zip(item.keys(), [list(val.values())[0] for val in item.values()])) for item in response['Items']]
            return items
        except ClientError as e:
            print(e.response['Error']['Message'])
            return None
