import json
import random
import tls_client
from fake_useragent import UserAgent
import time

class BundleFinderService:
    def __init__(self):
        self.sendRequest = tls_client.Session(client_identifier='chrome_103')
        self.ua = UserAgent(os='linux', browsers=['firefox'])
        self.formatTokens = lambda x: float(x) / 1_000_000  
        
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

    def get_team_trades(self, contract_address: str):
        """Get team/creator trades for a token"""
        url = f"https://gmgn.ai/defi/quotation/v1/trades/sol/{contract_address}?limit=100&maker=&tag%5B%5D=creator&tag%5B%5D=dev_team"
        retries = 3
        tx_hashes = set()
        
        for attempt in range(retries):
            try:
                self.randomise()
                
                info_response = self.sendRequest.get(
                    f"https://gmgn.ai/defi/quotation/v1/tokens/sol/{contract_address}", 
                    headers=self.headers
                )
                if info_response.status_code == 200:
                    info = info_response.json()
                    total_supply = info['total_supply']

                    
                    trades_response = self.sendRequest.get(url, headers=self.headers)
                    if trades_response.status_code == 200:
                        trades = trades_response.json()['data']['history']
                        
                        
                        for trade in trades:
                            if trade['event'] == "buy":
                                tx_hashes.add(trade['tx_hash'])
                                
                        return {
                            'tx_hashes': list(tx_hashes),
                            'total_supply': total_supply
                        }
            except Exception as e:
                print(f"Error fetching team trades on attempt {attempt + 1}: {e}")
            time.sleep(1)
        return None

    def check_bundle(self, tx_hashes: list, total_supply: int):
        """Check if transactions are bundled and get details"""
        total_amount = 0.00
        transactions = 0
        transaction_details = {}

        for tx_hash in tx_hashes:
            url = f"https://api.solana.fm/v0/transfers/{tx_hash}"
            retries = 3
            
            for attempt in range(retries):
                try:
                    response = self.sendRequest.get(url)
                    if response.status_code == 200:
                        transfer_data = response.json().get('result', {}).get('data', [])
                        
                        if isinstance(transfer_data, list):
                            amounts = []
                            for action in transfer_data:
                                if action.get('action') == "transfer" and action.get("token") != "":
                                    amount = self.formatTokens(action.get('amount'))
                                    amounts.append(amount)
                                    total_amount += amount
                                    transactions += 1
                                    
                            if amounts:
                                amounts_percentages = [
                                    (amount / total_supply * 100) for amount in amounts
                                ]
                                transaction_details[tx_hash] = {
                                    "amounts": amounts,
                                    "amounts_percentages": amounts_percentages
                                }
                        break
                except Exception as e:
                    print(f"Error checking bundle on attempt {attempt + 1}: {e}")
                time.sleep(1)

        return {
            "bundle_detected": transactions > 1,
            "transactions_count": transactions,
            "total_amount": total_amount,
            "percentage_of_supply": (total_amount / total_supply) if total_supply > 0 else 0,
            "transaction_details": transaction_details
        }

    def analyze_bundle(self, contract_address: str):
        """Analyze bundle transactions for a contract"""
        try:
            
            team_data = self.get_team_trades(contract_address)
            if not team_data:
                return None
                
            
            bundle_data = self.check_bundle(
                team_data['tx_hashes'], 
                team_data['total_supply']
            )
            
            return {
                "contract_address": contract_address,
                "bundle_detected": bundle_data["bundle_detected"],
                "transactions_count": bundle_data["transactions_count"],
                "total_amount": bundle_data["total_amount"],
                "percentage_of_supply": bundle_data["percentage_of_supply"],
                "transaction_details": bundle_data["transaction_details"]
            }
            
        except Exception as e:
            print(f"Error analyzing bundle: {e}")
            return None 