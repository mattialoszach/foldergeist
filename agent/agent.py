import os
from utils.fs_utils import get_folder_structure
from utils.parser import parse_llm_response
from utils.spinner_animation import start_spinner_thread, display_thinking_spinner, display_action_spinner

class FoldergeistAgent:
    def __init__(self, root_path, chain_dict, max_iterations=2):
        self.root_path = root_path
        self.chain_dict = chain_dict
        self.max_iterations = max_iterations
        self.actions = [None, "understand_file", "understand_structure"] # Possible actions
        self.chat_context = "" # Input for prompt to remember last response
    
    # Question-Answer Run with potential action(s)
    def run(self, question):
        for i in range(self.max_iterations):
            folder_structure = get_folder_structure(self.root_path) # Tree like folder structure for context

            print("") # Correct spacing

            # Thinking Animation Thread & running main_chain pipeline
            stop_event, spinner_thread = start_spinner_thread(display_thinking_spinner)
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

            # To-Do: Remove Debugging
            ### For Debugging Purposes ###
            #print("###For Debugging###")
            #print(result)
            #print("###\n")
            #print(parsed_response)
            ###

            # Thinking process from main_chain pipeline
            if parsed_response["comment"]:
                print("\033[90m<thinking>\n" + parsed_response["comment"] + "\n</thinking>\033[0m")
                print("") # Correct spacing
                self.chat_context = parsed_response["comment"]

            # Check if action appropriate
            if "error" in parsed_response or parsed_response["action"] not in self.actions:
                continue
            
            # Run action 1
            if parsed_response["action"] == "understand_file":
                path, result = self.understand_file(parsed_response, question)
                self.chat_context = result[-300:] if len(result) > 300 else result
                print(f" \033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Read file ('{path}') \033[0m\n")
                print(result)
                print("")
            # Run action 2
            elif parsed_response["action"] == "understand_structure":
                result = self.understand_structure(folder_structure, question)
                print(result)
                print("")
            # elif ... further actions

            # Check for termination condition
            if parsed_response["termination"] == True:
                break
    
    # Helper function - get file content
    def read_file(self, action):
        try:
            relative_path = action["args"]["path"]
            full_path = os.path.join(self.root_path, relative_path)
            with open(full_path, "r") as f:
                return relative_path, f.read()
        except Exception as e:
            return "", f"Error reading file: {e}"
    
    # Action 1: Understanding file (using context_chain)
    def understand_file(self, action, question):
        try:
            path, read_content = self.read_file(action)

            # Taking action animation & running context_chain pipeline
            stop_event, spinner_thread = start_spinner_thread(display_action_spinner)
            try:
                result = self.chain_dict["context_chain"].invoke({
                    "chat_context": self.chat_context,
                    "file_path": path, 
                    "file_content": read_content, 
                    "question": question
                })
            finally:
                stop_event.set()
                spinner_thread.join()

            return path, result
        except Exception as e:
            return "", f"Error understanding file: {e}"

    # Action 2: Understanding folder structure (using structure_chain)
    def understand_structure(self, folder_structure, question):
        try:
            # Taking action animation & running structure_chain pipeline
            stop_event, spinner_thread = start_spinner_thread(display_action_spinner)
            try:
                result = self.chain_dict["structure_chain"].invoke({
                    "chat_context": self.chat_context,
                    "folder_structure": folder_structure, 
                    "question": question
                })
            finally:
                stop_event.set()
                spinner_thread.join()

            return result
        except Exception as e:
            return "", f"Error understanding structure: {e}"