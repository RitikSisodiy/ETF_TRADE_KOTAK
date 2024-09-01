import os
class Notification:
    def __init__(self):
        self.content = ""
    def notify(self, *args, **kwargs):
        # Simple notification mechanism (can be replaced with actual notifications)
        message = "".join([str(arg) for arg in args])
        print(f"Notification: {message}",**kwargs)
        self.send_notification(
            title='Kotak Neo',
            content=message,
            image_path='./icon.ico'
        )
    
    def send_notification(self,title, content, image_path,id=100):
        # Construct the termux-notification command
        image_path = os.path.abspath(image_path)
        self.content += "\n"+ content
        command = f"termux-notification --title '{title}' --content '{self.content}' --image-path {image_path} --id {id}"
        
        # Execute the command
        os.system(command)
notify = Notification()