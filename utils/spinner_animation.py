import time
import sys
import threading

# Starting thread with argument function
def start_spinner_thread(spinner_function):
    stop_event = threading.Event() # Set to False per default
    spinner_thread = threading.Thread(target=spinner_function, args=(stop_event,))
    spinner_thread.start()
    return stop_event, spinner_thread

# Thinking animation
def display_thinking_spinner(stop_event):
    spinner = ['|', '/', '-', '\\']
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r\033[1;90mThinking {spinner[i % len(spinner)]}\033[0m")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r\033[K")  # Clear line

# Taking action animation
def display_action_spinner(stop_event):
    spinner = ['|', '/', '-', '\\']
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r\033[1;38;5;208mTaking action {spinner[i % len(spinner)]}\033[0m")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r\033[K")  # Clear line

