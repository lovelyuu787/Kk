import requests
import time
import random
import json
import sys
import os
from colorama import Fore, Style, init
init(autoreset=True)


class Bot:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://api.example.com'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json',
        }

    def get_token(self):
        try:
            response = self.session.get(f'{self.base_url}/auth', headers=self.headers)
            if response.status_code == 200:
                token = response.json().get('token')
                return token
            else:
                print(Fore.RED + f"Failed to get token: {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"Error fetching token: {e}")
        return None

    def perform_task(self, token):
        try:
            headers = self.headers.copy()
            headers['Authorization'] = f'Bearer {token}'
            response = self.session.post(f'{self.base_url}/tasks/do', headers=headers)
            if response.status_code == 200:
                print(Fore.GREEN + "✅ Task completed successfully!")
            else:
                print(Fore.RED + f"❌ Task failed: {response.status_code}")
        except Exception as e:
            print(Fore.RED + f"Error performing task: {e}")

    def run(self):
        print(Fore.CYAN + "Starting Bot without 2Captcha support...")
        token = self.get_token()
        if not token:
            print(Fore.RED + "❌ Could not retrieve token. Exiting.")
            return
        while True:
            self.perform_task(token)
            wait = random.randint(10, 30)
            print(Fore.YELLOW + f"Waiting {wait}s before next task...")
            time.sleep(wait)


if __name__ == '__main__':
    try:
        bot = Bot()
        bot.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\nBot stopped manually.")
