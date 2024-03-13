import requests
# from ...llm_services import LlmServiceClass
from backend.services.llm_services import LlmServiceClass

class HuggingfaceTinyLlama(LlmServiceClass):
    def __init__(self, config):
        super().__init__(config, name="HuggingfaceTinyLlama")
        self.api_url = config['api_url']
        self.headers = {"Authorization": f"Bearer {config['api_key']}"}

    def query(self, prompt):
        response = requests.post(self.api_url, headers=self.headers, json={"inputs": prompt})
        return response.json()
    
    def format_prompt(self, system_prompt, supporting_documents, chat_history):#chat_history, system_prompt = None, supporting_documents
        """
        Formats the system prompt, supporting documents, and chat history into a single prompt.
        
        Args:
            system_prompt (str): The initial system message describing the assistant's capabilities.
            supporting_documents (str): Text from supporting documents relevant to the conversation.
            history (list of dict): A list of dictionaries, each containing user and bot messages. E.g.
                                [{'user': "what is the highest...", 'bot': "The highest...."},
                                {'user': "tell me more about...", 'bot': "Sure, here is..."},
                                {'user': "current question..."}]

        Returns:
            str: A formatted prompt string ready to be sent to the LLM.
        """
        # Format the system prompt
        formatted_system_prompt = f"<system>{system_prompt}</system>\n"
        
        # Format supporting documents
        formatted_docs = f"<SupportingDocuments>{supporting_documents}</SupportingDocuments>\n"
        
        # Format chat history
        formatted_history = "<dialogue>"
        for exchange in chat_history:
            user_prompt = f"User: {exchange.get('user', '')}\n"
            bot_response = f"Assistant: {exchange.get('bot', '')}\n" if 'bot' in exchange else ""
            formatted_history += user_prompt + bot_response
        formatted_history += "</dialogue>"
        
        # Combine all parts
        final_prompt = formatted_system_prompt + formatted_docs + formatted_history
        return final_prompt
    
system_prompt = """You are an assistant that helps users with questions. You will be given some documents for your context within the tags "SupportingDocument" html tags below. And the user and assistant chat history between the html tags marked as "dialogue". The user message is mentioned between html tags "User" and the assistant generated previous responses between "Assistant" html tags. If the chat history only has "User" question then "Assistant" tags will not be present as it first question. """
results = [
        "Mars_Exploration_History: Mars exploration has been an ongoing endeavor since the early 20th century, with missions ranging from flybys and orbiters to rovers and landers. ",
        
        "James_Webb_Space_Telescope: The James Webb Space Telescope (JWST) is a powerful infrared telescope launched in December 2021. JWST is designed to observe the universe's earliest stars and galaxies, study the formation of stars and planetary systems, and investigate the atmospheres of exoplanets. Early observations have already revealed groundbreaking discoveries, including the faintest light ever detected from a galaxy and the presence of water vapor in the atmosphere of an exoplanet.",
        
        "Space_Colonization: Space colonization is the idea of establishing permanent human settlements beyond Earth. Potential destinations include the Moon, Mars, and other planets or moons in our solar system. Proponents of space colonization argue that it would offer humanity a way to escape environmental threats on Earth, access new resources, and expand our knowledge of the universe. However, space colonization faces significant challenges, including the high cost, technological hurdles, and potential health risks for humans living in space.",
    ]
docs = "\n\n".join(results)
history = [{'user': "What are some of the major achievements in Mars exploration?"}]

config = {"api_url": "https://api-inference.huggingface.co/models/TinyLlama/TinyLlama-1.1B-Chat-v1.0",
          "api_key": ""}

llma_model = HuggingfaceTinyLlama(config=config)
prepared_prompt = llma_model.format_prompt(system_prompt=system_prompt,
                                           supporting_documents=docs, chat_history=history)

response = llma_model.query(prompt=prepared_prompt)
print(response)