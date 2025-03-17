import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
import time
from faker import Faker

# Banner
print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @jatintiwari0 
> › By      :- JATIN TIWARI
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                
""")
print('\x1b[38;5;208m⇼'*60)

# Function to generate random strings
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Get Mail.tm domains
def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'[×] E-mail Error : {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error : {e}')
        return None

# Create a Mail.tm email account
def create_mail_tm_account(proxy=None):
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    if mail_domains:
        domain = random.choice(mail_domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        first_name = fake.first_name()
        last_name = fake.last_name()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
        
        url = "https://api.mail.tm/accounts"
        headers = {"Content-Type": "application/json"}
        data = {"address": f"{username}@{domain}", "password": password}
        
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy)
            if response.status_code == 201:
                return f"{username}@{domain}", password, first_name, last_name, birthday
            else:
                print(f'[×] Email Error : {response.text}')
                return None, None, None, None, None
        except Exception as e:
            print(f'[×] Error : {e}')
            return None, None, None, None, None

# Get OTP from Mail.tm inbox
def get_mail_tm_otp(email, password, proxy=None):
    login_url = "https://api.mail.tm/token"
    inbox_url = "https://api.mail.tm/messages"
    
    headers = {"Content-Type": "application/json"}
    login_data = {"address": email, "password": password}
    
    try:
        # Get Mail.tm authentication token
        response = requests.post(login_url, headers=headers, json=login_data, proxies=proxy)
        if response.status_code != 200:
            print(f"[×] Token Error: {response.text}")
            return None

        token = response.json().get("token")
        headers["Authorization"] = f"Bearer {token}"

        # Fetch OTP from inbox
        for _ in range(10):  # Retry for 10 attempts
            time.sleep(5)
            response = requests.get(inbox_url, headers=headers, proxies=proxy)
            if response.status_code == 200:
                messages = response.json().get("hydra:member", [])
                for msg in messages:
                    if "Facebook" in msg["subject"]:
                        message_id = msg["id"]
                        message_response = requests.get(f"{inbox_url}/{message_id}", headers=headers, proxies=proxy)
                        if message_response.status_code == 200:
                            otp = extract_otp(message_response.json()["text"])
                            if otp:
                                return otp
            print("[*] Waiting for OTP...")
        
        print("[×] OTP Not Found.")
        return None
    except Exception as e:
        print(f"[×] Error Fetching OTP: {e}")
        return None

# Extract OTP from email text
def extract_otp(text):
    import re
    match = re.search(r'\b\d{5,6}\b', text)
    return match.group(0) if match else None

# Confirm email on Facebook
def confirm_facebook_email(email, otp, proxy=None):
    url = "https://www.facebook.com/confirmemail"
    data = {"email": email, "otp": otp}
    
    try:
        response = requests.post(url, data=data, proxies=proxy)
        return response.status_code == 200
    except Exception as e:
        print(f"[×] Error Confirming Email: {e}")
        return False

# Register a Facebook account
def register_facebook_account(email, password, first_name, last_name, birthday, proxy=None):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])
    
    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'firstname': first_name,
        'format': 'json',
        'gender': gender,
        'lastname': last_name,
        'email': email,
        'locale': 'en_US',
        'method': 'user.register',
        'password': password,
        'reg_instance': generate_random_string(32),
        'return_multiple_errors': True
    }
    
    sorted_req = sorted(req.items(), key=lambda x: x[0])
    sig = ''.join(f'{k}={v}' for k, v in sorted_req)
    req['sig'] = hashlib.md5((sig + secret).encode()).hexdigest()
    
    api_url = 'https://b-api.facebook.com/method/user.register'
    response = requests.post(api_url, data=req, proxies=proxy)
    if response.status_code == 200:
        reg = response.json()
        if 'new_user_id' in reg:
            print(f"✔ Account Created: {email} | ID: {reg['new_user_id']}")
            return True
        else:
            print(f"[×] Registration Error: {reg}")
            return False
    else:
        print(f"[×] Registration Failed: {response.text}")
        return False

# Get working proxies
def load_proxies():
    with open('proxies.txt', 'r') as file:
        return [{'http': f'http://{line.strip()}'} for line in file]

def get_working_proxies():
    proxies = load_proxies()
    valid_proxies = []
    
    for proxy in proxies:
        try:
            response = requests.get('https://api.mail.tm', proxies=proxy, timeout=5)
            if response.status_code == 200:
                valid_proxies.append(proxy)
        except:
            continue
    return valid_proxies

# Main Execution
working_proxies = get_working_proxies()
if not working_proxies:
    print("[×] No working proxies found. Please check your proxies.")
else:
    num_accounts = int(input("[+] How Many Accounts You Want: "))
    for _ in range(num_accounts):
        proxy = random.choice(working_proxies)
        email, password, first_name, last_name, birthday = create_mail_tm_account(proxy)
        if email:
            otp = get_mail_tm_otp(email, password, proxy)
            if otp and confirm_facebook_email(email, otp, proxy):
                register_facebook_account(email, password, first_name, last_name, birthday, proxy)
            else:
                print("[×] Email Confirmation Failed.")

print('\x1b[38;5;208m⇼'*60)
