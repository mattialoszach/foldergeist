import os
import json
from .ollama_model import choose_model

CONFIG_DIR = os.path.expanduser("~/.config/foldergeist")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def create_config():
    """Function for creation of config file"""
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR) # Create config directory, if non existing yet
    
    print(
        "\nWhen using \033[38;5;208mFoldergeist\033[0m, your agent relies on a base model that must be selected. "
        "Your model runs locally via the Ollama service. Make sure Ollama is installed correctly "
        "(for more information visit 'https://ollama.com')\n"
        "Once you've selected a base model, it will be saved in a configuration file located at "
        "\033[1m'~/.config/foldergeist/config.json'\033[0m\n"
        "If you want to change the model later, just update the value of the 'model_name' key "
        "in that file.\n"
        "👉  It is generally recommended to use models like 'llama3:latest'."
    )
    model_name = choose_model()
    config_data = {"model_name": model_name}

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)
    
    print(f"\n↪ Config file created at {CONFIG_FILE}")
    

def load_config():
    """Loads existing configurations"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config_data = json.load(f)
        return config_data.get("model_name")
    else:
        return None

def setup():
    model_name = load_config()

    if model_name == None: # Config file not found
        create_config()
        model_name = load_config() # Config data can now be accessed
    info_model = f"\033[38;5;208m↪ Using model: \033[1m{model_name}\033[0m"
    return info_model, model_name

if __name__ == "__main__":
    setup()