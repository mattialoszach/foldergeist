from langchain_ollama.llms import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from utils.intro_graphic import intro_ascii
from .agent import FoldergeistAgent
from .prompt_builder import main_prompt, context_prompt, structure_prompt

model = OllamaLLM(model="llama3")

# main_chain = main_prompt | model
chain_dict = {
    "main_chain": main_prompt | model,
    "context_chain": context_prompt | model,
    "structure_chain": structure_prompt | model
}

exit_kw = ["/q", "/quit", "/exit"]

def chat():
    intro_ascii()

    root_path = input("Please enter your Folder / Path (if you press 'ENTER' I will continue with using your current folder): ")
    agent = FoldergeistAgent(root_path, chain_dict)

    print("\033[90mType your question here (or type '/q', '/quit', '/exit' to quit):\n\033[0m")
    while True:

        question = input(">>> ")
        if question.lower() in exit_kw:
            break
        if question.lower()[0] == '/':
            print("\033[90mType your question here (or type '/q', '/quit', '/exit' to quit):\033[0m")
            continue
        
        agent.run(question)

if __name__ == "__main__":
    chat()