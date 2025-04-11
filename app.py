from flask import Flask, jsonify, request
from flask_cors import CORS
from .services.top_traders_service import TopTradersService
from .services.top_holders_service import TopHoldersService
from .services.early_buyers_service import EarlyBuyersService
from .services.wallet_analyzer_service import WalletAnalyzerService
from .services.wallet_checker_service import WalletCheckerService
from .services.bsc_top_traders_service import BscTopTradersService
from .services.bsc_wallet_checker_service import BscWalletCheckerService
from .services.bundle_finder_service import BundleFinderService
from .services.eth_timestamp_service import EthTimestampService
from .services.eth_top_traders_service import EthTopTradersService
from .services.eth_wallet_checker_service import EthWalletCheckerService
from .services.gmgn_service import GMGNService
from .services.transaction_scanner_service import TransactionScannerService
from .services.wallet_details_service import WalletDetailsService

app = Flask(__name__)


cors_config = {
    "origins": ["*"],  
    "methods": ["GET", "POST", "OPTIONS", "PUT", "PATCH", "DELETE"],  
    "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept"]
}

cors = CORS(app) 
app.config['CORS_HEADERS'] = 'Content-Type'


@app.before_request
def log_request_info():
    app.logger.info('Headers: %s', request.headers)
    app.logger.info('Body: %s', request.get_data())

top_traders_service = TopTradersService()
top_holders_service = TopHoldersService()
early_buyers_service = EarlyBuyersService()
wallet_analyzer_service = WalletAnalyzerService()
wallet_checker_service = WalletCheckerService()
bsc_top_traders_service = BscTopTradersService()
bsc_wallet_checker_service = BscWalletCheckerService()
bundle_finder_service = BundleFinderService()
eth_timestamp_service = EthTimestampService()
eth_top_traders_service = EthTopTradersService()
eth_wallet_checker_service = EthWalletCheckerService()
gmgn_service = GMGNService()
transaction_scanner_service = TransactionScannerService()
wallet_details_service = WalletDetailsService()

@app.route("/api/")
def home():
    return jsonify({
        "message": "Welcome to Flask API",
        "status": "success"
    })

@app.route("/api/home")
def home_s():
    return jsonify({
        "message": "Welcome to Flasssk API",
        "status": "success"
    })

@app.route("/api/top-traders", methods=['POST'])
def get_top_traders():
    try:
        data = request.get_json()
        contract_addresses = data.get('addresses')
        
        if not contract_addresses:
            return jsonify({
                'success': False,
                'message': 'No contract addresses provided'
            }), 400

        traders = top_traders_service.get_top_traders(contract_addresses)
        
        return jsonify({
            'success': True,
            'data': traders
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/top-holders", methods=['POST'])
def get_top_holders():
    try:
        data = request.get_json()
        contract_addresses = data.get('addresses')
        
        if not contract_addresses:
            return jsonify({
                'success': False,
                'message': 'No contract addresses provided'
            }), 400

        holders = top_holders_service.get_top_holders(contract_addresses)
        
        return jsonify({
            'success': True,
            'data': holders
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/early-buyers", methods=['POST'])
def get_early_buyers():
    try:
        data = request.get_json()
        contract_addresses = data.get('addresses')
        limit = data.get('limit', 20)  
        
        if not contract_addresses:
            return jsonify({
                'success': False,
                'message': 'No contract addresses provided'
            }), 400

        buyers = early_buyers_service.get_early_buyers(contract_addresses, limit)
        
        return jsonify({
            'success': True,
            'data': buyers
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/check-wallets", methods=['POST'])
def check_wallets():
    try:
        data = request.get_json()
        wallets = data.get('wallets')
        
        if not wallets:
            return jsonify({
                'success': False,
                'message': 'No wallet addresses provided'
            }), 400

        results = wallet_checker_service.check_wallets(wallets)
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/analyze-wallets", methods=['POST'])
def analyze_wallets():
    try:
        data = request.get_json()
        wallets = data.get('wallets')
        filters = data.get('filters', {})
        
        if not wallets:
            return jsonify({
                'success': False,
                'message': 'No wallet addresses provided'
            }), 400

        results = wallet_analyzer_service.analyze_wallets(wallets, filters)
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/bsc/top-traders", methods=['POST'])
def get_bsc_top_traders():
    try:
        data = request.get_json()
        contract_addresses = data.get('addresses')
        
        if not contract_addresses:
            return jsonify({
                'success': False,
                'message': 'No contract addresses provided'
            }), 400

        traders = bsc_top_traders_service.get_bsc_top_traders(contract_addresses)
        
        return jsonify({
            'success': True,
            'data': traders
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/bsc/check-wallets", methods=['POST'])
def check_bsc_wallets():
    try:
        data = request.get_json()
        wallets = data.get('wallets')
        
        if not wallets:
            return jsonify({
                'success': False,
                'message': 'No wallet addresses provided'
            }), 400

        results = bsc_wallet_checker_service.check_bsc_wallets(wallets)
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/analyze-bundle", methods=['POST'])
def analyze_bundle():
    try:
        data = request.get_json()
        contract_address = data.get('address')
        
        if not contract_address:
            return jsonify({
                'success': False,
                'message': 'No contract address provided'
            }), 400

        bundle_data = bundle_finder_service.analyze_bundle(contract_address)
        
        if not bundle_data:
            return jsonify({
                'success': False,
                'message': 'Failed to analyze bundle'
            }), 400

        return jsonify({
            'success': True,
            'data': bundle_data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/eth/mint-timestamp", methods=['POST'])
def get_eth_mint_timestamp():
    try:
        data = request.get_json()
        contract_address = data.get('address')
        
        if not contract_address:
            return jsonify({
                'success': False,
                'message': 'Contract address is required'
            }), 400

        timestamp = eth_timestamp_service.get_mint_timestamp(contract_address)
        
        if timestamp is None:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch mint timestamp'
            }), 400

        return jsonify({
            'success': True,
            'data': {
                'contract_address': contract_address,
                'mint_timestamp': timestamp
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/eth/transactions-by-time", methods=['POST'])
def get_eth_transactions_by_time():
    try:
        data = request.get_json()
        contract_address = data.get('address')
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        max_threads = data.get('max_threads', 5)
        
        if not all([contract_address, start_time, end_time]):
            return jsonify({
                'success': False,
                'message': 'Contract address, start time, and end time are required'
            }), 400

        results = eth_timestamp_service.get_transactions_by_timestamp(
            contract_address,
            int(start_time),
            int(end_time),
            max_threads
        )
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/eth/top-traders", methods=['POST'])
def get_eth_top_traders():
    try:
        data = request.get_json()
        contract_addresses = data.get('addresses')
        max_threads = data.get('max_threads', 5)
        
        if not contract_addresses:
            return jsonify({
                'success': False,
                'message': 'No contract addresses provided'
            }), 400

        traders = eth_top_traders_service.get_eth_top_traders(
            contract_addresses,
            max_threads
        )
        
        return jsonify({
            'success': True,
            'data': traders
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/eth/check-wallets", methods=['POST'])
def check_eth_wallets():
    try:
        data = request.get_json()
        wallets = data.get('wallets')
        max_threads = data.get('max_threads', 5)
        
        if not wallets:
            return jsonify({
                'success': False,
                'message': 'No wallet addresses provided'
            }), 400

        results = eth_wallet_checker_service.check_eth_wallets(
            wallets,
            max_threads
        )
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/gmgn/token-contracts", methods=['POST'])
def get_token_contracts():
    try:
        data = request.get_json()
        token_type = data.get('type')  
        site = data.get('site')  
        max_threads = data.get('max_threads', 5)
        
        if not token_type or not site:
            return jsonify({
                'success': False,
                'message': 'Token type and site are required'
            }), 400

        if token_type not in ['new', 'completing', 'soaring', 'bonded']:
            return jsonify({
                'success': False,
                'message': 'Invalid token type'
            }), 400

        if site not in ['Pump.Fun', 'Moonshot']:
            return jsonify({
                'success': False,
                'message': 'Invalid site'
            }), 400

        results = gmgn_service.get_token_contracts(
            token_type,
            site,
            max_threads
        )
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/scan-transactions", methods=['POST'])
def scan_transactions():
    try:
        data = request.get_json()
        contract_address = data.get('address')
        max_threads = data.get('max_threads', 5)
        
        if not contract_address:
            return jsonify({
                'success': False,
                'message': 'Contract address is required'
            }), 400

        results = transaction_scanner_service.scan_transactions(
            contract_address,
            max_threads
        )
        
        return jsonify({
            'success': True,
            'data': results
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route("/api/wallet-details", methods=['POST'])
def get_wallet_details():
    try:
        data = request.get_json()
        wallet_address = data.get('address')
        period = data.get('period', '7d')  # Default to 7d if not provided
        
        # Validate period
        valid_periods = ['1d', '7d', '30d', 'all']
        if period not in valid_periods:
            return jsonify({
                'success': False,
                'message': 'Invalid period. Must be one of: 1d, 7d, 30d, all'
            }), 400
        
        if not wallet_address:
            return jsonify({
                'success': False,
                'message': 'Wallet address is required'
            }), 400

        details = wallet_details_service.get_wallet_details(wallet_address, period)
        
        if not details:
            return jsonify({
                'success': False,
                'message': 'Failed to fetch wallet details'
            }), 400

        return jsonify({
            'success': True,
            'data': details
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == "__main__":
    app.run(debug=True)  