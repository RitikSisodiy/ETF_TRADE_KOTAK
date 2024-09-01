import os
import subprocess
import random

class Notification:
    def __init__(self):
        self.content = ""
        self.id = random.randint(0,100000)
    def notify(self, *args,update=True,print_txt=True, **kwargs):
        # Simple notification mechanism (can be replaced with actual notifications)
        message = "".join([str(arg) for arg in args])
        print_txt and print(f"Notification: {message}",**kwargs)
        self.send_notification(
            title='Kotak Neo',
            content=message,
            image_path='./icon.ico',
            update=update
        )
    
    
    def send_notification(self, title, content, image_path, update=True):
        # Construct the termux-notification command
        image_path = os.path.abspath(image_path)
        n_content = self.content
        n_content += "\n" + content
        if update:
            self.content = n_content
        command = [
            "termux-notification",
            "--title", title,
            "--content", n_content,
            "--image-path", image_path,
            "--id", str(self.id),
            "--alert-once"
        ]
        
        # Execute the command asynchronously
        subprocess.Popen(command)
notify = Notification()