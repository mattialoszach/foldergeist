from utils.fs_utils import get_folder_structure
from utils.parser import parse_llm_response

class FoldergeistAgent:
    def __init__(self, root_path, chain, max_iterations=5):
        self.root_path = root_path
        self.chain = chain
        self.max_iterations = max_iterations
    
    def run(self, question):
        folder_structure = get_folder_structure(self.root_path)
        result = self.chain.invoke({"folder_structure": folder_structure, "question": question}) # Run Pipeline
        print(result)
        print("\n")