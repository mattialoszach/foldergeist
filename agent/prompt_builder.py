from langchain_core.prompts import ChatPromptTemplate

template = """
You are an AI Agent for Folder Structure Management. 
Your name is Foldergeist.

Based on this context, answer the following question:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)