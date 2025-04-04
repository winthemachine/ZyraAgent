import time
import random
import tls_client
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

class GMGNService:
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
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=0, i',
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.ua.random
        }

    def get_url_for_type(self, token_type: str, site: str):
        """Get the appropriate URL based on token type and site"""
        base_urls = {
            "new": {
                "Pump.Fun": "https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h?limit=100&orderby=created_timestamp&direction=desc&new_creation=true",
                "Moonshot": "https://gmgn.ai/defi/quotation/v1/rank/sol/moonshot/1h?limit=100&orderby=created_timestamp&direction=desc&new_creation=true"
            },
            "completing": {
                "Pump.Fun": "https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h?limit=100&orderby=progress&direction=desc&pump=true",
                "Moonshot": "https://gmgn.ai/defi/quotation/v1/rank/sol/moonshot/1h?limit=100&orderby=progress&direction=desc&moonshot=true"
            },
            "soaring": {
                "Pump.Fun": "https://gmgn.ai/defi/quotation/v1/rank/sol/pump/1h?limit=100&orderby=market_cap_5m&direction=desc&soaring=true",
                "Moonshot": "https://gmgn.ai/defi/quotation/v1/rank/sol/moonshot/1h?limit=100&orderby=market_cap_5m&direction=desc&soaring=true"
            },
            "bonded": {
                "Pump.Fun": "https://gmgn.ai/defi/quotation/v1/pairs/sol/new_pairs/1h?limit=100&orderby=market_cap&direction=desc&launchpad=pump&period=1h&filters[]=not_honeypot&filters[]=pump",
                "Moonshot": "https://gmgn.ai/defi/quotation/v1/pairs/sol/new_pairs/1h?limit=100&orderby=open_timestamp&direction=desc&launchpad=moonshot&period=1h&filters[]=not_honeypot&filters[]=moonshot"
            }
        }
        return base_urls.get(token_type, {}).get(site)

    def fetch_contracts(self, token_type: str, site: str):
        """Fetch contract addresses for a specific token type"""
        url = self.get_url_for_type(token_type, site)
        if not url:
            return []

        retries = 3
        contracts = set()

        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json().get('data', {})
                    
                    if token_type == "bonded":
                        for item in data.get('pairs', []):
                            if base_address := item.get('base_address'):
                                contracts.add(base_address)
                    else:
                        for item in data.get('rank', []):
                            if address := item.get('address'):
                                contracts.add(address)
                    break
            except Exception as e:
                print(f"Error fetching contracts on attempt {attempt + 1}: {e}")
            time.sleep(1)

        return list(contracts)

    def get_token_contracts(self, token_type: str, site: str, max_threads: int = 5):
        """Get token contracts with concurrent processing"""
        all_contracts = set()
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = [
                executor.submit(self.fetch_contracts, token_type, site) 
                for _ in range(max_threads)
            ]
            
            for future in as_completed(futures):
                try:
                    contracts = future.result()
                    all_contracts.update(contracts)
                except Exception as e:
                    print(f"Error processing contracts: {e}")

        return {
            "token_type": token_type,
            "site": site,
            "total_contracts": len(all_contracts),
            "contracts": list(all_contracts)
        } 