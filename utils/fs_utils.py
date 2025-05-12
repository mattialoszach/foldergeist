import os

# Avoid certain types of files (custom preferences)
avoid_types = ["__pycache__", "venv"]

def get_folder_structure(path=None, max_depth=5, curr_depth=0):
    """
    Returns folder structure as recursive dict.
    - path: Starting path (optional). If None, current working directory is being used.
    - max_depth: How deep should function recursively go? (Safety measure - huge trees)
    """

    if path is not None and os.path.exists(path):
        path = os.path.abspath(path)
        
    else:
        path = os.getcwd()

    if curr_depth > max_depth:
        return {"name": os.path.basename(path), "type": "directory", "children": ["... (depth limit reached)"]}

    tree = {"name": os.path.basename(path), "type": "directory", "children": []}

    try:
        for entry in os.listdir(path):
            if entry in avoid_types:
                continue

            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path) and entry[0] != ".":
                tree["children"].append(get_folder_structure(full_path, max_depth, curr_depth + 1))
            else:
                tree["children"].append({
                    "name": entry,
                    "type": "file"
                })
    except PermissionError:
        tree["children"].append({"name": "Permission Denied", "type": "error"})

    return tree

if __name__ == "__main__":
    print("For debugging and testing the function")