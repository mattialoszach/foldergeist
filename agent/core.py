from langchain_ollama.llms import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from .agent import FoldergeistAgent
from .prompt_builder import prompt

model = OllamaLLM(model="llama3", streaming=True, callbacks=[StreamingStdOutCallbackHandler()])

chain = prompt | model

exit_kw = ["/q", "/quit", "/exit"]

def chat():
    print("\033[1;36m==============================\033[0m")
    print("\033[1;32m Foldergeist\033[0m")
    print("\033[90m AI Agent for Folder Management\033[0m")
    print("\033[1;36m==============================\033[0m")

    root_path = input("Please enter your Folder / Path (if you press 'ENTER' I will continue with using your current folder): ")
    agent = FoldergeistAgent(root_path, chain)

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