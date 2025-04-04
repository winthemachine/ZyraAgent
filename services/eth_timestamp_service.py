import random
import tls_client
from fake_useragent import UserAgent
import concurrent.futures
import time

class EthTimestampService:
    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.ua = UserAgent(os='linux', browsers=['firefox'])
        
    def randomise(self):
        """Randomize the user agent and headers"""
        self.identifier = random.choice([
            browser for browser in tls_client.settings.ClientIdentifiers.__args__ 
            if browser.startswith(('chrome', 'safari', 'firefox', 'opera'))
        ])
        self.sendRequest = tls_client.Session(
            random_tls_extension_order=True, 
            client_identifier=self.identifier
        )

        self.headers = {
            'Host': 'gmgn.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://gmgn.ai/?chain=eth',  
            'user-agent': self.ua.random
        }

    def get_mint_timestamp(self, contract_address: str):
        """Get contract creation timestamp"""
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/eth/{contract_address}"
        retries = 3

        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    return data['data']['token']['creation_timestamp']
            except Exception as e:
                print(f"Error fetching mint timestamp on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def fetch_trades_page(self, url):
        """Fetch a single page of trades"""
        retries = 3
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Error fetching trades page on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def get_transactions_by_timestamp(self, contract_address: str, start_time: int, end_time: int, max_threads: int = 5):
        """Get all transactions within a time range"""
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/eth/{contract_address}?limit=100"
        urls = []
        all_trades = []
        paginator = None
        
        print(f"Collecting trade pages for {contract_address}...")

        
        while True:
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            page_data = self.fetch_trades_page(url)
            
            if not page_data:
                break
                
            trades = page_data.get('data', {}).get('history', [])
            if not trades or trades[-1]['timestamp'] < start_time:
                break
                
            urls.append(url)
            paginator = page_data['data'].get('next')
            if not paginator:
                break

        
        print(f"Processing {len(urls)} pages for transactions...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(self.fetch_trades_page, url))

            for future in concurrent.futures.as_completed(futures):
                page_data = future.result()
                if not page_data:
                    continue
                    
                trades = page_data.get('data', {}).get('history', [])
                filtered_trades = [
                    trade for trade in trades 
                    if start_time <= trade['timestamp'] <= end_time
                ]
                all_trades.extend(filtered_trades)

        
        processed_trades = []
        for trade in all_trades:
            processed_trade = {
                "wallet": trade.get("maker"),
                "timestamp": trade.get("timestamp"),
                "type": trade.get("event"),
                "amount_usd": trade.get("amount_usd"),
                "tx_hash": trade.get("tx_hash")
            }
            processed_trades.append(processed_trade)

        return {
            "contract_address": contract_address,
            "start_time": start_time,
            "end_time": end_time,
            "total_trades": len(processed_trades),
            "trades": processed_trades
        } 