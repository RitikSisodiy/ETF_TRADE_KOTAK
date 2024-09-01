from neo_api_client import NeoAPI
from dotenv import load_dotenv
load_dotenv()
import pdb
import os
import time
import pickle
from notify import notify

def send_notification(title, content, image_path,id=100):
    # Construct the termux-notification command
    command = f"termux-notification --title '{title}' --content '{content}' --image-path {image_path} --id {id}"
    
    # Execute the command
    os.system(command)



class NeoClientManager:
    def __init__(self):
        self.client_file = "neoclient.pkl"
        self.client = self.get_neo_client()
        self.content = ""
    def wait_for_order_excution(self,order_id):
        while True:
            history = self.client.order_history(order_id= order_id)['data']
            if history["stat"]=='Ok':
                latest_history = history["data"][0]
                if latest_history["ordSt"]=="rejected":
                    return False
                elif latest_history["ordSt"]=="complete":
                    return True
                notify.notify(f"current order status for {order_id} is:", latest_history["ordSt"],end="\r",update=False)                
                time.sleep(10)
            else:
                return False
    def get_neo_client(self, new=False):
        if new and os.path.isfile(self.client_file):
            os.remove(self.client_file)
        
        if os.path.isfile(self.client_file):
            notify.notify("Loading existing client...")
            self.client = pickle.load(open(self.client_file, 'rb'))
        else:
            notify.notify("Creating new client...")
            self.client = NeoAPI(
                consumer_key=os.getenv("CONSUMER_KEY"),
                consumer_secret=os.getenv("CONSUMER_SECRET"),
                environment=os.getenv("ENV"),
                access_token=None,
                neo_fin_key="neotradeapi"
            )
            notify.notify("Logging in...")
            login_response = self.client.login(mobilenumber=os.getenv("MOBLIE"), password=os.getenv("PASSWORD"))
            print(login_response)
            notify.notify("Completing 2FA...")
            session_response = self.client.session_2fa(OTP=os.getenv("MPIN"))
            print(session_response)
            pickle.dump(self.client, open(self.client_file, 'wb'))
        
        return self.client

    def is_session_expired(self, res):
        notify.notify("Session expired, retrying...", res)
        res = str(res).lower()
        unauthorised_str = [
            "invalid credentials",
            "authentication",
            "2fa process"
        ]
        if any([a in res for a in unauthorised_str]):
            return True
        return False

    def place_order(self, symbol, price, quantity, retry=0):
        sym = f'{symbol}-EQ'
        kw = {
            "exchange_segment": "nse_cm",
            "product": "CNC",
            "price": f"{price}",
            "order_type": "L",
            "quantity": f"{quantity}",
            "validity": "DAY",
            "trading_symbol": sym,
            "transaction_type": "B",
        }
        
        notify.notify(f"Placing order for {symbol}: Price={price}, Quantity={quantity}")
        order = self.client.place_order(**kw)
        
        if order.get("stat") and order["stat"].lower() == "ok":
            notify.notify("Order placed successfully.")
            return True, order
        
        if retry != 0:
            notify.notify("Order failed. Reason:", order)
            return False, order
        else:
            if self.is_session_expired(order):
                retry += 1
                self.get_neo_client(new=True)
                return self.place_order(symbol, price, quantity, retry)
            return False, order
        

    
    def notify(self, message):
        # Simple notification mechanism (can be replaced with actual notifications)
        notify.notify(f"Notification: {message}")
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
if __name__ == "__main__":
    price = 75
    symbol = 'ABSLNN50ET'
    ammount = 1000

    pdb.set_trace()
   
    order = NeoClientManager().place_order(symbol,price,int(ammount/price))
    pdb.set_trace()
    notify.notify(order)

    order_id = "240830000558819"
    client.trade_report(order_id=order_id) 
    client.order_history(order_id = order_id)