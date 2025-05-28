import os
import shutil
from utils.fs_utils import get_folder_structure
from utils.parser import parse_llm_response
from utils.spinner_animation import start_spinner_thread, display_thinking_spinner, display_action_spinner
from .chat_context import format_chat_context

class FoldergeistAgent:
    def __init__(self, root_path, chain_dict, max_iterations=2):
        self.root_path = root_path
        self.chain_dict = chain_dict
        self.max_iterations = max_iterations
        self.actions = [None, "understand_file", "understand_structure", "rename_path", "change_path", "delete_path", "copy_path"] # Possible actions
        self.chat_context = [] # Input for prompt to remember last response
        self.chat_context_length = 2 # How many past Q&A pairs should be saved
        self.chat_context_max_chars = 1500 # How many chars get saved per question/response regarding Q&A pairs
    
    # Question-Answer Run with potential action(s)
    def run(self, question):
        for i in range(self.max_iterations):
            folder_structure = get_folder_structure(self.root_path) # Tree like folder structure for context

            print("") # Correct spacing

            # Prepare chat history for prompt template and pipeline
            self.chat_context = self.chat_context[-self.chat_context_length:]
            formatted_context = format_chat_context(self.chat_context, self.chat_context_max_chars)

            # Thinking Animation Thread & running main_chain pipeline
            stop_event, spinner_thread = start_spinner_thread(display_thinking_spinner)
            try:
                result = self.chain_dict["main_chain"].invoke({
                    "chat_context": formatted_context,
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
            if parsed_response.get("comment"):
                print("\033[90m<thinking>\n" + parsed_response["comment"] + "\n</thinking>\033[0m")
                print("") # Correct spacing

            # Check if action appropriate
            if "error" in parsed_response or parsed_response["action"] not in self.actions:
                continue
            
            # Run action 1
            if parsed_response["action"] == "understand_file":
                path, result = self.understand_file(parsed_response, question)
                self.chat_context.append({"Question": question, "Response": result}) # Chat history
                print(f" \033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Read file ('{path}') \033[0m\n")
                print(result)
                print("")
            # Run action 2
            elif parsed_response["action"] == "understand_structure":
                result = self.understand_structure(folder_structure, question)
                self.chat_context.append({"Question": question, "Response": result}) # Chat history
                print(result)
                print("")
            # Run action 3
            elif parsed_response["action"] == "rename_path":
                print(f" \033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Rename file/folder ('{parsed_response["args"]["src"]}') \033[0m\n")
                change = self.rename_path(parsed_response)
                if change:
                    self.chat_context.append({"Question": question, "Response": f"Action taken, renamed file ('{parsed_response["args"]["src"]}')"}) # Chat history
                else:
                    self.chat_context.append({"Question": question, "Response": f"Could not rename file ('{parsed_response["args"]["src"]}')"})

                print("")
            # Run action 4
            elif parsed_response["action"] == "change_path":
                print(f" \033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Change path ('{parsed_response["args"]["src"]}') \033[0m\n")
                change = self.change_path(parsed_response)
                if change:
                    self.chat_context.append({"Question": question, "Response": f"Action taken, change path ('{parsed_response["args"]["src"]}')"}) # Chat history
                else:
                    self.chat_context.append({"Question": question, "Response": f"Could not change path ('{parsed_response["args"]["src"]}')"})
                print("")
            # Run action 5
            elif parsed_response["action"] == "delete_path":
                print(f" \033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Delete path ('{parsed_response["args"]["path"]}') \033[0m\n")
                change = self.delete_path(parsed_response)
                if change:
                    self.chat_context.append({"Question": question, "Response": f"Action taken, delete path ('{parsed_response["args"]["path"]}')"}) # Chat history
                else:
                    self.chat_context.append({"Question": question, "Response": f"Could not delete path ('{parsed_response["args"]["path"]}')"})
                print("")
            # Run action 6
            elif parsed_response["action"] == "copy_path":
                print(f" \033[1;48;5;15m ⚙️  \033[0m\033[1;48;5;208m Action - Copy path ('{parsed_response["args"]["src"]}') \033[0m\n")
                change = self.copy_path(parsed_response)
                if change:
                    self.chat_context.append({"Question": question, "Response": f"Action taken, copied path ('{parsed_response["args"]["src"]}')"}) # Chat history
                else:
                    self.chat_context.append({"Question": question, "Response": f"Could not copy path ('{parsed_response["args"]["src"]}')"})
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
    
    # Action 3: Renaming file/folder
    def rename_path(self, action):
        try:
            old_name = os.path.join(self.root_path, action["args"]["src"])
            new_name = os.path.join(self.root_path, action["args"]["dest"])
                
            if not os.path.exists(old_name):
                raise FileNotFoundError(f"Invalid path!")

            print(f"Potential change: \033[38;5;208m\033[1m{old_name} → {new_name}\033[0m")

            confirm_action = ""
            while confirm_action not in ["y", "n"]:
                 confirm_action = input(f"⚠️  Do you want to confirm this action? (y/n): ").lower()

            if confirm_action == "y":
                os.rename(old_name, new_name)
                print(f"\n✅  Success: Renamed \033[38;5;208m\033[1m{old_name} → {new_name}\033[0m")
                return True
            else:
                print("\n❌  Aborting action...")
                return False

        except Exception as e:
            print(f"❗ Error renaming structure: {e}")
            print("Please try again!")
            return False

    # Action 4: Change path
    def change_path(self, action):
        try:
            old_path = os.path.join(self.root_path, action["args"]["src"])
            dest_folder = os.path.join(self.root_path, action["args"]["dest"])
            new_path = os.path.join(dest_folder, os.path.basename(old_path))
                
            if not os.path.exists(old_path):
                raise FileNotFoundError(f"Invalid path!")

            print(f"Potential change: \033[38;5;208m\033[1m{old_path} → {new_path}\033[0m")

            confirm_action = ""
            while confirm_action not in ["y", "n"]:
                 confirm_action = input(f"⚠️  Do you want to confirm this action? (y/n): ").lower()

            if confirm_action == "y":
                os.rename(old_path, new_path)
                print(f"\n✅  Success: Changed path \033[38;5;208m\033[1m{old_path} → {new_path}\033[0m")
                return True
            else:
                print("\n❌  Aborting action...")
                return False

        except Exception as e:
            print(f"❗ Error renaming structure: {e}")
            print("Please try again!")
            return False
        
    # Action 5: Delete path
    def delete_path(self, action):
        try:
            target_path = os.path.join(self.root_path, action["args"]["path"])

            if not os.path.exists(target_path):
                raise FileNotFoundError("Invalid path!")

            print(f"Potential delete: \033[38;5;196m\033[1m{target_path}\033[0m")

            confirm_action = ""
            while confirm_action not in ["y", "n"]:
                confirm_action = input(f"⚠️  Do you want to permanently delete this path? (y/n): ").lower()

            if confirm_action == "y":
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                else:
                    os.remove(target_path)
                print(f"\n🗑️  Deleted: \033[38;5;196m\033[1m{target_path}\033[0m")
                return True
            else:
                print("\n❌  Aborting deletion...")
                return False

        except Exception as e:
            print(f"❗ Error deleting path: {e}")
            print("Please try again!")
            return False
        
    # Action 6: Copy path
    def copy_path(self, action):
        try:
            src_path = os.path.join(self.root_path, action["args"]["src"])
            dest_folder = os.path.join(self.root_path, action["args"]["dest"])
            dest_path = os.path.join(dest_folder, os.path.basename(src_path))

            if not os.path.exists(src_path):
                raise FileNotFoundError("Invalid source path!")

            print(f"Potential copy: \033[38;5;39m\033[1m{src_path} → {dest_path}\033[0m")

            confirm_action = ""
            while confirm_action not in ["y", "n"]:
                confirm_action = input(f"⚠️  Do you want to confirm this copy action? (y/n): ").lower()

            if confirm_action == "y":
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dest_path)
                else:
                    os.makedirs(dest_folder, exist_ok=True)
                    shutil.copy2(src_path, dest_path)
                print(f"\n✅  Success: Copied \033[38;5;39m\033[1m{src_path} → {dest_path}\033[0m")
                return True
            else:
                print("\n❌  Aborting copy...")
                return False

        except Exception as e:
            print(f"❗ Error copying path: {e}")
            print("Please try again!")
            return False