from neo_api_client import NeoAPI
from dotenv import load_dotenv
load_dotenv()
import pdb
import os
import pickle

class NeoClientManager:
    def __init__(self):
        self.client_file = "neoclient.pkl"
        self.client = self.get_neo_client()
    def wait_for_order_excution(self,order_id):
        while True:
            history = self.client.order_history(order_id= order_id)['data']
            if history["stat"]=='Ok':
                latest_history = history["data"][0]
                if latest_history["ordSt"]=="rejected":
                    self.notify(f"Your order id {order_id} is rejected \n Reason: {latest_history['rejRsn']}")
                    return False
                elif latest_history["ordSt"]=="complete":
                    self.notify(f"Your order id {order_id} is completed")
                    return True
                print(f"current order status for {order_id} is:", latest_history["ordSt"],end="\r")                
                time.sleep(10)
            else:
                return False
    def get_neo_client(self, new=False):
        if new and os.path.isfile(self.client_file):
            os.remove(self.client_file)
        
        if os.path.isfile(self.client_file):
            print("Loading existing client...")
            self.client = pickle.load(open(self.client_file, 'rb'))
        else:
            print("Creating new client...")
            self.client = NeoAPI(
                consumer_key=os.getenv("CONSUMER_KEY"),
                consumer_secret=os.getenv("CONSUMER_SECRET"),
                environment=os.getenv("ENV"),
                access_token=None,
                neo_fin_key="neotradeapi"
            )
            print("Logging in...")
            login_response = self.client.login(mobilenumber=os.getenv("MOBLIE"), password=os.getenv("PASSWORD"))
            print(login_response)
            print("Completing 2FA...")
            session_response = self.client.session_2fa(OTP=os.getenv("MPIN"))
            print(session_response)
            pickle.dump(self.client, open(self.client_file, 'wb'))
        
        return self.client

    def is_session_expired(self, res):
        print("Session expired, retrying...", res)
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
        
        print(f"Placing order for {symbol}: Price={price}, Quantity={quantity}")
        order = self.client.place_order(**kw)
        
        if order.get("stat") and order["stat"].lower() == "ok":
            print("Order placed successfully.")
            self.notify(f"Order placed successfully: {order}")
            return True, order
        
        if retry != 0:
            print("Order failed. Reason:", order)
            self.notify(f"Order failed: {order}")
            return False, order
        else:
            if self.is_session_expired(order):
                retry += 1
                self.get_neo_client(new=True)
                return self.place_order(symbol, price, quantity, retry)
            return False, order
        


    def notify(self, message):
        # Simple notification mechanism (can be replaced with actual notifications)
        print(f"Notification: {message}")

if __name__ == "__main__":
    price = 75
    symbol = 'ABSLNN50ET'
    ammount = 1000

    pdb.set_trace()
   
    order = NeoClientManager().place_order(symbol,price,int(ammount/price))
    pdb.set_trace()
    print(order)

    order_id = "240830000558819"
    client.trade_report(order_id=order_id) 
    client.order_history(order_id = order_id)