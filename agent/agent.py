from utils.fs_utils import get_folder_structure
from utils.parser import parse_llm_response

class FoldergeistAgent:
    def __init__(self, root_path, chain_dict, max_iterations=2):
        self.root_path = root_path
        self.chain_dict = chain_dict
        self.max_iterations = max_iterations
        self.actions = [None, "understand_file"]
    
    def run(self, question):
        for i in range(self.max_iterations):
            folder_structure = get_folder_structure(self.root_path)
            result = self.chain_dict["main_chain"].invoke({"iteration": i, "folder_structure": folder_structure, "question": question}) # Run Pipeline

            parsed_response = parse_llm_response(result)

            ### For Debugging Purposes ###
            #print("###For Debugging###")
            #print(result)
            #print("###\n")
            #print(parsed_response)
            ###
            if parsed_response["comment"]:
                print("\n")
                print("<thinking>\n" + parsed_response["comment"] + "\n</thinking>")
                print("\n")

            if "error" in parsed_response or parsed_response["action"] not in self.actions:
                continue

            if parsed_response["action"] == "understand_file":
                path, result = self.understand_file(parsed_response, question)
                print(f" \033[1m\033[48;5;208m🔧 Action - Read file ('{path}')\033[0m\n")
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
        
    def understand_file(self, action, question):
        try:
            path, read_content = self.read_file(action)
            result = self.chain_dict["context_chain"].invoke({"file_path": path, "file_content": read_content, "question": question})
            return path, result
        except Exception as e:
            return "", f"Error understanding file: {e}"
