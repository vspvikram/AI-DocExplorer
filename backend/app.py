 
import os
import mimetypes
import time
import logging
import openai
from flask import Flask, request, jsonify
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from approaches.chatreadretrieveread import ChatReadRetrieveReadApproach
from azure.storage.blob import BlobServiceClient
#vik
from dotenv import load_dotenv
import unicodedata 
import PyPDF2 
from io import BytesIO
import json
from azure.cosmos import CosmosClient, PartitionKey, exceptions #vik: for cosmos db
from authlib.integrations.flask_client import OAuth #vik: for azure ad authentication
from flask import redirect, url_for, session, make_response #vik: for azure ad authentication
from functools import wraps #vik: for azure ad authentication
import hashlib #vik: for hashing chat session id

# importing services
from services.llm_services.openai.openai_chatapi import OpenAIChatService
from services.service_factory import get_llm_service, get_llm_embed_service, get_search_service, get_doc_storage_service, get_chat_storage_service

load_dotenv(dotenv_path=".environments/ai_chatbot/.env")
# Vik: Logging configuration
logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# Replace these with your own values, either in environment variables or directly here
AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT") or "mystorageaccount"
AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER") or "content"
AZURE_SEARCH_SERVICE = os.environ.get("AZURE_SEARCH_SERVICE") or "gptkb"
AZURE_SEARCH_INDEX = os.environ.get("AZURE_SEARCH_INDEX") or "gptkbindex"
AZURE_SEARCH_API_KEY = os.environ.get("AZURE_SEARCH_API_KEY") or "gptkey"
AZURE_SEARCH_STORAGE_KEY = os.environ.get("AZURE_SEARCH_STORAGE_KEY") or "gptstorage"
AZURE_OPENAI_SERVICE = os.environ.get("AZURE_OPENAI_SERVICE") or "myopenai"
AZURE_OPENAI_GPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_GPT_DEPLOYMENT") or "davinci"
AZURE_OPENAI_CHATGPT_DEPLOYMENT = os.environ.get("AZURE_OPENAI_CHATGPT_DEPLOYMENT") or "chat"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT") or "embedding" #vik: for embedding model
KB_FIELDS_CONTENT = os.environ.get("KB_FIELDS_CONTENT") or "content"
KB_FIELDS_CATEGORY = os.environ.get("KB_FIELDS_CATEGORY") or "category"
KB_FIELDS_SOURCEPAGE = os.environ.get("KB_FIELDS_SOURCEPAGE") or "sourcepage"

# Prepare config file
LLM_SERVICE_NAME = os.getenv('LLM_SERVICE_NAME')
LLM_MODEL_NAME = os.getenv('LLM_MODEL_NAME')
LLM_API_KEY = os.getenv('LLM_API_KEY')

LLM_EMBED_SERVICE_NAME=os.getenv('LLM_EMBED_SERVICE_NAME')
LLM_EMBED_MODEL_NAME=os.getenv('LLM_EMBED_MODEL_NAME')

SEARCH_SERVICE_NAME = os.getenv('SEARCH_SERVICE_NAME')
SEARCH_API_KEY = os.getenv('SEARCH_API_KEY')
SEARCH_INDEX_NAME=os.getenv('SEARCH_INDEX_NAME')
SEARCH_NAMESPACE = os.getenv('SEARCH_NAMESPACE')
KB_FIELDS_SOURCEPAGE=os.getenv('KB_FIELDS_SOURCEPAGE')
KB_FIELDS_CONTENT=os.getenv('KB_FIELDS_CONTENT')

DOC_STORAGE_SERVICE_NAME = os.getenv('DOC_STORAGE_SERVICE_NAME')
DOC_STORAGE_SECRET_ACCESS_KEY=os.getenv('DOC_STORAGE_SECRET_ACCESS_KEY')
DOC_STORAGE_ACCESS_KEY_ID=os.getenv('DOC_STORAGE_ACCESS_KEY_ID')
DOC_STORAGE_BUCKET_NAME=os.getenv('DOC_STORAGE_BUCKET_NAME')

CHAT_STORAGE_SERVICE_NAME = os.getenv('CHAT_STORAGE_SERVICE_NAME')
CHAT_STORAGE_ACCESS_KEY_ID = os.getenv('CHAT_STORAGE_ACCESS_KEY_ID')
CHAT_STORAGE_SECRET_ACCESS_KEY = os.getenv('CHAT_STORAGE_SECRET_ACCESS_KEY')
CHAT_STORAGE_TABLE_NAME = os.getenv('CHAT_STORAGE_TABLE_NAME')
CHAT_STORAGE_REGION_NAME = os.getenv('CHAT_STORAGE_REGION_NAME')

config = {
    "llm_service_name": LLM_SERVICE_NAME, "llm_api_key": LLM_API_KEY, 'llm_model_name': LLM_MODEL_NAME,
    'llm_embed_service_name': LLM_EMBED_SERVICE_NAME, 'llm_embed_model_name': LLM_EMBED_MODEL_NAME,
    "search_service_name": SEARCH_SERVICE_NAME, "search_api_key": SEARCH_API_KEY,
    "search_index_name": SEARCH_INDEX_NAME, 'search_namespace': SEARCH_NAMESPACE,
    'doc_storage_service_name': DOC_STORAGE_SERVICE_NAME,
    'doc_storage_access_key_id': DOC_STORAGE_ACCESS_KEY_ID, 
    'doc_storage_secret_access_key': DOC_STORAGE_SECRET_ACCESS_KEY,
    'doc_storage_bucket_name': DOC_STORAGE_BUCKET_NAME,
    'chat_storage_service_name': CHAT_STORAGE_SERVICE_NAME,
    'chat_storage_access_key_id': CHAT_STORAGE_ACCESS_KEY_ID, 
    'chat_storage_secret_access_key': CHAT_STORAGE_SECRET_ACCESS_KEY,
    'chat_storage_table_name': CHAT_STORAGE_TABLE_NAME,
    'chat_storage_region_name': CHAT_STORAGE_REGION_NAME
}

# Intializing the services clients
LLM_CLIENT = get_llm_service(config=config)
LLM_EMBED_CLIENT = get_llm_embed_service(config=config)
SEARCH_CLIENT = get_search_service(config=config)
DOC_STORAGE_CLIENT = get_doc_storage_service(config=config)
CHAT_STORAGE_CLIENT = get_chat_storage_service(config=config)

# Set up clients for Cognitive Search and Storage
# search_client_credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)
# search_client = SearchClient(
#     endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
#     index_name=AZURE_SEARCH_INDEX,
#     credential=search_client_credential)

# blob_client_credential = AzureKeyCredential(AZURE_SEARCH_STORAGE_KEY)
# blob_client = BlobServiceClient(
#     account_url=f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net", 
#     credential=AZURE_SEARCH_STORAGE_KEY)
# blob_container = blob_client.get_container_client(AZURE_STORAGE_CONTAINER)

# Vik: Cosmos DB client and container client
cosmos_url = os.environ.get("COSMOS_URL")
cosmos_key = os.environ.get("COSMOS_KEY")
# cosmos_client = CosmosClient(cosmos_url, cosmos_key)
# cosmos_db = cosmos_client.get_database_client("ChatHistory")
# cosmos_container = cosmos_db.get_container_client("ChatSessions")

# Various approaches to integrate GPT and external knowledge, 
chat_approaches = {
    "rrr": ChatReadRetrieveReadApproach(LLM_CLIENT, LLM_EMBED_CLIENT, SEARCH_CLIENT,
                                        DOC_STORAGE_CLIENT, KB_FIELDS_SOURCEPAGE, KB_FIELDS_CONTENT)
}


app = Flask(__name__)

# # Vik: Azure AD authentication
# oauth = OAuth(app)
# azure = oauth.register(
#     name='azure',
#     client_id=os.environ.get("CLIENT_ID"),
#     client_secret=os.environ.get("CLIENT_SECRET"),
#     access_token_url=f'https://login.microsoftonline.com/{os.environ.get("TENANT_ID")}/oauth2/token',
#     authorize_url=f'https://login.microsoftonline.com/{os.environ.get("TENANT_ID")}/oauth2/authorize',
#     api_base_url='https://graph.microsoft.com/',
#     client_kwargs={
#         'scope': 'openid profile email'
#     },
#     jwks_uri=f'https://login.microsoftonline.com/{os.environ.get("TENANT_ID")}/discovery/v2.0/keys'
# )

app.config.update({
    'SECRET_KEY': os.environ.get("FLASK_SECRET_KEY")
})

# Vik: function to create a new chat session id
def create_chat_session_id(user_id):
    timestamp = str(time.time())
    session_id = hashlib.sha256((user_id + timestamp).encode()).hexdigest()
    return session_id

# Vik: function to create a new chat session document in Cosmos DB
def create_chat_session_document(history, generated_answer, existing_session=None, chat_session=None):
    if existing_session and chat_session:
        chat_session['chatData'].append({
            "user": history[-1]['user'],
            "bot": generated_answer['answer']
        })
        chat_session["regeneration_data"] = {"history": history}
        chat_session["lastUpdateTime"] = time.time()
    else:
        full_history = history
        full_history[-1]['bot'] = generated_answer['answer']
        prompt = generated_answer['thoughts'].split('Prompt:')[1].replace('<br>', '\n')
        chat_session = {
            "id": session.get('session_id'), # session id
            "userId": session.get('email'), # user id
            "userOID": session.get('user_oid'),
            "firstName": session.get('first_name'),
            "lastName": session.get('last_name'),
            "sessionStartTime": session.get('session_timestamp'),
            "lastUpdateTime": time.time(),
            "chatSessionName": f"{history[-1]['user'][:20]}",
            "chatData": full_history,
            "regeneration_data": {
                "history": history,
            }
        }
    if generated_answer['Chat_Session_Name'] != "":
        chat_session['chatSessionName'] = generated_answer['Chat_Session_Name']
    chat_session['chatData'][-1]['Supporting_docs'] = [generated_answer['data_points'][i].split(':')[0] for i in range(len(generated_answer['data_points']))]
    chat_session['chatData'] = json.dumps(chat_session['chatData'])
    chat_session['regeneration_data'] = json.dumps(chat_session['regeneration_data'])
    return chat_session

# Vik: function to push the chat session document to Cosmos DB
def push_chat_session_document(request, r):
    session_id = session.get('session_id')
    user_email = session.get('email')

    # Attempt to read the existing chat session document
    chat_session = CHAT_STORAGE_CLIENT.read_item(session_id=session_id, user_id=user_email)
    if chat_session:
        # If the session document exists, update it
        chat_session = create_chat_session_document(request.json["history"], generated_answer=r, 
                                                    existing_session=True, chat_session=chat_session)
    else:
        # If the session document doesn't exist, create a new one
        chat_session = create_chat_session_document(request.json["history"], generated_answer=r)
    
    # Upsert the (new or updated) chat session document to DynamoDB
    CHAT_STORAGE_CLIENT.upsert_item(chat_session=chat_session)
    
    # try:
    #     chat_session = cosmos_container.read_item(item=session.get('session_id'), partition_key=session.get('email'))
    #     chat_session = create_chat_session_document(request.json["history"], generated_answer=r,
    #                                                 existing_session=True, chat_session=chat_session)
    # except exceptions.CosmosResourceNotFoundError:
    #     # If the session document doesn't exist, create a new one
    #     chat_session = create_chat_session_document(request.json["history"], generated_answer=r)
    # cosmos_container.upsert_item(chat_session)
 
# Vik: User login protocols for Azure AD authentication
# #vik: login route
# @app.route("/login")
# def login():
#     # redirect_uri = url_for('authorize', _external=True)
#     session['next_url'] = request.args.get('referrer')
#     redirect_uri = url_for('authorize', _external=True, _scheme='https')
#     # # Vik cosmos maintainence code
#     # for item in cosmos_container.query_items(
#     #         query='SELECT * FROM c',
#     #         enable_cross_partition_query=True):
#     #     chat_data = item['chatData']
        
#     #     chat_session_name = f"{chat_data[0]['user']}"
#     #     chat_session_name = chat_session_name.capitalize()
#     #     item['chatSessionName'] = chat_session_name
#     #     history_ = []
#     #     for i in range(len(chat_data)):
#     #         if i < len(chat_data) - 1:
#     #             history_.append({"user": chat_data[i]["user"], "bot": chat_data[i]["bot"]})
#     #         else:
#     #             history_.append({"user": chat_data[i]["user"]})
        
#     #     item["regeneration_data"] = {"history": history_}
            
#     #     cosmos_container.upsert_item(item)
#     return azure.authorize_redirect(redirect_uri)

#vik: authorize route
@app.route("/authorize")
def authorize():
    # token = azure.authorize_access_token()
    # user_info = token['userinfo']
    user_info = {
        "unique_name": "vikramsingh@temp.com",
        "given_name": "Vikram",
        "family_name": "Singh",
        "oid": "123456789",

    }
    session['email'] = user_info['unique_name']
    session['first_name'] = user_info['given_name']
    session['last_name'] = user_info['family_name']
    session['user_oid'] = user_info['oid']
    session['session_id'] = create_chat_session_id(session['email'])
    session['session_timestamp'] = time.time()
    next_url = session.pop('next_url', '/')
    logging.info(f"Session data after authorization: {session}")
    resp = make_response(redirect(next_url))
    resp.set_cookie('shouldRefetch', 'true', max_age=120)  # Set for 1 minute
    return resp
    # return redirect(next_url)

#vik: function to check if user is logged in
def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"Route being accessed: {request.path}, Method: {request.method}")  # Add logging
        if 'email' not in session:
            # Check if the request if an AJAX request
            if request.headers.get('X-Requested-With') == 'chatComponent':
                next_url = "/" # request.url
                login_url = url_for('login', next=next_url)
                response = jsonify(error='login_required', login_url=login_url)
                response.status_code = 403
                return response
            else:
                # For regular web page requests, redirect to the login page
                return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
 
#vik: logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Vik: route to reset the chat session
@app.route('/clear_history', methods=['POST'])
# @require_login
def clear_history():
    session['session_id'] = create_chat_session_id(session['email'])
    session['session_timestamp'] = time.time()
    # New session id creation in the '/' route
    return redirect('/')

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def static_file(path):
    logging.info(f"Session data at beginning of static_file for path {path}: {session}")
    response = make_response(app.send_static_file(path))
    # response.set_cookie('session_id', "1234567890")
    return response
# @app.route("/", defaults={"path": "index.html"})
# @app.route("/<path:path>")
# def static_file(path):
#     logging.info(f"Session data at beginning of static_file for path {path}: {session}")
#     session['session_id'] = create_chat_session_id(session['email'])
#     session['session_timestamp'] = time.time()
#     response = make_response(app.send_static_file(path))
#     response.set_cookie('session_id', session['session_id'])
#     return response


# Serve content files from blob storage from within the app to keep the example self-contained. 
# *** NOTE *** this assumes that the content files are public, or at least that all users of the app
# can access all the files. This is also slow and memory hungry.
@app.route("/content/<path>")
# @require_login
def content_file(path):
    # blob = blob_container.get_blob_client(path).download_blob()
    return_blob = DOC_STORAGE_CLIENT.download_document(path)
    # mime_type = blob.properties["content_settings"]["content_type"]
    # if mime_type == "application/octet-stream":
    mime_type = mimetypes.guess_type(path)[0] or "application/octet-stream"
    # return_blob = blob.readall() #vik
    # return_blob = return_blob.decode('latin-1', 'ignore') #vik
    # return_blob = return_blob.replace('\u2013', '?') #vik
    # return_blob = return_blob.encode('latin-1', 'ignore') #vik
    # modified_pdf_content = BytesIO()
    # doc = fitz.open(stream=return_blob, filetype="pdf")
    # for page in doc:
    #     modified_content = page.get_text().replace('\u2013', 'vsp')  # Remove en dash character
    #     modified_pdf_content.write(modified_content.encode('latin-1', errors='replace'))
    # modified_pdf_bytes = modified_pdf_content.getvalue()
    # return blob.readall(), 200, {"Content-Type": mime_type, "Content-Disposition": f"inline; filename={path}"}
    return return_blob, 200, {"Content-Type": mime_type, "Content-Disposition": f"inline; filename={path}"}
 
# Vik: Fetch the current version number from the version.json file
@app.route("/version", methods=["GET"])
def version():
    try:
        # if testing in debug mode then change the file path to "./backend/version.json" and for deployment "./version.json"
        with open("./backend/version.json", "r") as f:
            data = json.load(f)
            for obj in data:
                if obj["current_version"]:
                    return jsonify({"version": obj["version"]})
    except FileNotFoundError:
        return jsonify({"version": "unknown"})
 
# Vik: Fetch the current user's chat history from Cosmos DB using the user's email
# def fetch_chat_history(user_email):
#     try:
        # query={
        #     "query": f'SELECT * FROM ChatSessions c WHERE c.userId = @userEmail ORDER BY c._ts DESC',
        #     "parameters": [
        #         {"name": "@userEmail", "value": user_email}
        #     ]
        # }
        # items = list(cosmos_container.query_items(query=query, enable_cross_partition_query=True))
#         return items
#     except exceptions.CosmosResourceNotFoundError:
#         return jsonify({"error": "No chat history found"}), 400
    
# Vik: Fetch the chat history for the current user from Cosmos DB
# @app.route("/getChatHistory", methods=["GET"])
# @require_login
# def get_chat_history():
#     user_email = session['email']
#     chat_history = fetch_chat_history(user_email)
#     # # Vik cosmos maintainence code
#     # for item in cosmos_container.query_items(
#     #         query='SELECT * FROM c',
#     #         enable_cross_partition_query=True):
#     #     chat_data = item['chatData']
        
#     #     chat_session_name = f"{chat_data[0]['user']}"
#     #     chat_session_name = chat_session_name.capitalize()
#     #     item['chatSessionName'] = chat_session_name
#     #     history_ = []
#     #     for i in range(len(chat_data)):
#     #         if i < len(chat_data) - 1:
#     #             history_.append({"user": chat_data[i]["user"], "bot": chat_data[i]["bot"]})
#     #         else:
#     #             history_.append({"user": chat_data[i]["user"]})
        
#     #     item["regeneration_data"] = {"history": history_}
            
#     #     cosmos_container.upsert_item(item)
#     return jsonify(chat_history)
        
# @app.route("/ask", methods=["POST"])
# @require_login
# def ask():
#     # ensure_openai_token()
#     approach = request.json["approach"]
#     try:
#         impl = ask_approaches.get(approach)
#         if not impl:
#             return jsonify({"error": "unknown approach"}), 400
#         r = impl.run(request.json["question"], request.json.get("overrides") or {})
#         return jsonify(r)
#     except Exception as e:
#         logging.exception("Exception in /ask")
#         return jsonify({"error": str(e)}), 500
    
@app.route("/chat", methods=["POST"])
# @require_login
def chat():
    # ensure_openai_token()
    approach = request.json["approach"]
    try:
        # checking if it's a fresh chat session
        if len(request.json["history"]) == 1:
            session['session_id'] = create_chat_session_id(session['email'])
            session['session_timestamp'] = time.time()
        impl = chat_approaches.get(approach)
        if not impl:
            return jsonify({"error": "unknown approach"}), 400
        r = impl.run(request.json["history"], request.json.get("overrides") or {})
        # Vik: save chat session to Chat session storage service
        push_chat_session_document(request, r)
        return jsonify(r)
    except Exception as e:
        logging.exception("Exception in /chat")
        return jsonify({"error": str(e)}), 500
    
@app.route("/chatSession/<session_id>", methods=["GET"])
# @require_login
def chat_session(session_id):
    # check if the session id is valid session_id, user_id
    try:
        chat_session = CHAT_STORAGE_CLIENT.read_item(session_id=session_id, user_id=session['email'])
        session['session_id'] = session_id
        return jsonify(chat_session)
    except:
        return jsonify({"error": "Invalid session id"}), 400
    
def fetch_all_chat_history(user_email):
    try:
        query = f"SELECT * FROM \"{CHAT_STORAGE_TABLE_NAME}\" WHERE \"userId\" = '{user_email}'"
        # query={
        #     "query": f'SELECT c.id, c.chatSessionName, c._ts  FROM ChatSessions c WHERE c.userId = @userEmail ORDER BY c._ts DESC',
        #     "parameters": [
        #         {"name": "@userEmail", "value": user_email} 
        #     ]
        # }
        items = CHAT_STORAGE_CLIENT.query_items(query=query)
        # items = list(cosmos_container.query_items(query=query, enable_cross_partition_query=True))
        return items
    except:
        return "Error: Error in fetching the chat sessions for the user"

@app.route('/check_login', methods=['GET'])
def check_login():
    try:
        if 'email' in session:
            userData = {"firstName": session['first_name'], 
                        "lastName": session['last_name'], 
                        "email": session['email'], "session_id": session['session_id']}
            chatSessions = fetch_all_chat_history(session['email'])  # Assume get_user_data is a function to fetch user data.
            # chatSessions = []
            
            user_data = {"userData": userData, "chatSessions": chatSessions, "isLoggedIn": True}
            return jsonify(user_data)
        else:
            return jsonify({'error': 'Not logged in', "isLoggedIn": False}), 401
    except Exception as e:
        print(f"Error: {e}") # Vik: for debugging
        return jsonify({'error': 'Server error'}), 500
 
# def ensure_openai_token():
#     global openai_token
#     if openai_token.expires_on < int(time.time()) - 60:
#         openai_token = azure_credential.get_token("https://cognitiveservices.azure.com/.default")
#         openai.api_key = openai_token.token
    
if __name__ == "__main__":
    app.run(ssl_context='adhoc') #debug=True, ssl_context='adhoc'

