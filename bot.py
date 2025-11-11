import os
import sys
import time
import json
import random
import asyncio
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from eth_account import Account
from eth_account.messages import encode_defunct
from dotenv import load_dotenv

load_dotenv()

class Colors:
    RESET = "\033[0m"
    BRIGHT = "\033[1m"
    GREEN = "\033[32m\033[1m"
    YELLOW = "\033[33m\033[1m"
    BLUE = "\033[34m\033[1m"
    MAGENTA = "\033[35m\033[1m"
    CYAN = "\033[36m\033[1m"
    WHITE = "\033[37m\033[1m"
    RED = "\033[31m\033[1m"
    GRAY = "\033[90m"

class SecurityConfig:
    """Security configuration to prevent wallet drain"""
    MAX_TRANSACTION_AMOUNT = 0.01
    MIN_BALANCE_THRESHOLD = 0.001
    MAX_TRANSACTIONS_PER_HOUR = 100
    REQUIRE_CONFIRMATION = False

class Logger:
    """Enhanced logger with custom formatting"""
    
    @staticmethod
    def clear_terminal():
        os.system('clear' if os.name != 'nt' else 'cls')
    
    @staticmethod
    def _get_timestamp():
        wib_timezone = timezone(timedelta(hours=7))
        return datetime.now(wib_timezone).strftime("%H:%M:%S")
    
    @staticmethod
    def info(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.BLUE}[{wallet_display}]{Colors.RESET} {msg}")
    
    @staticmethod
    def success(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.GREEN}[{wallet_display}]{Colors.RESET} âœ… {msg}")
    
    @staticmethod
    def error(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.RED}[{wallet_display}]{Colors.RESET} âŒ {msg}")
    
    @staticmethod
    def warning(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.YELLOW}[{wallet_display}]{Colors.RESET} âš¡ {msg}")
    
    @staticmethod
    def process(wallet: Optional[str], msg: str):
        timestamp = Logger._get_timestamp()
        wallet_display = wallet or 'SYS'
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.MAGENTA}[{wallet_display}]{Colors.RESET} ðŸ”„ {msg}")
    
    @staticmethod
    def security(msg: str):
        timestamp = Logger._get_timestamp()
        print(f"{Colors.GRAY}{timestamp}{Colors.RESET} {Colors.RED}[SECURITY]{Colors.RESET} ðŸ” {msg}")

def display_banner():
    """Display application banner"""
    banner = f"""{Colors.CYAN}
    â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—
    â•‘                                                          â•‘
    â•‘                 BlockStreet Auto Bot                     â•‘
    â•‘                                                          â•‘
    â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
{Colors.RESET}"""
    print(banner)

def display_menu():
    """Display main menu"""
    print(f"\n{Colors.CYAN}â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â• MAIN MENU â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—{Colors.RESET}")
    print(f"{Colors.GREEN}  [1]{Colors.RESET} Auto Swap          {Colors.GREEN}[6]{Colors.RESET} Repay Loan")
    print(f"{Colors.GREEN}  [2]{Colors.RESET} Manual Swap        {Colors.GREEN}[7]{Colors.RESET} Auto All Operations")
    print(f"{Colors.GREEN}  [3]{Colors.RESET} Supply Assets      {Colors.GREEN}[8]{Colors.RESET} Set TX Count")
    print(f"{Colors.GREEN}  [4]{Colors.RESET} Withdraw Assets    {Colors.GREEN}[9]{Colors.RESET} Security Settings")
    print(f"{Colors.GREEN}  [5]{Colors.RESET} Borrow Assets")
    print(f"{Colors.CYAN}â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•{Colors.RESET}")
    print(f"{Colors.RED}  [0]{Colors.RESET} Exit Bot\n")

class WalletManager:
    """Secure wallet management"""
    
    @staticmethod
    def load_wallets_from_file(filename: str = 'private_keys.txt') -> List[Dict]:
        """Load wallets from file with validation"""
        wallets = []
        
        if not Path(filename).exists():
            Logger.error(None, f'Configuration file {filename} not found')
            Logger.info(None, f'Create {filename} with format: privatekey:wallet_name')
            return wallets
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            for idx, line in enumerate(lines, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                try:
                    parts = line.split(':')
                    private_key = parts[0].strip()
                    name = parts[1].strip() if len(parts) > 1 else f'W{idx}'
                    
                    if not private_key.startswith('0x'):
                        private_key = '0x' + private_key
                    
                    account = Account.from_key(private_key)
                    
                    wallets.append({
                        'account': account,
                        'name': name,
                        'address': account.address
                    })
                    
                except Exception as e:
                    Logger.warning(None, f'Invalid wallet config at line {idx}')
            
            if wallets:
                Logger.success(None, f'Successfully loaded {len(wallets)} wallet(s)')
        
        except Exception as e:
            Logger.error(None, f'Failed to read configuration: {str(e)}')
        
        return wallets
    
    @staticmethod
    def validate_transaction_amount(amount: float) -> bool:
        """Validate transaction amount against security limits"""
        if amount > SecurityConfig.MAX_TRANSACTION_AMOUNT:
            Logger.security(f'Amount {amount} exceeds limit {SecurityConfig.MAX_TRANSACTION_AMOUNT}')
            return False
        return True

class ProxyManager:
    """Proxy management"""
    
    @staticmethod
    def parse_proxy(proxy_line: str) -> Optional[str]:
        """Parse proxy string into proper format"""
        proxy = proxy_line.strip()
        if not proxy or proxy.startswith('#'):
            return None
        
        proxy = proxy.replace('http://', '').replace('https://', '')
        
        if '@' in proxy:
            parts = proxy.split('@')
            if len(parts) == 2:
                host_port = parts[0]
                user_pass = parts[1]
                return f'http://{user_pass}@{host_port}'
        
        parts = proxy.split(':')
        if len(parts) == 4:
            host, port, user, password = parts
            return f'http://{user}:{password}@{host}:{port}'
        
        return f'http://{proxy}'
    
    @staticmethod
    def load_proxies(filename: str = 'proxies.txt') -> List[str]:
        """Load proxies from file"""
        proxies = []
        
        if not Path(filename).exists():
            return proxies
        
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                proxy = ProxyManager.parse_proxy(line)
                if proxy:
                    proxies.append(proxy)
        
        except Exception as e:
            Logger.error(None, f'Proxy loading error: {str(e)}')
        
        return proxies


class CaptchaSolver:
    \"\"\"Captcha solver stub â€” automated 2Captcha usage removed.

    This stub preserves the original method names so the rest of the script
    works unchanged. It intentionally returns an empty API key and will not
    perform any network captcha solving. If a captcha_token is required by the
    site, the script will continue but you must provide or obtain the token
    manually (or integrate an alternative solver).
    \"\"\"

    @staticmethod
    def get_api_key(filename: str = '2captcha.txt') -> str:
        \"\"\"Return empty string to indicate no 2Captcha key will be used.\"\"\"
        # 2Captcha usage removed by user request â€” do not load or require any key.
        return ''

    @staticmethod
    async def solve_turnstile(api_key: str, sitekey: str, pageurl: str) -> Optional[str]:
        \"\"\"Automated solving disabled.

        If api_key is provided (non-empty) this function will raise to avoid
        accidentally calling 2Captcha. When api_key is empty, the caller should
        skip automated solving and continue (captcha_token should be '').
        \"\"\"
        if api_key:
            raise Exception('Automated Turnstile solving disabled: 2Captcha integration removed.')
        # Return empty token to continue execution without automated captcha solving.
        return ''


class BlockStreetAPI:
    """BlockStreet API client with security features"""
    
    CUSTOM_SIGN_TEXT = """blockstreet.money wants you to sign in with your Ethereum account:
0x4CBB1421DF1CF362DC618d887056802d8adB7BC0

Welcome to Block Street

URI: https://blockstreet.money
Version: 1
Chain ID: 1
Nonce: Z9YFj5VY80yTwN3n
Issued At: 2025-10-27T09:49:38.537Z
Expiration Time: 2025-10-27T09:51:38.537Z"""
    
    def __init__(self, wallet_data: Dict, proxy: Optional[str] = None):
        self.wallet_data = wallet_data
        self.account = wallet_data['account']
        self.name = wallet_data['name']
        self.address = wallet_data['address']
        self.session_cookie = None
        self.transaction_count = 0
        self.last_transaction_time = 0
        
        self.session = requests.Session()
        self.session.headers.update({
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'origin': 'https://blockstreet.money',
            'referer': 'https://blockstreet.money/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
        })
        
        if proxy:
            self.session.proxies = {
                'http': proxy,
                'https': proxy
            }
    
    def _check_rate_limit(self) -> bool:
        """Check if rate limit is exceeded"""
        current_time = time.time()
        if current_time - self.last_transaction_time < 3600:
            if self.transaction_count >= SecurityConfig.MAX_TRANSACTIONS_PER_HOUR:
                Logger.security(f'Rate limit reached for {self.name}')
                return False
        else:
            self.transaction_count = 0
            self.last_transaction_time = current_time
        
        self.transaction_count += 1
        return True
    
    def _send_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Send HTTP request with security checks"""
        url = f'https://api.blockstreet.money/api{endpoint}'
        
        headers = kwargs.pop('headers', {})
        headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        
        if self.session_cookie:
            headers['Cookie'] = self.session_cookie
        
        try:
            response = self.session.request(method, url, headers=headers, timeout=30, **kwargs)
            
            if 'set-cookie' in response.headers:
                cookie = response.headers['set-cookie']
                if 'gfsessionid=' in cookie:
                    self.session_cookie = cookie.split(';')[0]
            
            if response.status_code >= 200 and response.status_code < 300:
                data = response.json()
                if data.get('code') in [0, '0']:
                    return data.get('data', data)
                return data
            
            raise Exception(f'HTTP {response.status_code}: {response.text}')
        
        except Exception as e:
            raise Exception(f'Request failed: {str(e)}')
    
    async def login(self, captcha_token: str) -> Dict:
        """Login to BlockStreet"""
        try:
            Logger.process(self.name, 'Generating signature...')
            
            message = encode_defunct(text=self.CUSTOM_SIGN_TEXT)
            signed_message = self.account.sign_message(message)
            signature = signed_message.signature.hex()
            
            import re
            nonce_match = re.search(r'Nonce:\s*([^\n\r]+)', self.CUSTOM_SIGN_TEXT)
            nonce = nonce_match.group(1).strip() if nonce_match else 'Z9YFj5VY80yTwN3n'
            
            issued_match = re.search(r'Issued At:\s*([^\n\r]+)', self.CUSTOM_SIGN_TEXT)
            issued_at = issued_match.group(1).strip() if issued_match else datetime.now().isoformat()
            
            expiration_match = re.search(r'Expiration Time:\s*([^\n\r]+)', self.CUSTOM_SIGN_TEXT)
            expiration_time = expiration_match.group(1).strip() if expiration_match else datetime.now().isoformat()
            
            data = {
                'address': self.address,
                'nonce': nonce,
                'signature': signature,
                'chainId': '1',
                'issuedAt': issued_at,
                'expirationTime': expiration_time,
                'invite_code': os.getenv('INVITE_CODE', '')
            }
            
            Logger.process(self.name, 'Authenticating with server...')
            result = self._send_request('POST', '/account/signverify', data=data)
            
            Logger.success(self.name, 'Authentication successful âœ“')
            return result
        
        except Exception as e:
            raise Exception(f'Authentication failed: {str(e)}')
    
    def get_token_list(self) -> List[Dict]:
        """Get available tokens"""
        return self._send_request('GET', '/swap/token_list')
    
    def get_earn_info(self) -> Dict:
        """Get earning information"""
        return self._send_request('GET', '/earn/info')
    
    def get_supplies(self) -> List[Dict]:
        """Get supplied assets"""
        return self._send_request('GET', '/my/supply')
    
    def share(self) -> Dict:
        """Daily check-in"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        return self._send_request('POST', '/share')
    
    def swap(self, from_symbol: str, to_symbol: str, from_amount: float, to_amount: float) -> Dict:
        """Swap tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(from_amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'from_symbol': from_symbol,
            'to_symbol': to_symbol,
            'from_amount': str(from_amount),
            'to_amount': str(to_amount)
        }
        
        return self._send_request('POST', '/swap', json=data)
    
    def supply(self, symbol: str, amount: float) -> Dict:
        """Supply tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/supply', json=data)
    
    def withdraw(self, symbol: str, amount: float) -> Dict:
        """Withdraw tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/withdraw', json=data)
    
    def borrow(self, symbol: str, amount: float) -> Dict:
        """Borrow tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/borrow', json=data)
    
    def repay(self, symbol: str, amount: float) -> Dict:
        """Repay borrowed tokens with security checks"""
        if not self._check_rate_limit():
            raise Exception('Rate limit exceeded')
        
        if not WalletManager.validate_transaction_amount(amount):
            raise Exception('Amount exceeds security limit')
        
        data = {
            'symbol': symbol,
            'amount': str(amount)
        }
        
        return self._send_request('POST', '/repay', json=data)

async def process_auto_swap(wallets: List[Dict], proxies: List[str], token_list: List[Dict], captcha_token: str, tx_count: int):
    """Process auto swap for all wallets"""
    Logger.info(None, f'Starting Auto Swap for {len(wallets)} wallet(s)')
    Logger.info(None, f'Transactions per wallet: {tx_count}')
    
    proxy_index = 0
    for idx, wallet_data in enumerate(wallets, 1):
        proxy = proxies[proxy_index % len(proxies)] if proxies else None
        proxy_index += 1
        
        print(f"\n{Colors.CYAN}{'â•' * 60}{Colors.RESET}")
        print(f"{Colors.YELLOW}Processing Wallet {idx}/{len(wallets)}: {wallet_data['name']}{Colors.RESET}")
        print(f"{Colors.CYAN}{'â•' * 60}{Colors.RESET}")
        
        api = BlockStreetAPI(wallet_data, proxy)
        
        try:
            await api.login(captcha_token)
            
            supplies = api.get_supplies()
            owned_tokens = [s for s in supplies if s and float(s.get('amount', 0)) > 0]
            
            if not owned_tokens:
                Logger.warning(wallet_data['name'], 'No supplied assets found to swap')
                continue
            
            for i in range(tx_count):
                Logger.process(wallet_data['name'], f'Executing swap {i + 1}/{tx_count}')
                
                try:
                    from_asset = random.choice(owned_tokens)
                    from_token = next((t for t in token_list if t['symbol'] == from_asset['symbol']), None)
                    
                    if not from_token:
                        continue
                    
                    to_token = random.choice([t for t in token_list if t['symbol'] != from_token['symbol']])
                    
                    from_amount = get_random_amount(0.001, 0.0015)
                    to_amount = (from_amount * float(from_token.get('price', 1))) / float(to_token.get('price', 1))
                    
                    api.swap(from_token['symbol'], to_token['symbol'], from_amount, to_amount)
                    Logger.success(wallet_data['name'], f'Swapped {from_amount:.6f} {from_token["symbol"]} â†’ {to_amount:.6f} {to_token["symbol"]}')
                    
                except Exception as e:
                    Logger.error(wallet_data['name'], f'Swap failed: {str(e)}')
                
                if i < tx_count - 1:
                    await random_delay()
