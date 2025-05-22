from utils.fs_utils import get_folder_structure
from utils.parser import parse_llm_response
from utils.spinner_animation import start_spinner_thread, display_spinner

class FoldergeistAgent:
    def __init__(self, root_path, chain_dict, max_iterations=2):
        self.root_path = root_path
        self.chain_dict = chain_dict
        self.max_iterations = max_iterations
        self.actions = [None, "understand_file", "understand_structure"]
        self.chat_context = "" # Input for prompt to remember last response
    
    def run(self, question):
        for i in range(self.max_iterations):
            folder_structure = get_folder_structure(self.root_path) # Tree like folder structure for context

            # Thinking Animation Thread
            stop_event, spinner_thread = start_spinner_thread()
            try:
                result = self.chain_dict["main_chain"].invoke({
                    "chat_context": self.chat_context,
                    "iteration": i,
                    "folder_structure": folder_structure,
                    "question": question
                })
            finally:
                stop_event.set()
                spinner_thread.join()

            # Parsing LLM Result
            parsed_response = parse_llm_response(result) # Main Action Decision (JSON Format)

            ### For Debugging Purposes ###
            print("###For Debugging###")
            print(result)
            print("###\n")
            print(parsed_response)
            ###

            if parsed_response["comment"]:
                print("\n")
                print("<thinking>\n" + parsed_response["comment"] + "\n</thinking>")
                print("\n")
                self.chat_context = parsed_response["comment"]

            if "error" in parsed_response or parsed_response["action"] not in self.actions:
                continue

            if parsed_response["action"] == "understand_file":
                path, result = self.understand_file(parsed_response, question)
                self.chat_context = result[-300:] if len(result) > 300 else result
                print(f"\033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Read file ('{path}') \033[0m\n")
                print(result)
                print("\n")
            elif parsed_response["action"] == "understand_structure":
                result = self.understand_structure(folder_structure, question)
                print(result)
                print("\n")
            # elif ... further actions

            if parsed_response["termination"] == True:
                break

            

    def read_file(self, action):
        try:
            with open(action["args"]["path"], "r") as f:
                return action["args"]["path"], f.read()
        except Exception as e:
            return "", f"Error reading file: {e}"
    
    # Action
    def understand_file(self, action, question):
        try:
            path, read_content = self.read_file(action)
            result = self.chain_dict["context_chain"].invoke({"chat_context": self.chat_context, "file_path": path, "file_content": read_content, "question": question})
            return path, result
        except Exception as e:
            return "", f"Error understanding file: {e}"

    def understand_structure(self, folder_structure, question):
        try:
            result = self.chain_dict["structure_chain"].invoke({"chat_context": self.chat_context, "folder_structure": folder_structure, "question": question})
            return result
        except Exception as e:
            return "", f"Error understanding structure: {e}"