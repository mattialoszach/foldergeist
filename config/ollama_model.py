import subprocess
import json

def list_installed_models():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, check=True)
        lines = result.stdout.strip().splitlines()
        model_names = [line.split()[0] for line in lines[1:]]
        return model_names
    
    except Exception as e:
        print(f"❌ Error fetching models: {e}")
        return []

def choose_model():
    models = list_installed_models()
    if not models:
        print(
            "⚠️  No Ollama models found. Please install a model first.\n"
            "Make sure you have models installed by running:\n"
            "  👉  ollama list\n"
            "If this error message still appears, you can manually update the configuration file:\n"
            "  ~/.config/foldergeist/config.json\n"
            "Set the value of the 'model_name' key to your desired model (e.g. 'llama3')."
        )
        exit(1)
    
    print("\n\033[1mAvailable Ollama models on your system:\033[0m\n")
    for i, m in enumerate(models):
        print(f"    [{i + 1}] {m}")

    while True:
        choice = input(f"\nSelect a model [1-{len(models)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(models):
            return models[int(choice) - 1]
        else:
            print("Invalid selection. Please enter a number.")

if __name__ == "__main__":
    print(list_installed_models())