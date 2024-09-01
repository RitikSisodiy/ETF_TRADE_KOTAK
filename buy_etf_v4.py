import pandas as pd
import pdb
import yfinance as yf
from datetime import datetime, timedelta
from tqdm import tqdm
import os
import json
from trade_api import NeoClientManager
from notify import notify
# File to persist accumulated investment
accumulated_investment_file = "accumulated_investment.json"

# Function to fetch historical data
def fetch_data(etf_list, start_date, end_date):
    data = {}
    for etf in tqdm(etf_list):
        data[etf] = yf.download(etf, start=start_date, end=end_date, progress=False)
    return data

# Function to calculate the 20-day moving average and percentage drop
def calculate_metrics(data):
    results = {}
    for etf, df in data.items():
        df['20-DMA'] = df['Close'].rolling(window=20).mean()
        current_price = df['Close'].iloc[-1]
        moving_average = df['20-DMA'].iloc[-1]
        if pd.notna(moving_average):
            percentage_drop = ((current_price - moving_average) / moving_average) * 100
            results[etf] = percentage_drop
    return results

# Function to get the ETF to buy, excluding recently bought ETFs unless criteria are met
def get_etf_to_buy(metrics, last_investments, min_drop=2, additional_drop=2.5):
    sorted_metrics = sorted(metrics.items(), key=lambda x: x[1], reverse=False)
    
    for etf, percentage_drop in sorted_metrics:
        last_investment_date, last_investment_drop = last_investments.get(etf, (None, None))
        if last_investment_date:
            days_since_last_investment = (datetime.today() - last_investment_date).days
            if days_since_last_investment <= 5 and percentage_drop > (last_investment_drop - additional_drop):
                continue
        if percentage_drop <= -min_drop:
            return etf, percentage_drop
    
    return None

# Function to log buy history and update the last_investments dictionary
def log_buy_history(etf, percentage_drop, investment_amount, num_shares, last_investments):
    buy_history_file = "buy_history_v4.csv"
    current_date = datetime.today().strftime('%Y-%m-%d')
    
    if not os.path.exists(buy_history_file):
        with open(buy_history_file, 'w') as f:
            f.write("Date,ETF,Percentage Drop,Investment Amount,Num Shares\n")
    
    with open(buy_history_file, 'a') as f:
        f.write(f"{current_date},{etf},{percentage_drop:.2f},{investment_amount:.2f},{num_shares}\n")
    
    last_investments[etf] = (datetime.today(), percentage_drop)

# Function to load accumulated investment from a file
def load_accumulated_investment():
    if os.path.exists(accumulated_investment_file):
        with open(accumulated_investment_file, 'r') as f:
            data = json.load(f)
            return data.get('accumulated_investment', 0)
    return 0

# Function to save accumulated investment to a file
def save_accumulated_investment(amount):
    with open(accumulated_investment_file, 'w') as f:
        json.dump({'accumulated_investment': amount}, f)

# Example workflow
def main():
    etf_list = ["ABSLBANETF.NS", "ABSLNN50ET.NS", "ALPHA.NS", "ALPHAETF.NS", "ALPL30IETF.NS", "AUTOBEES.NS", "AUTOIETF.NS", "AXISGOLD.NS", "AXISILVER.NS", "AXISNIFTY.NS", "AXISTECETF.NS", "BANKBEES.NS", "BANKBETF.NS", "BANKIETF.NS", "BANKNIFTY1.NS", "BFSI.NS", "BSE500IETF.NS", "BSLGOLDETF.NS", "BSLNIFTY.NS", "COMMOIETF.NS", "CONSUMBEES.NS", "CONSUMIETF.NS", "CPSEETF.NS", "DIVOPPBEES.NS", "EQUAL50ADD.NS", "FINIETF.NS", "FMCGIETF.NS", "GOLDBEES.NS", "GOLDCASE.NS", "GOLDETF.NS", "GOLDETFADD.NS", "GOLDIETF.NS", "GOLDSHARE.NS", "HDFCBSE500.NS", "HDFCGOLD.NS", "HDFCLOWVOL.NS", "HDFCMID150.NS", "HDFCMOMENT.NS", "HDFCNEXT50.NS", "HDFCNIF100.NS", "HDFCNIFBAN.NS", "HDFCNIFIT.NS", "HDFCNIFTY.NS", "HDFCPSUBK.NS", "HDFCPVTBAN.NS", "HDFCSENSEX.NS", "HDFCSILVER.NS", "HDFCSML250.NS", "HEALTHIETF.NS", "HEALTHY.NS", "HNGSNGBEES.NS", "ICICIB22.NS", "INFRABEES.NS", "INFRAIETF.NS", "IT.NS", "ITBEES.NS", "ITETF.NS", "ITETFADD.NS", "ITIETF.NS", "JUNIORBEES.NS", "KOTAKGOLD.NS", "KOTAKSILVE.NS", "LOWVOLIETF.NS", "MAFANG.NS", "MAHKTECH.NS", "MAKEINDIA.NS", "MASPTOP50.NS", "MID150BEES.NS", "MIDCAP.NS", "MIDCAPETF.NS", "MIDCAPIETF.NS", "MIDQ50ADD.NS", "MIDSELIETF.NS", "MNC.NS", "MOHEALTH.NS", "MOM100.NS", "MOM30IETF.NS", "MOMENTUM.NS", "MOMOMENTUM.NS", "MON100.NS", "MONIFTY500.NS", "MONQ50.NS", "MOREALTY.NS", "MOSMALL250.NS", "MOVALUE.NS", "NEXT50IETF.NS", "NIF100BEES.NS", "NIF100IETF.NS", "NIFITETF.NS", "NIFMID150.NS", "NIFTY1.NS", "NIFTY50ADD.NS", "NIFTYBEES.NS", "NIFTYETF.NS", "NIFTYIETF.NS", "NIFTYQLITY.NS", "NV20.NS", "NV20BEES.NS", "NV20IETF.NS", "PHARMABEES.NS", "PSUBANK.NS", "PSUBNKBEES.NS", "PSUBNKIETF.NS", "PVTBANIETF.NS", "PVTBANKADD.NS", "QGOLDHALF.NS", "SBIETFCON.NS", "SBIETFIT.NS", "SBIETFPB.NS", "SENSEXETF.NS", "SETFGOLD.NS", "SETFNIF50.NS", "SETFNIFBK.NS", "SETFNN50.NS", "SILVER.NS", "SILVERADD.NS", "SILVERBEES.NS", "SILVERETF.NS", "SILVERIETF.NS", "SILVRETF.NS", "SMALLCAP.NS", "TATAGOLD.NS", "TATSILV.NS", "TECH.NS", "TNIDETF.NS", "UTIBANKETF.NS", "UTINEXT50.NS", "UTINIFTETF.NS", "UTISENSETF.NS"]
    end_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')
    
    daily_investment_amount = 1000

    accumulated_investment = load_accumulated_investment() or daily_investment_amount
    
    last_investments = {}

    data = fetch_data(etf_list, start_date, end_date)
    
    metrics = calculate_metrics(data)
    
    etf_to_buy = get_etf_to_buy(metrics, last_investments)
    
    if etf_to_buy:
        etf, percentage_drop = etf_to_buy
        current_price = data[etf]['Close'].iloc[-1]
        num_shares = int(accumulated_investment // current_price)
        investment_amount = num_shares * current_price
        etf = etf.split(".")[0]
        if num_shares > 0:
            notify.notify(f"ETF to Buy: {etf}, Percentage Drop: {percentage_drop:.2f}%, Shares: {num_shares}, Investment: {investment_amount:.2f}")
            client= NeoClientManager()
            order_success,order = client.place_order(etf,current_price,num_shares)
            if order_success:
                client.wait_for_order_excution(order["nOrdNo"])
                log_buy_history(etf, percentage_drop, investment_amount, num_shares, last_investments)
                accumulated_investment = daily_investment_amount
        else:
            notify.notify(f"Not enough funds to buy at least one share of {etf}. Accumulating funds for the next day.")
            accumulated_investment += daily_investment_amount
    else:
        notify.notify("No suitable ETF to buy today. Accumulating funds for the next day.")
        accumulated_investment += daily_investment_amount
    
    save_accumulated_investment(accumulated_investment)

if __name__ == "__main__":
    main()
