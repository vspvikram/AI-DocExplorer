import openai
from openai import OpenAI
import os
print(os.listdir())

# from ...llm_services import LlmServiceClass
from services.llm_services import LlmServiceClass


class OpenAIChatService(LlmServiceClass):
    def __init__(self, config):
        super().__init__(config, name="OpenAIChatService")
        self.client = OpenAI()
        self.model_name = config['llm_model_name']
        if "llm_api_key" not in config:
            raise "Invalid config: Does not have the api key"

    def create(self, messages, model = None, **kwargs):
        """Input parameters:
        messages: list of dict with roles and their content
        model: default gpt-3.5-turbo if not given any
        kwargs: (optional) default values as follows
                "temperature": 1,
                "max_tokens": 256,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
        """
        model_name = model if model else self.model_name
        try:
            openai.api_key = self.config['llm_api_key']
            # Default parameters for the chat completion
            params = {
                "model": model_name or "gpt-3.5-turbo",
                "messages": messages,
                "temperature": 1,
                "max_tokens": 256,
                "top_p": 1,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            # Update the default params with any other specified parameters
            params.update(kwargs)

            response = self.client.chat.completions.create(**params)
            # response = openai.ChatCompletion.create(
            #     model = model or "gpt-4-turbo",
            #     messages=messages,
            #     # Add more parameters as needed
            # )
            return response.choices[0].message.content if response.choices else None
        except Exception as e:
            print("Unable to generate ChatCompletion response")
            print(f"Exception: {e}")
            return e

    def format_prompt(self, chat_history, system_prompt = None, supporting_documents = None):
        """
        Input params:
        chat_history (list of dict): A list of dictionaries, each containing user and bot messages. E.g.
                                [{'user': "what is the highest...", 'bot': "The highest...."},
                                {'user': "tell me more about...", 'bot': "Sure, here is..."},
                                {'user': "current question..."}]
        system_prompt: system prompt (Optional)
        supporting_documents: supporting_documents (Optional)
        """
        messages = []

        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})

        # Add supporting documents if provided
        if supporting_documents:
            messages.append({'role': 'system', 'content': f"Supporting Documents:\n{supporting_documents}"})

        # Format the chat history into messages
        messages.extend(self.get_chat_history_for_ChatCompletion(chat_history))

        return messages

    def get_chat_history_for_ChatCompletion(self, history):
        messages = []
        for interaction in history:
            if 'user' in interaction:
                messages.append({'role': 'user', 'content': interaction['user']})
            if 'bot' in interaction:
                messages.append({'role': 'assistant', 'content': interaction['bot']})
        return messages

##################################################
    
# if __name__ == "__main__":
#     system_prompt = """You are an assistant that helps users with questions. You will be given some documents for your context within the tags below. And the user and assistant chat history separately. Use all this information to generate a response for the latest user question."""
#     results = [
#             "Mars_Exploration_History: Mars exploration has been an ongoing endeavor since the early 20th century, with missions ranging from flybys and orbiters to rovers and landers. ",
            
#             "James_Webb_Space_Telescope: The James Webb Space Telescope (JWST) is a powerful infrared telescope launched in December 2021. JWST is designed to observe the universe's earliest stars and galaxies, study the formation of stars and planetary systems, and investigate the atmospheres of exoplanets. Early observations have already revealed groundbreaking discoveries, including the faintest light ever detected from a galaxy and the presence of water vapor in the atmosphere of an exoplanet.",
            
#             "Space_Colonization: Space colonization is the idea of establishing permanent human settlements beyond Earth. Potential destinations include the Moon, Mars, and other planets or moons in our solar system. Proponents of space colonization argue that it would offer humanity a way to escape environmental threats on Earth, access new resources, and expand our knowledge of the universe. However, space colonization faces significant challenges, including the high cost, technological hurdles, and potential health risks for humans living in space.",
#         ]
#     docs = "\n\n".join(results)
#     history = [{'user': "What are some of the major achievements in Mars exploration?"}]

#     config = {"llm_api_key": ""}

#     openai_model = OpenAIChatService(config=config)
#     messages = openai_model.format_prompt(system_prompt=system_prompt,
#                                             supporting_documents=docs, chat_history=history)
#     response = openai_model.create(messages=messages)

#     print(response)

