import json
import time
import random
import tls_client
from fake_useragent import UserAgent

class BscTopTradersService:
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
            'referer': 'https://gmgn.ai/?chain=bsc',  
            'user-agent': self.ua.random
        }

    def fetch_top_traders(self, contract_address: str):
        """Fetch top traders data for a single BSC contract address"""
        url = f"https://gmgn.ai/defi/quotation/v1/tokens/top_traders/bsc/{contract_address}?orderby=profit&direction=desc"
        retries = 3

        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:
                    data = response.json().get('data', [])
                    if data:
                        return self.process_traders_data(data)
            except Exception as e:
                print(f"Error fetching data on attempt {attempt + 1}: {e}")
                
                try:
                    import cloudscraper
                    scraper = cloudscraper.create_scraper()
                    response = scraper.get(url, headers=self.headers)
                    if response.status_code == 200:
                        data = response.json().get('data', [])
                        if data:
                            return self.process_traders_data(data)
                except Exception as e:
                    print(f"Backup scraper failed: {e}")
            time.sleep(1)
        return []

    def process_traders_data(self, traders_data):
        """Process the raw traders data into a formatted response"""
        processed_data = []
        
        for trader in traders_data:
            try:
                multiplier_value = trader.get('profit_change')
                if multiplier_value:
                    processed_trader = {
                        "address": trader['address'],
                        "bought_usd": f"${trader['total_cost']:,.2f}" if trader.get('total_cost') is not None else "$0.00",
                        "total_profit": f"${trader['realized_profit']:,.2f}" if trader.get('realized_profit') is not None else "$0.00",
                        "unrealized_profit": f"${trader['unrealized_profit']:,.2f}" if trader.get('unrealized_profit') is not None else "$0.00",
                        "multiplier": f"{multiplier_value:.2f}x",
                        "buys": trader.get('buy_tx_count_cur', 0),
                        "sells": trader.get('sell_tx_count_cur', 0)
                    }
                    processed_data.append(processed_trader)
            except Exception as e:
                print(f"Error processing trader data: {e}")
                continue

        return processed_data

    def get_bsc_top_traders(self, contract_addresses):
        """Get top traders for multiple BSC contract addresses"""
        if isinstance(contract_addresses, str):
            contract_addresses = [addr.strip() for addr in contract_addresses.split(',')]
        
        all_traders = []
        for address in contract_addresses:
            traders = self.fetch_top_traders(address)
            all_traders.extend(traders)
            
        return all_traders 