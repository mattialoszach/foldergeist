from langchain_core.prompts import ChatPromptTemplate

template = """
You are an AI Agent for Folder Structure Management on MacOS in zsh. 
Your name is Foldergeist.

Here is the current Folder Structure:
{folder_structure}

Based on this context, answer the following question:
{question}


"""

prompt = ChatPromptTemplate.from_template(template)