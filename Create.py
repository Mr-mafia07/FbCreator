import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
from faker import Faker
import time
import re

print(f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @jatintiwari0 
> › By      :- JATIN TIWARI
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛                
""")
print('\x1b[38;5;208m⇼'*60)

def generate_random_string(length):
    """Generate a random alphanumeric string"""
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

def get_mail_domains(proxy=None):
    """Fetch available email domains from mail.tm"""
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'[×] Email Error : {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error : {e}')
        return None

def create_mail_tm_account(proxy=None):
    """Create a temporary email account and return credentials"""
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    
    if mail_domains:
        domain = random.choice(mail_domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
        first_name = fake.first_name()
        last_name = fake.last_name()
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

def get_mail_tm_token(email, password, proxy=None):
    """Get auth token for mail.tm inbox"""
    url = "https://api.mail.tm/token"
    headers = {"Content-Type": "application/json"}
    data = {"address": email, "password": password}
    
    try:
        response = requests.post(url, headers=headers, json=data, proxies=proxy)
        if response.status_code == 200:
            return response.json()["token"]
        else:
            print(f'[×] Token Error: {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error: {e}')
        return None

def get_latest_mail(token, proxy=None):
    """Fetch the latest email from inbox"""
    url = "https://api.mail.tm/messages"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, proxies=proxy)
        if response.status_code == 200:
            messages = response.json()["hydra:member"]
            if messages:
                latest_message_id = messages[0]["id"]
                return get_mail_content(token, latest_message_id, proxy)
            else:
                print("[×] No emails received yet.")
                return None
        else:
            print(f'[×] Inbox Error: {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error: {e}')
        return None

def get_mail_content(token, message_id, proxy=None):
    """Extract OTP from the latest email"""
    url = f"https://api.mail.tm/messages/{message_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(url, headers=headers, proxies=proxy)
        if response.status_code == 200:
            email_data = response.json()
            otp = extract_otp(email_data["text"])
            return otp
        else:
            print(f'[×] Message Fetch Error: {response.text}')
            return None
    except Exception as e:
        print(f'[×] Error: {e}')
        return None

def extract_otp(email_text):
    """Extract OTP from email text using regex"""
    otp_match = re.search(r'\b\d{4,6}\b', email_text)
    return otp_match.group(0) if otp_match else "OTP Not Found"

def register_facebook_account(email, password, first_name, last_name, birthday, proxy=None):
    """Register a Facebook account using the generated email"""
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
    reg = response.json()

    if "new_user_id" in reg:
        user_id = reg['new_user_id']
        token = reg['session_info']['access_token']
        return user_id, token
    else:
        print(f"[×] Registration Error: {reg}")
        return None, None

working_proxies = [{"http": "http://127.0.0.1:8080"}]  # Replace with actual working proxies

if not working_proxies:
    print('[×] No working proxies found. Please check your proxies.')
else:
    for i in range(int(input('[+] How Many Accounts You Want: '))):
        proxy = random.choice(working_proxies)
        email, password, first_name, last_name, birthday = create_mail_tm_account(proxy)
        
        if email and password:
            print(f"[*] Waiting for OTP...")  
            time.sleep(10)  # Wait for email to arrive  
            token = get_mail_tm_token(email, password, proxy)
            otp = get_latest_mail(token, proxy) if token else "OTP Not Found"

            user_id, fb_token = register_facebook_account(email, password, first_name, last_name, birthday, proxy)
            if user_id:
                print(f'''
-----------ACCOUNT CREATED-----------
EMAIL     : {email}
ID        : {user_id}
PASSWORD  : {password}
NAME      : {first_name} {last_name}
BIRTHDAY  : {birthday} 
GENDER    : {gender}
OTP       : {otp}
TOKEN     : {fb_token}
-------------------------------------
''')
