import time
import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent

class WalletCheckerService:
    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.cloudScraper = cloudscraper.create_scraper()
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
        self.sendRequest.timeout_seconds = 60

        self.headers = {
            'Host': 'gmgn.ai',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'dnt': '1',
            'priority': 'u=1, i',
            'referer': 'https://gmgn.ai/?chain=sol',
            'user-agent': self.ua.random
        }

    def get_token_distribution(self, wallet: str, period='30d'):
        """Get token distribution data for a wallet"""
        url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/{wallet}/unique_token_7d?interval={period}"
        retries = 3
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
                if response.status_code == 200:
                    return response.json()
            except Exception as e:
                print(f"Error fetching token distribution on attempt {attempt + 1}: {e}")
                try:
                    response = self.cloudScraper.get(url, headers=self.headers)
                    if response.status_code == 200:
                        return response.json()
                except Exception as e:
                    print(f"Backup scraper failed: {e}")
            time.sleep(1)
        return None

    def get_wallet_data(self, wallet: str):
        """Get wallet data including 7d and 30d metrics"""
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/wallet/{wallet}"
        retries = 3
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data_7d = response.json()
                    if data_7d['msg'] == "success":
                        # Get 30d data
                        url_30d = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/wallet/{wallet}?period=30d"
                        response_30d = self.sendRequest.get(url_30d, headers=self.headers)
                        data_30d = response_30d.json()
                        
                        # Get token distributions
                        token_distribution_7d = self.get_token_distribution(wallet, '7d')
                        token_distribution_30d = self.get_token_distribution(wallet, '30d')
                        
                        return {
                            "wallet_7d": data_7d,
                            "wallet_30d": data_30d,
                            "distribution_7d": token_distribution_7d,
                            "distribution_30d": token_distribution_30d
                        }
            except Exception as e:
                print(f"Error fetching wallet data on attempt {attempt + 1}: {e}")
                try:
                    response = self.cloudScraper.get(url, headers=self.headers)
                    if response.status_code == 200:
                        data_7d = response.json()
                        if data_7d['msg'] == "success":
                            url_30d = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/wallet/{wallet}?period=30d"
                            response_30d = self.cloudScraper.get(url_30d, headers=self.headers)
                            data_30d = response_30d.json()
                            
                            token_distribution_7d = self.get_token_distribution(wallet, '7d')
                            token_distribution_30d = self.get_token_distribution(wallet, '30d')
                            
                            return {
                                "wallet_7d": data_7d,
                                "wallet_30d": data_30d,
                                "distribution_7d": token_distribution_7d,
                                "distribution_30d": token_distribution_30d
                            }
                except Exception as e:
                    print(f"Backup scraper failed: {e}")
            time.sleep(1)
        return None

    def check_wallets(self, wallets):
        """Check multiple wallets"""
        if isinstance(wallets, str):
            wallets = [addr.strip() for addr in wallets.split(',')]
        
        results = []
        for wallet in wallets:
            data = self.get_wallet_data(wallet)
            if data:
                results.append(data)
                
        return results 