import json
import time
import random
import tls_client
from fake_useragent import UserAgent

class EarlyBuyersService:
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
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.ua.random
        }

    def fetch_early_buyers(self, contract_address: str, limit: int = 20):
        """Fetch early buyers data for a single contract address"""
        url = f"https://gmgn.ai/vas/api/v1/token_trades/sol/{contract_address}?revert=true&app_lang=en-US&from_app=gmgn"
        retries = 3

        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:
                    data = response.json().get('data', {}).get('history', [])
                    if isinstance(data, list):
                        # Filter buy events and exclude creators, then limit results
                        buyers = [
                            item for item in data 
                            if item.get('event') == "buy" and 
                            "creator" not in item.get('maker_token_tags', [])
                        ]
                        return buyers[:limit]
            except Exception as e:
                print(f"Error fetching data on attempt {attempt + 1}: {e}")
                
                try:
                    import cloudscraper
                    scraper = cloudscraper.create_scraper()
                    response = scraper.get(url, headers=self.headers)
                    if response.status_code == 200:
                        data = response.json().get('data', {}).get('history', [])
                        if isinstance(data, list):
                            buyers = [
                                item for item in data 
                                if item.get('event') == "buy" and 
                                "creator" not in item.get('maker_token_tags', [])
                            ]
                            return buyers[:limit]
                except Exception as e:
                    print(f"Backup scraper failed: {e}")
            time.sleep(1)
        return []

    def get_early_buyers(self, contract_addresses, limit: int = 20):
        """Get early buyers for multiple contract addresses"""
        if isinstance(contract_addresses, str):
            contract_addresses = [addr.strip() for addr in contract_addresses.split(',')]
        
        all_buyers = []
        for address in contract_addresses:
            buyers = self.fetch_early_buyers(address, limit)
            all_buyers.extend(buyers)
            
        return all_buyers 