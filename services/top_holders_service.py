import json
import time
import random
import tls_client
from fake_useragent import UserAgent

class TopHoldersService:
    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.ua = UserAgent(os='linux', browsers=['firefox'])
        
        self.excluded_addresses = [
            "5Q544fKrFoe6tsEbD7S8EmxGTJYAKtTVhAW5Q5pge4j1",
            "TSLvdd1pWpHVjahSpsvCXUbgwsL3JAcvokwaKt1eokM"
        ]
        
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

    def get_bonding_curve(self, contract_address: str):
        """Get bonding curve address for a contract"""
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contract_address}"
        retries = 3

        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:
                    data = response.json().get('data', {})
                    try:
                        return data['token']['pool_info']['pool_address']
                    except (KeyError, TypeError):
                        return ""
            except Exception as e:
                print(f"Error fetching bonding curve on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return ""

    def fetch_top_holders(self, contract_address: str):
        """Fetch top holders data for a single contract address"""
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_holders/sol/{contract_address}?orderby=amount_percentage&direction=desc"
        retries = 3

        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:
                    data = response.json().get('data', [])
                    if data:
                        # Only get bonding curve to exclude it from results
                        bonding_curve = self.get_bonding_curve(contract_address)
                        if bonding_curve:
                            self.excluded_addresses.append(bonding_curve)
                        # Filter out excluded addresses and low value holders
                        return [holder for holder in data 
                               if holder['address'] not in self.excluded_addresses 
                               and holder.get('cost_cur', 0) >= 50]
            except Exception as e:
                print(f"Error fetching data on attempt {attempt + 1}: {e}")
                
                try:
                    import cloudscraper
                    scraper = cloudscraper.create_scraper()
                    response = scraper.get(url, headers=self.headers)
                    if response.status_code == 200:
                        data = response.json().get('data', [])
                        if data:
                            return [holder for holder in data 
                                   if holder['address'] not in self.excluded_addresses 
                                   and holder.get('cost_cur', 0) >= 50]
                except Exception as e:
                    print(f"Backup scraper failed: {e}")
            time.sleep(1)
        return []

    def get_top_holders(self, contract_addresses):
        """Get top holders for multiple contract addresses"""
        if isinstance(contract_addresses, str):
            contract_addresses = [addr.strip() for addr in contract_addresses.split(',')]
        
        all_holders = []
        for address in contract_addresses:
            holders = self.fetch_top_holders(address)
            all_holders.extend(holders)
            
        return all_holders 