from utils.fs_utils import get_folder_structure
from utils.parser import parse_llm_response

class FoldergeistAgent:
    def __init__(self, root_path, chain, max_iterations=2):
        self.root_path = root_path
        self.chain = chain
        self.max_iterations = max_iterations
        self.actions = [None, "read_file"]
    
    def run(self, question):
        for i in range(self.max_iterations):
            folder_structure = get_folder_structure(self.root_path)
            result = self.chain.invoke({"iteration": i, "folder_structure": folder_structure, "question": question}) # Run Pipeline

            parsed_response = parse_llm_response(result)

            ### For Debugging Purposes ###
            #print("###For Debugging###")
            #print(result)
            #print("###\n")
            #print(parsed_response)
            ###

            print(parsed_response["comment"])
            print("\n")

            if "error" in parsed_response or parsed_response["action"] not in self.actions:
                continue

            if parsed_response["action"] == "read_file":
                read_content = self.read_file(parsed_response)
                print(read_content)
            # else if ... further actions

            print("\n")

            if parsed_response["termination"] == True:
                break

            

    def read_file(self, action):
        try:
            with open(action["args"]["path"], "r") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
