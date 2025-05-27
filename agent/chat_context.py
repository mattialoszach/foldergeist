def format_chat_context(chat_context, chat_context_max_chars):
    formatted = ""
    for entry in chat_context:
        q = entry["Question"][:chat_context_max_chars]
        a = entry["Response"][-chat_context_max_chars:]
        formatted += f"[Q] {q}\n[A] {a}\n\n"
    return formatted.strip()

if __name__ == "__main__":
    chat_history = [
        {"Question": "What is main.py?", "Response": "main.py has..."},
        {"Question": "Rename main.py", "Response": "rename_path: src: main.py, dest: main_old.py"}
    ]

    print(format_chat_context(chat_history, 1000))