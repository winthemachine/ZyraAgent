import json
import time
import random
import tls_client
from fake_useragent import UserAgent

class WalletAnalyzerService:
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

    def get_token_distribution(self, wallet: str):
        """Get token distribution data for a wallet"""
        url = f"https://gmgn.ai/defi/quotation/v1/rank/sol/wallets/{wallet}/unique_token_7d?interval=30d"
        retries = 3
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers, allow_redirects=True)
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
                            elif profit_percentage >= 600:
                                distribution["600% +"] += 1
                                
                    return distribution
            except Exception as e:
                print(f"Error fetching token distribution on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def get_wallet_data(self, wallet: str):
        """Get wallet data including 7d and 30d metrics"""
        url = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=7d"
        retries = 5
        
        for attempt in range(retries):
            try:
                self.randomise()
                response = self.sendRequest.get(url, headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['msg'] == "success":
                        wallet_data = data['data']
                        
                        
                        url_30d = f"https://gmgn.ai/defi/quotation/v1/smartmoney/sol/walletNew/{wallet}?period=30d"
                        response_30d = self.sendRequest.get(url_30d, headers=self.headers)
                        data_30d = response_30d.json()['data']
                        
                        
                        token_distribution = self.get_token_distribution(wallet)
                        
                        return self.process_wallet_data(wallet, wallet_data, data_30d, token_distribution)
            except Exception as e:
                print(f"Error fetching wallet data on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def process_wallet_data(self, wallet, data_7d, data_30d, token_distribution):
        """Process wallet data into a formatted response"""
        try:
            processed_data = {
                "wallet": wallet,
                "total_profit_percent": f"{data_7d['total_profit_pnl'] * 100:.2f}%" if data_7d.get('total_profit_pnl') is not None else "0%",
                "profit_7d": f"${data_7d['realized_profit_7d']:,.2f}" if data_7d.get('realized_profit_7d') is not None else "$0.00",
                "profit_30d": f"${data_30d['realized_profit_30d']:,.2f}" if data_30d.get('realized_profit_30d') is not None else "$0.00",
                "winrate_7d": f"{data_7d['winrate'] * 100:.2f}%" if data_7d.get('winrate') is not None else "0%",
                "winrate_30d": f"{data_30d['winrate'] * 100:.2f}%" if data_30d.get('winrate') is not None else "0%",
                "sol_balance": f"{float(data_7d['sol_balance']):.2f}" if data_7d.get('sol_balance') is not None else "0",
                "trades_7d": data_7d.get('buy_7d', 0),
                "trades_30d": data_30d.get('buy_30d', 0),
                "token_distribution": token_distribution if token_distribution else {},
                "tags": data_7d.get('tags', []),
                "link": f"https://gmgn.ai/sol/address/{wallet}"
            }
            return processed_data
        except Exception as e:
            print(f"Error processing wallet data: {e}")
            return None

    def analyze_wallets(self, wallets, filters=None):
        """Analyze multiple wallets with optional filtering"""
        if isinstance(wallets, str):
            wallets = [addr.strip() for addr in wallets.split(',')]
        
        results = []
        for wallet in wallets:
            data = self.get_wallet_data(wallet)
            if data:
                
                if filters:
                    if self.apply_filters(data, filters):
                        results.append(data)
                else:
                    results.append(data)
                    
        return results
    
    def apply_filters(self, data, filters):
        """Apply filters to wallet data"""
        try:
            
            profit_7d = float(data['profit_7d'].replace('$', '').replace(',', ''))
            profit_30d = float(data['profit_30d'].replace('$', '').replace(',', ''))
            winrate_7d = float(data['winrate_7d'].replace('%', ''))
            winrate_30d = float(data['winrate_30d'].replace('%', ''))
            trades_7d = int(data['trades_7d'])
            trades_30d = int(data['trades_30d'])
            
            
            if filters.get('min_profit_7d') and profit_7d < filters['min_profit_7d']:
                return False
            if filters.get('max_profit_7d') and profit_7d > filters['max_profit_7d']:
                return False
            if filters.get('min_profit_30d') and profit_30d < filters['min_profit_30d']:
                return False
            if filters.get('max_profit_30d') and profit_30d > filters['max_profit_30d']:
                return False
            if filters.get('min_winrate_7d') and winrate_7d < filters['min_winrate_7d']:
                return False
            if filters.get('max_winrate_7d') and winrate_7d > filters['max_winrate_7d']:
                return False
            if filters.get('min_winrate_30d') and winrate_30d < filters['min_winrate_30d']:
                return False
            if filters.get('max_winrate_30d') and winrate_30d > filters['max_winrate_30d']:
                return False
            if filters.get('min_trades_7d') and trades_7d < filters['min_trades_7d']:
                return False
            if filters.get('max_trades_7d') and trades_7d > filters['max_trades_7d']:
                return False
            if filters.get('min_trades_30d') and trades_30d < filters['min_trades_30d']:
                return False
            if filters.get('max_trades_30d') and trades_30d > filters['max_trades_30d']:
                return False
            
            return True
        except Exception as e:
            print(f"Error applying filters: {e}")
            return False 