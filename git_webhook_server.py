import os
import sys
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Define the paths to your Python script and requirements file
SCRIPT_PATH = 'git_webhook_server.py'
REQUIREMENTS_PATH = 'requirements.txt'

# Initialize the process variable
process = None

class RestartHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == os.path.abspath(SCRIPT_PATH):
            print(f'{SCRIPT_PATH} changed. Restarting server...')
            restart_server()
        elif event.src_path == os.path.abspath(REQUIREMENTS_PATH):
            print(f'{REQUIREMENTS_PATH} changed. Installing requirements...')
            install_requirements()

def restart_server():
    global process
    if process is not None:
        process.terminate()
        process.wait()
    process = subprocess.Popen([sys.executable, SCRIPT_PATH])

def install_requirements():
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', REQUIREMENTS_PATH], check=True)

if __name__ == "__main__":
    global process
    process = subprocess.Popen([sys.executable, SCRIPT_PATH])

    event_handler = RestartHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=False)
    observer.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
