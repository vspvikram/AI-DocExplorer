import os
import openai
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import QueryType
from approaches.approach import Approach
from azure.storage.blob import ContainerClient #vik
from .text import nonewlines
from io import BytesIO #vik
import PyPDF2 #vik
import numpy as np #vik
import re #vik
from services.llm_services import LlmServiceClass
from services.llm_services import EmbeddingModelClass
from services.chat_storage_services import ChatStorageService
from services.doc_storage_services import DocStorageService
from services.search_services import SearchServiceClass
# from openai.error import InvalidRequestError #vik
# from approaches.groundedness import create_prompt_groundedness, get_int_between_tags
# Chat Limit 
CHAT_LIMIT = 30 #vik


# Vik: data cleaning before embedding generation
def clean_text(text, sep_token = " \n "):
    s = re.sub(r'\s+', ' ', text).strip()
    s = re.sub(r". ,", "", s)
    s = s.replace("..", ".")
    s = s.replace(". .", ".")
    s = s.replace("\n", " ")
    s = s.strip()
    return s
 
class ChatReadRetrieveReadApproach(Approach):
    prompt_prefix = """
You are an assistant that helps users with their quantum physics research questions.
Strictly utilize ONLY the facts from the designated documents below. If the required information isn't contained within these documents, your response should be "That information is not in the reference sources provided to me." Under no circumstances should you generate responses that aren't based on the provided documents. If asking a clarifying question to the user would help, ask the question. If there are multiple correct answers, ask a clarifying question to the user before responding. 
For tabular information return it as an html table. Do not return markdown format.
Each source has a name followed by colon and the actual information and the sources are separated by two new line characters. Each fact you use in the response should be accompanied by a citation in square brackets, including the full name of the source with its extension, e.g., [source_name.extension]. Please refrain from combining sources and list each source separately using square brackets, e.g., [source1.pdf] [source2.txt] [source3 Document.pdf]. Just use the source full file name with its extension inside the square brackets, do not include additional text inside the square brackets.
{follow_up_questions_prompt}
"""

    follow_up_questions_prompt_content = """Generate three very brief follow-up questions that the user would likely ask next about their quantum physics research. 
    Use double angle brackets to reference the questions, e.g. <<Are there exclusions for prescriptions?>>.
    Try not to repeat questions that have already been asked.
    Only generate questions and do not generate any text before or after the questions, such as 'Next Questions'"""

    query_prompt_template = """Below is a history of the conversation so far, and a new question asked by the user that needs to be answered by searching in a knowledge base for quantum physics research papers. 
    Generate a search query based on the conversation and the new question. 
    Do not include cited source filenames and document names e.g info.txt or doc.pdf in the search query terms.
    Do not include any text inside [] or <<>> in the search query terms.
    Do not include any additional words or special characters like "search query", only generate the optimized search query that can directly be used.
    If the question is not in English, translate the question to English before generating the search query.
    """

    chat_session_name_prompt = """"Using the chat history provided below between tripple backticks, generate a concise chat session name. Only generate the chat session name without using unnecessary words such as 'Chat name', special characters, and tags such as 'user' and 'assistant'. Generate a pure alpha-numeric [A-Za-z0-9 ] name without using any special characters except whitespace. The name should be long enough with at least 30 characters and short enough with no more than 50 characters in it. The chat history is as follows:
Chat History: ```{chat_history}```
Chat Session Name: 
"""
    def __init__(self, llm_client: LlmServiceClass, llm_embed_client: EmbeddingModelClass,
                 search_client: SearchServiceClass, 
                 doc_storage_client: DocStorageService,
                 sourcepage_field: str, 
                 content_field: str):       
          
        self.search_client = search_client
        self.llm_client = llm_client
        self.llm_embed_client = llm_embed_client
        self.doc_storage_client = doc_storage_client
        self.sourcepage_field = sourcepage_field
        self.content_field = content_field


    # vik: generate embeddings for the given text
    def get_embeddings(self, text=None):
        if self.llm_embed_client is None:
            raise Exception("Embedding deployment is not set")
        # check if the text has less than 2048 tokens
        if len(text.split()) > 2048:
            raise Exception("Text has more than 2048 tokens")
        
        # clean the text
        text = clean_text(text)
        
        # generate embeddings
        embeddings = self.llm_embed_client.generate_embeddings(
            text = text
        )
        return embeddings
    

    def run(self, history: list[dict], overrides: dict) -> any:
        chat_length = len(history)
        if len(history) > CHAT_LIMIT: #vik: limit the chat history
            answer = "The chat history is too long, please start a new chat session. Sorry for the inconvenience..."
            return {"data_points": "", 
                    "answer": answer, "thoughts": f"Searched for:<br>""<br><br>Prompt:<br>",
                    "Chat_Limit": CHAT_LIMIT, "Current_Chat_Length": chat_length}
        use_semantic_captions = True if overrides.get("semantic_captions") else False
        top = overrides.get("top") or 5
        exclude_category = overrides.get("exclude_category") or None
        filter = "category ne '{}'".format(exclude_category.replace("'", "''")) if exclude_category else None


        # STEP 1: Generate an optimized keyword search query based on the chat history and the last question
        messages = self.llm_client.format_prompt(system_prompt=self.query_prompt_template,
                                                 chat_history=history)
        completion = self.llm_client.create(messages=messages)
        q = completion


        # vik: function wrapper to get the search results for the given query
        def get_search_results(q):
            # STEP 2: Retrieve relevant documents from the search index with the LLM optimized query
            r = self.search_client.query_index(vector=self.get_embeddings(q),
                                               top_k=top)
            

            return r
        
        # vik: function to get the search results based on the preference to use just the chunks of the content or the entire content of the page
        def get_search_results_content(r, full_content=True):
            if not full_content:
                results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
            else:
                # results = [doc[self.sourcepage_field] + ": " + nonewlines(doc[self.content_field]) for doc in r]
                #vik: downloading the entire content of the pages
                results = []
                print("For query: {}".format(q))
                for doc in r:
                    print("Doc ID: {}".format(doc['sourcepage']))
                    # print("Doc Search Score: {}".format(doc['@search.score']))
                    # print("Doc Reranker score: {}".format(doc['@search.reranker_score']))
                    blob_client = self.blob_container.get_blob_client(doc[self.sourcepage_field])
                    blob = blob_client.download_blob()
                    stream = BytesIO()
                    blob.download_to_stream(stream)
                    filereader = PyPDF2.PdfReader(stream)
                    text_pdf = filereader.pages[0].extract_text()
                    results.append(doc[self.sourcepage_field] + ": " + nonewlines(text_pdf))
                # results = [doc[self.sourcepage_field] + ": " + nonewlines(self.blob_container.get_blob_client(doc[self.sourcepage_field]).download_blob().content_as_text(encoding='UTF-8')) for doc in r]
            content = "\n\n".join(results)
            
            # vik: end
            return content, results
        
        follow_up_questions_prompt = self.follow_up_questions_prompt_content if overrides.get("suggest_followup_questions") else ""
        
        # function to get the prompt for the given search results and generate the answer
        def generate_response(content, results, follow_up_questions_prompt):
            # Allow client to replace the entire prompt, or to inject into the exiting prompt using >>>
            prompt_override = overrides.get("prompt_template")

            if prompt_override is None:
                prompt = self.prompt_prefix.format(follow_up_questions_prompt=follow_up_questions_prompt)
            
            else:
                prompt = prompt_override.format(follow_up_questions_prompt=follow_up_questions_prompt)

            messages_new = self.llm_client.format_prompt(system_prompt=prompt,
                                                     supporting_documents=content,
                                                    chat_history=history)
            completion = self.llm_client.create(messages=messages_new)


            # STEP 3: Generate a contextual and content specific answer using the search results and chat history            
            prompt_txt = self.create_prompt_from_messages(messages=messages_new)
            
            return completion, prompt_txt
        
        # Error handling when prompt is too long
        try:
            # vik: get the search results for the given query
            r = get_search_results(q)

            # vik: get the search results based on the preference to use just the chunks of the content or the entire content of the page
            content, results = get_search_results_content(r, full_content=False)
            
            # vik: get the prompt for the given search results and generate the answer
            completion, prompt = generate_response(content, results, follow_up_questions_prompt)
        # except InvalidRequestError:
        except:
            r = get_search_results(q)
            content, results = get_search_results_content(r, full_content=False)
            completion, prompt = generate_response(content, results, follow_up_questions_prompt)
        # vik: get the groundedness score for the generated response (this later to be added in the UI as well)
        # groundedness_prompt = create_prompt_groundedness(rag_response=completion.choices[0].text, rag_context=prompt)
        # groundedness_completion = openai.Completion.create(
        #     engine=self.chatgpt_deployment, 
        #     prompt=groundedness_prompt, 
        #     temperature=0.0, 
        #     max_tokens=32, 
        #     n=1, 
        #     stop=["<|im_end|>", "<|im_start|>"])
        # groundedness_score = get_int_between_tags("groundedness", groundedness_completion.choices[0].text)
        # print("Groundedness Score: {}".format(groundedness_score))
            
        # vik: get the chat session name for the given chat history and the latest question
        if chat_length in [1, 4, 7, 10, 14]:
            chat_session_name_prompt = self.chat_session_name_prompt.format(chat_history=self.get_chat_history_as_text(history, include_last_turn=True))

            messages = [{'role': 'user', 'content': chat_session_name_prompt}]
            chat_session_name = self.llm_client.create(messages=messages)
            chat_session_name = chat_session_name.replace("\"", "")
        else:
            chat_session_name = ""
 
        return {"data_points": results, "answer": completion,
                "thoughts": f"Searched for:<br>{q}<br><br>Prompt:<br>" + prompt.replace('\n', '<br>'),
                "Chat_Limit": CHAT_LIMIT, "Current_Chat_Length": chat_length,
                "Chat_Session_Name": chat_session_name}
    
    def get_chat_history_as_text(self, history, include_last_turn=True, approx_max_tokens=1000) -> str:
        history_text = ""
        for h in reversed(history if include_last_turn else history[:-1]):
            history_text = """user:""" +"\n" + h["user"] + "\n" + "\n" + """assistant:""" + "\n" + (h.get("bot") if h.get("bot") else "") + "\n" + history_text
            if len(history_text) > approx_max_tokens*4:
                break      
        return history_text
    
    def get_chat_history_for_ChatCompletion(self, history, existing_list=None):
        messages = existing_list if existing_list else []
        for interaction in history:
            if 'user' in interaction:
                messages.append({'role': 'user',
                                 'content': interaction['user']})
            if 'bot' in interaction:
                messages.append({'role': 'assistant',
                                 'content': interaction['bot']})
        return messages
    
    def create_prompt_from_messages(self, messages):
        formatted_text = []
        for message in messages:
            role = message['role'].capitalize()
            content = message['content']
            formatted_text.append(f"{role}: {content}")


        return "\n".join(formatted_text)
