import os
from langchain_ollama.llms import OllamaLLM
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from utils.intro_graphic import intro_ascii
from config.config import setup
from .agent import FoldergeistAgent
from .prompt_builder import main_prompt, context_prompt, structure_prompt

# Make config file setup with model preferences
info_model, model_name = setup()
model = OllamaLLM(model=model_name)

# Dict with all possible pipelines
chain_dict = {
    "main_chain": main_prompt | model,
    "context_chain": context_prompt | model,
    "structure_chain": structure_prompt | model
}

exit_kw = ["/q", "/quit", "/exit"] # Keywoards for exit

# Chat Interface
def chat():
    intro_ascii()

    # Check if valid path and display path
    root_path = ""

    for attempt in range(2):
        root_path = input("Please enter your Folder / Path (if you \033[38;5;208mpress 'ENTER'\033[0m I will continue with using your \033[38;5;208mcurrent folder\033[0m): ").strip()

        if root_path == "":
            print("Using current working directory...")
            root_path = os.getcwd()
            print(f"\033[38;5;208m↪ Working with root path '\033[1m{root_path}\033[0m'")
            break

        if os.path.exists(root_path):
            print(f"\033[38;5;208m↪ Working with root path '\033[1m{root_path}\033[0m'")
        else:
            print(f"❌ The path '{root_path}' wasn't found.")

            if attempt == 0:
                try_again = input("Do you want to try again? (y/n): ").strip().lower()
                if try_again != "y":
                    print("👋 Exiting...")
                    return None
            else:
                print("🚫 Second attempt failed. Exiting...")
                return None

    print(info_model) # Information about model in use

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