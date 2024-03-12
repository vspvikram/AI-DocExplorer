# Plug-and-Play-RAG

# Quantum AI Search Assistant: QASA
------------------


This is the main codebase for the QASA project. It is a web application that allows users to interact with a chatbot to get information about their own files stored in database. 


The chatbot is powered by these services running on the azure cloud:
- Pinecone Index Search Service
- AWS S3 Storage Service
- Azure OpenAI Service:
    - GPT-3.5 Turbo API for the generative model 
- AWS DynamoDB Storage Service
    - To store the chat history of the users


The web application is built using the flask framework for backend and React for frontend and is hosted on an Azure App Service.


## Installation
To use this codebase, you will need to follow the steps mentioned below. 


Any issues or bugs can be reported to the issues tab of this repository or by contacting the developers: (Vikram Singh).


# To run the app locally


## Install the dependencies for the backend
```
# creating python virtual environment for the backend
python -m venv backend/backend_env
```


```
cd backend
# For windows
./backend_env/Scripts/python.exe -m pip install -r requirements.txt

# For Mac OS
source ./backend_env/bin/activate
pip install -r requirements.txt
```



## Install the dependencies for the frontend
```
cd frontend
#if the packages are not installed then run the command below
npm install  
```
```
npm run build
cd ..\backend 
```


## Setup the environment variables
Make sure you have created an os environment variables file for your app by creating folders `.azure/<your env name>`. Add a new file named `.env` and add the following content to it:
```
# Openai API key
LLM_SERVICE_NAME="<your LLM service Name or openai>"
LLM_API_KEY="<Your LLM service api key>"

# Embedding LLM service and model name
LLM_EMBED_SERVICE_NAME="<LLM Embedding model service name>"
LLM_EMBED_MODEL_NAME="<LLM Embedding model name>"

# Pinecone key
SEARCH_SERVICE_NAME = "<Search Service name, e.g. pinecone>"
SEARCH_API_KEY="<Search Service API key>"
SEARCH_INDEX_NAME="<Search Index name>"
KB_FIELDS_SOURCEPAGE="<Sourcepage field name on Index>"
KB_FIELDS_CONTENT="<Text content field name on Index>"

#S3 access key
DOC_STORAGE_SERVICE_NAME="<Storage Service name for storing documents>"
DOC_STORAGE_SECRET_ACCESS_KEY="<Storage Service secret access key>"
DOC_STORAGE_ACCESS_KEY_ID="<Storage Service access key>"
DOC_STORAGE_BUCKET_NAME="<Storage service bucket/container name>"

CHAT_STORAGE_SERVICE_NAME="<Storage service name for storing chat sessions>"
CHAT_STORAGE_SECRET_ACCESS_KEY="<Chat storage service secret access key>"
CHAT_STORAGE_ACCESS_KEY_ID="<Chat storage service access key>"
CHAT_STORAGE_TABLE_NAME="<Chat storage table name>"
CHAT_STORAGE_REGION_NAME="<Chat storage service region name>"

FLASK_SECRET_KEY="<Define you secret flask key>"
```
After creating the file, you should update the path to this file in `backend/app.py` in the `load_dotenv` function call with the name of your `<env name>`


## To run locally
```
./backend_env/Scripts/python.exe ./app.py 
```
--------------------------------
--------------------------------


# To deploy to azure web app


## Install the dependencies for the frontend and build the frontend
--------------------------------
```
cd frontend
#if the packages are not installed then run the command below
npm install  
```
```
npm run build
cd ..\backend 
```


## Environment variables setup in the azure web app
--------------------------------
In the azure portal, go to the `Web-App -> Configuration (under settings)` and set the following environment variables by clicking on the `New application setting` button
```
AZURE_ENV_NAME="<your env name>"
AZURE_OPENAI_RESOURCE_GROUP="<resource group name>"
AZURE_OPENAI_SERVICE="<openai service name>"
AZURE_STORAGE_ACCOUNT="<storage account name>"
AZURE_STORAGE_CONTAINER="<storage container name>"
AZURE_SEARCH_SERVICE="<search service name>"
AZURE_SEARCH_INDEX="<search index name>"
AZURE_SEARCH_API_KEY="<search api key>"
AZURE_SEARCH_STORAGE_KEY="<search storage key>"
AZURE_OPENAI_GPT_DEPLOYMENT="<openai gpt deployment name>"
AZURE_OPENAI_CHATGPT_DEPLOYMENT="<openai chat gpt deployment name>"
OPENAI_API_KEY="<openai api key of user>"
SCM_DO_BUILD_DURING_DEPLOYMENT="true"
```
This part can also be done using the azure cli. Please refer to the following link for more details: https://docs.microsoft.com/en-us/azure/app-service/configure-common#configure-app-settings



## Create a ZIP file of your application with the following files and folders in backend folder
--------------------------------
```
- approaches
- static
- app.py
- langchainadapters.py
- lookuptool.py
- requirements.txt
- text.py
- version.json
```


## ENV variables setup
--------------------------------
In the powershell terminal, run the following commands to set the environment variables
```
$resourceGroupName='finsit-t113-20230330' or <your resource group name>
$appServiceName='GCAChatbot' or <your app name>
$env:SCM_DO_BUILD_DURING_DEPLOYMENT='true'          
```


## To deploy the app to Azure
```
az webapp deploy --name $appServiceName --resource-group $resourceGroupName --src-path app.zip
```


## For troubleshooting: setting subscription to the account
```
az account set --subscription fce04e5c-fd9f-462a-abb8-9e83ac353dba
# confirm if the subscription is set to the correct account
az account show
```



