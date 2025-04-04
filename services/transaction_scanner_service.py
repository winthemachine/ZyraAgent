import random
import tls_client
import base64
from fake_useragent import UserAgent
from threading import Lock
import time
import concurrent.futures

class TransactionScannerService:
    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.ua = UserAgent(os='linux', browsers=['firefox'])
        self.lock = Lock()
        
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
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.ua.random
        }

    def fetch_page(self, url: str):
        """Fetch a single page of transaction data"""
        retries = 3
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()['data']
                    return {
                        'history': data['history'],
                        'next_page': data.get('next')
                    }
            except Exception as e:
                print(f"Error fetching page on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def scan_transactions(self, contract_address: str, max_threads: int = 5):
        """Scan all transactions for a contract and collect buyer addresses"""
        base_url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contract_address}?limit=100"
        urls = []
        all_transactions = []
        paginator = None
        
        print(f"Collecting transaction pages for {contract_address}...")

        
        while True:
            url = f"{base_url}&cursor={paginator}" if paginator else base_url
            page_data = self.fetch_page(url)
            
            if not page_data:
                break
                
            urls.append(url)
            paginator = page_data.get('next_page')
            
            if paginator:
                print(f"Found page: {base64.b64decode(paginator).decode('utf-8')}")
            else:
                break

        
        print(f"Processing {len(urls)} pages for transactions...")
        buyers = set()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(self.fetch_page, url))

            for future in concurrent.futures.as_completed(futures):
                page_data = future.result()
                if not page_data:
                    continue
                    
                with self.lock:
                    for tx in page_data['history']:
                        if tx['event'] == "buy":
                            transaction = {
                                "wallet": tx['maker'],
                                "tx_hash": tx['tx_hash'],
                                "type": tx['event'],
                                "amount_usd": tx.get('amount_usd'),
                                "timestamp": tx.get('timestamp')
                            }
                            all_transactions.append(transaction)
                            buyers.add(tx['maker'])

        return {
            "contract_address": contract_address,
            "total_buyers": len(buyers),
            "buyer_addresses": list(buyers),
            "transactions": all_transactions
        } 