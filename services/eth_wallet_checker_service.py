import time
import random
import tls_client
import cloudscraper
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed

class EthWalletCheckerService:
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
            'referer': 'https://gmgn.ai/?chain=eth',  
            'user-agent': self.ua.random
        }

    def get_token_distribution(self, wallet: str, period='30d'):
        """Get token distribution data for an ETH wallet"""
        url = f"https://gmgn.ai/defi/quotation/v1/rank/eth/wallets/{wallet}/unique_token_7d?interval={period}"
        retries = 3
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    tokens = data['data']['tokens']
                    
                    distribution = {
                        "-50% +": 0,
                        "0% - -50%": 0,
                        "0 - 50%": 0,
                        "50% - 199%": 0,
                        "200% - 499%": 0,
                        "500% - 600%": 0,
                        "600% +": 0
                    }

                    for token in tokens:
                        profit_pnl = token.get('total_profit_pnl')
                        if profit_pnl is not None:
                            profit_percentage = profit_pnl * 100
                            
                            if profit_percentage <= -50:
                                distribution["-50% +"] += 1
                            elif -50 < profit_percentage < 0:
                                distribution["0% - -50%"] += 1
                            elif 0 <= profit_percentage < 50:
                                distribution["0 - 50%"] += 1
                            elif 50 <= profit_percentage < 199:
                                distribution["50% - 199%"] += 1
                            elif 200 <= profit_percentage < 499:
                                distribution["200% - 499%"] += 1
                            elif 500 <= profit_percentage < 600:
                                distribution["500% - 600%"] += 1
                            else:
                                distribution["600% +"] += 1
                                
                    return distribution
            except Exception as e:
                print(f"Error fetching token distribution on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def get_wallet_data(self, wallet: str):
        """Get wallet data including 7d and 30d metrics for ETH"""
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/eth/walletNew/{wallet}?period=7d"
        retries = 5
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        wallet_data = data['data']
                        
                        
                        url_30d = f"https://gmgn.ai/defi/quotation/v1/smartmoney/eth/walletNew/{wallet}?period=30d"
                        response_30d = self.sendRequest.get(url_30d, headers=self.headers)
                        data_30d = response_30d.json()['data']
                        
                        
                        token_distribution_30d = self.get_token_distribution(wallet, '30d')
                        token_distribution_7d = self.get_token_distribution(wallet, '7d')
                        
                        return self.process_wallet_data(wallet, wallet_data, data_30d, token_distribution_7d, token_distribution_30d)
            except Exception as e:
                print(f"Error fetching wallet data on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def process_wallet_data(self, wallet, data, data_30d, token_distro_7d, token_distro_30d):
        """Process ETH wallet data into a formatted response"""
        try:
            return {
                "wallet": wallet,
                "total_profit_percent": f"{data['total_profit_pnl'] * 100:.2f}%" if data.get('total_profit_pnl') is not None else "0%",
                "profit_7d": f"${data['realized_profit_7d']:,.2f}" if data.get('realized_profit_7d') is not None else "$0.00",
                "profit_30d": f"${data_30d['realized_profit_30d']:,.2f}" if data_30d.get('realized_profit_30d') is not None else "$0.00",
                "winrate_7d": f"{data['winrate'] * 100:.2f}%" if data.get('winrate') is not None else "0%",
                "winrate_30d": f"{data_30d['winrate'] * 100:.2f}%" if data_30d.get('winrate') is not None else "0%",
                "eth_balance": f"{float(data['eth_balance']):.2f}" if data.get('eth_balance') is not None else "0",
                "trades_7d": data.get('buy_7d', 0),
                "trades_30d": data_30d.get('buy_30d', 0),
                "token_distribution_7d": token_distro_7d if token_distro_7d else {},
                "token_distribution_30d": token_distro_30d if token_distro_30d else {},
                "tags": data.get('tags', []),
                "link": f"https://gmgn.ai/eth/address/{wallet}"
            }
        except Exception as e:
            print(f"Error processing wallet data: {e}")
            return None

    def check_eth_wallets(self, wallets, max_threads=5):
        """Check multiple ETH wallets"""
        if isinstance(wallets, str):
            wallets = [addr.strip() for addr in wallets.split(',')]
        
        results = []
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {
                executor.submit(self.get_wallet_data, wallet): wallet 
                for wallet in wallets
            }
            
            for future in as_completed(futures):
                try:
                    data = future.result()
                    if data:
                        results.append(data)
                except Exception as e:
                    print(f"Error processing wallet: {e}")
                    
        return results 