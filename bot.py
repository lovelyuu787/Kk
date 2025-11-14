import requests
import time
import json
import os
from colorama import Fore, init
init(autoreset=True)

BASE_URL = "https://blockstreet.money"

# ------------------------------
# Utility classes and functions
# ------------------------------
class BlockStreetAutoBot:
    def __init__(self):
        self.session = requests.Session()
        self.user_agent = "Mozilla/5.0 (Linux; Android 13)"

    def log(self, msg, color=Fore.WHITE):
        print(color + str(msg))

    def load_private_keys(self):
        if not os.path.exists("private_keys.txt"):
            self.log("private_keys.txt not found!", Fore.RED)
            return []
        with open("private_keys.txt", "r") as f:
            keys = [x.strip() for x in f.readlines() if x.strip()]
        self.log(f"[OK] Loaded {len(keys)} private key(s)", Fore.GREEN)
        return keys

    # ------------------------------
    # MAIN SWAP LOGIC (with delay)
    # ------------------------------
    def swap(self):
        url_balance = f"{BASE_URL}/api/me/balance"
        url_swap = f"{BASE_URL}/api/me/swap"

        keys = self.load_private_keys()
        if not keys:
            self.log("No private keys found.", Fore.RED)
            return

        FROM_SYMBOL = "BSD"
        TO_SYMBOL = "AAPL"
        swap_iters = 5
        RATE_BSD_TO_AAPL = 0.000438
        from_amount_val = 0.01
        FROM_AMOUNT_STR = f"{from_amount_val:.6f}".rstrip("0").rstrip(".")

        for pk in keys:
            headers = {"Authorization": pk, "User-Agent": self.user_agent}
            try:
                r = self.session.get(url_balance, headers=headers, timeout=15)
                data = r.json()
            except:
                self.log("Balance fetch failed", Fore.RED)
                continue

            if data.get("code") != 0:
                self.log("Invalid response for balance", Fore.RED)
                continue

            balance_val = float(data["data"].get(FROM_SYMBOL, 0))
            self.log(f"Balance: {balance_val} {FROM_SYMBOL}", Fore.CYAN)

            successful_swaps = 0
            swapped_aapl_total = 0.0

            for i in range(swap_iters):
                if balance_val < from_amount_val:
                    self.log("⚠ Remaining balance insufficient.", Fore.YELLOW)
                    break

                to_amount_val = from_amount_val * RATE_BSD_TO_AAPL
                to_amount_str = f"{to_amount_val:.6f}".rstrip("0").rstrip(".")

                payload = {
                    "from_symbol": FROM_SYMBOL,
                    "to_symbol": TO_SYMBOL,
                    "from_amount": FROM_AMOUNT_STR,
                    "to_amount": to_amount_str,
                }

                try:
                    s = self.session.post(url_swap, headers=headers, json=payload, timeout=15)
                    swap_data = s.json()
                except:
                    self.log("Swap request error", Fore.RED)
                    break

                if swap_data.get("code") == 0:
                    self.log(f"✅ Swap #{i+1} OK", Fore.GREEN)
                    successful_swaps += 1
                    swapped_aapl_total += to_amount_val
                    balance_val -= from_amount_val
                else:
                    self.log("Swap failed.", Fore.RED)
                    break

                # *** 20-SECOND DELAY ADDED HERE ***
                time.sleep(20)

            self.log(f"Swaps done: {successful_swaps}", Fore.GREEN)
            self.log(f"Total AAPL earned: {swapped_aapl_total}", Fore.CYAN)

# ------------------------------
# Program Start
# ------------------------------
if __name__ == "__main__":
    bot = BlockStreetAutoBot()
    bot.swap()
