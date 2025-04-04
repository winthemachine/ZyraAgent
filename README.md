# Solana Analytics API 🚀

A powerful Flask-based REST API service that provides comprehensive analytics for Solana tokens and wallets. This project leverages GMGN.ai's data to deliver insights about top traders, holders, early buyers, and detailed wallet analysis.

## ⚠️ Important Note About GMGN.ai Access

Before using this API:
- GMGN.ai uses Cloudflare protection which may affect some requests

## 🌟 Features & Endpoints

### 1. Top Traders Analysis `/api/top-traders`
- Track most successful traders for specific tokens
- Detailed metrics including:
  - Profit/Loss calculations
  - Trading volumes
  - Win rates
  - Transaction history
  - Performance trends

### 2. Top Holders Analysis `/api/top-holders`
- Identify largest token holders
- Smart filtering:
  - Excludes bonding curve addresses
  - Filters low-value holders (< 50 USD)
  - Removes contract addresses
  - Tracks holding duration

### 3. Early Buyers Detection `/api/early-buyers`
- Find early token investors
- Includes:
  - Entry price analysis
  - Timing information
  - Transaction details
  - Creator address exclusion

### 4. Wallet Analysis `/api/check-wallets`
- Comprehensive wallet metrics:
  - 7-day performance
  - 30-day performance
  - Token distribution
  - Trading patterns

### 5. Wallet Details `/api/wallet-details`
- In-depth wallet information:
  - Complete transaction history
  - Current holdings
  - Performance metrics
  - Smart money analysis

## 🛠️ Technical Requirements

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)
- Git (for cloning)

### Required Packages
```bash
Flask
tls-client
fake-useragent
cloudscraper
```

## 📦 Installation Guide

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/ZyraAgent.git
cd ZyraAgent
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Setup
```bash
# Edit .env with your settings
FLASK_APP=app.py
FLASK_ENV=development
```

## 🚀 Running the API

### Development Mode
```bash
flask run
# API will be available at http://localhost:5000
```

### Production Mode
```bash
gunicorn app:app
```

## 📡 API Usage Examples

### 1. Top Traders Endpoint
```python
import requests

# Get top traders for a token
response = requests.post('http://localhost:5000/api/top-traders', 
    json={'contract_addresses': 'token_address1,token_address2'})

print(response.json())
```

### 2. Top Holders Endpoint
```python
# Get top holders for a token
response = requests.post('http://localhost:5000/api/top-holders',
    json={'contract_addresses': 'token_address'})
```

### 3. Early Buyers Endpoint
```python
# Get early buyers with limit
response = requests.post('http://localhost:5000/api/early-buyers',
    json={
        'contract_addresses': 'token_address',
        'limit': 20
    })
```

## 🔒 Security Features

- Randomized User-Agents
- TLS Client implementation
- Request header randomization
- Anti-bot protection bypass
- Rate limiting protection
- IP rotation support

## 📁 Project Structure
```
ZyraAgent/
├── app.py                    # Main Flask application
├── requirements.txt          # Dependencies
├── .env                     # Environment variables
├── services/
│   ├── __init__.py
│   ├── top_traders_service.py
│   ├── top_holders_service.py
│   ├── early_buyers_service.py
│   ├── wallet_checker_service.py
│   └── wallet_details_service.py
└── README.md
```

## 🔧 Error Handling

The API implements robust error handling:
- Multiple retry attempts (3x)
- Cloudscraper fallback
- Detailed error messages
- Rate limit handling
- Connection timeout management

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
