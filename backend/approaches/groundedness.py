import os
import re
# import semantic_kernel as sk
# from semantic_kernel.connectors.ai.open_ai import AzureTextCompletion
from dotenv import load_dotenv
import openai
load_dotenv(dotenv_path=".azure/openai_test/.env")
# function to create the prompt for the evaluation
def create_prompt_groundedness(rag_response, rag_context):
    # System prompt importing from the file "skprompt.txt"
    with open("./backend/approaches/skprompt.txt", "r") as f:
        system_prompt = f.read()
    prompt = system_prompt.format(rag_response=rag_response, rag_context=rag_context)
    return prompt
rag_query = """
What is objective 2.2 about?
"""
rag_response = """
Objective 2.2 is about our environmental sustainability goals. 
"""
rag_context = """
Objective 2.1: Unlock the full capabilities of AI, ML and analytics solutions
Maximize the potential of artificial intelligence (AI) and machine learning (ML) technologies 
through strategic deployment for optimal results in support of the AI and Analytics strategy. 
Ensure AI, ML and analytics solutions leverage the “Responsible AI Framework” to protect 
privacy, reduce bias and align to legislative requirements.
Objective 2.2: Establish a performant data access layer based on business value
Provide standards for a framework, patterns and technology choices that drive a 
consistent, customer-centric approach to easily accessing and using the data applicable to 
various personas in a performant, reliable way that delivers a seamless consumer 
experience.
Objective 2.3: Align and prioritize data investments with business priorities and 
competitive performance
Accelerate delivery of proactive and fit for purpose modern analytic tools aligned to true 
business needs. Drive prioritization of data products to encourage cross functional usage 
across the value chain and to break down silos.
"""
# Parse 
def get_int_between_tags(tag_name: str, text_to_parse: str) -> int:
    pattern = fr"<{tag_name}>\s*(\d+)\s*</{tag_name}>"
    match = re.search(pattern, text_to_parse)
    if match:
        groundedness_number = match.group(1)
        return int(groundedness_number)
    else:
        raise Exception(f"No integer found between tags: {tag_name}")
    
# score = get_int_between_tags("groundedness", evaluation_response.result)
# print(f"Score: {score}")

