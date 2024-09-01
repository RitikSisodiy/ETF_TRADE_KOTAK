import os
import random
class Notification:
    def __init__(self):
        self.content = ""
        self.id = random.randint(0,100000)
    def notify(self, *args,update=True, **kwargs):
        # Simple notification mechanism (can be replaced with actual notifications)
        message = "".join([str(arg) for arg in args])
        print(f"Notification: {message}",**kwargs)
        self.send_notification(
            title='Kotak Neo',
            content=message,
            image_path='./icon.ico',
            update=update
        )
    
    def send_notification(self,title, content, image_path,id=100,update=True):
        # Construct the termux-notification command
        image_path = os.path.abspath(image_path)
        n_content = self.content
        n_content += "\n" + content
        if update:
            self.content = n_content
        command = f"termux-notification --title '{title}' --content '{n_content}' --image-path {image_path} --id {id}"
        
        # Execute the command
        os.system(command)
notify = Notification()