import json
import time
import random
import tls_client
from fake_useragent import UserAgent
from datetime import datetime

class WalletDetailsService:
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
            'user-agent': self.ua.random,
            'from_app': 'gmgn',
            'app_lang': 'en-US',
            'os': 'web'
        }

    def get_wallet_details(self, wallet_address: str, period: str = '7d'):
        """Fetch detailed wallet information from all endpoints
        
        Args:
            wallet_address (str): The wallet address to fetch details for
            period (str): The time period for stats - one of '1d', '7d', '30d', 'all'. Defaults to '7d'
        """
        base_url = "https://gmgn.ai/api/v1"
        
        # Define endpoints with query parameters
        recent_url = f"{base_url}/wallet_holdings/sol/{wallet_address}?from_app=gmgn&app_lang=en-US&os=web&limit=50&orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=true&tx30d=true"
        holdings_url = f"{base_url}/wallet_holdings/sol/{wallet_address}?from_app=gmgn&app_lang=en-US&os=web&limit=50&orderby=last_active_timestamp&direction=desc&showsmall=false&sellout=false&hide_abnormal=false"
        dashboard_url = f"{base_url}/wallet_stat/sol/{wallet_address}/{period}"
        
        data = {
            "recent": {},
            "holdings": {},
            "dashboard": {}
        }
        
        # Fetch recent data
        try:
            self.randomise()
            response = self.sendRequest.get(recent_url, headers=self.headers)
            if response.status_code == 200:
                data["recent"] = response.json()
        except Exception as e:
            print(f"Error fetching recent data: {e}")

        # Fetch holdings data
        try:
            self.randomise()
            response = self.sendRequest.get(holdings_url, headers=self.headers)
            if response.status_code == 200:
                data["holdings"] = response.json()
        except Exception as e:
            print(f"Error fetching holdings data: {e}")

        # Fetch dashboard data
        try:
            self.randomise()
            response = self.sendRequest.get(dashboard_url, headers=self.headers)
            if response.status_code == 200:
                data["dashboard"] = response.json()
        except Exception as e:
            print(f"Error fetching dashboard data: {e}")

        return self.process_wallet_data(data)

    def process_wallet_data(self, data):
        """Process the raw wallet data into a formatted response"""
        try:
            processed_data = {
                "recent": data["recent"].get("data", {}).get("holdings", []),
                "holdings": data["holdings"].get("data", {}).get("holdings", []),
                "dashboard": data["dashboard"].get("data", {})
            }
            
            return processed_data
            
        except Exception as e:
            print(f"Error processing wallet data: {e}")
            return {
                "recent": {"message": "error", "data": {"holdings": []}},
                "holdings": {"message": "error", "data": {"holdings": []}},
                "dashboard": {"message": "error", "data": {}}
            } 