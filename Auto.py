import threading
from queue import Queue
import requests
import random
import string
import json
import hashlib
from faker import Faker

# Green text color for terminal output
GREEN = '\033[92m'
RESET = '\033[0m'

print(f"""
{GREEN}┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓           
> › Github :- @khanalex
> › By      :- AL3X KHAN
> › Proxy Support Added by @coopers-lab
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛{RESET}                """)
print(GREEN + '\x1b[38;5;208m⇼'*60 + RESET)

# OTP generation function (Now 5-digit OTP for ID creation)
def generate_otp():
    otp = ''.join(random.choices(string.digits, k=5))  # 5-digit OTP for ID creation
    return otp

# Generate random string (Username)
def generate_random_string(length):
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

# Getting mail domains
def get_mail_domains(proxy=None):
    url = "https://api.mail.tm/domains"
    try:
        response = requests.get(url, proxies=proxy)
        if response.status_code == 200:
            return response.json()['hydra:member']
        else:
            print(f'{GREEN}[×] E-mail Error : {response.text}{RESET}')
            return None
    except Exception as e:
        print(f'{GREEN}[×] Error : {e}{RESET}')
        return None

# Mail.tm account creation (Now with 5-digit OTP)
def create_mail_tm_account(proxy=None):
    fake = Faker()
    mail_domains = get_mail_domains(proxy)
    if mail_domains:
        domain = random.choice(mail_domains)['domain']
        username = generate_random_string(10)
        password = fake.password()
        otp = generate_otp()  # Generate 5-digit OTP only for new account
        birthday = fake.date_of_birth(minimum_age=18, maximum_age=45)
        first_name = fake.first_name()
        last_name = fake.last_name()
        url = "https://api.mail.tm/accounts"
        headers = {"Content-Type": "application/json"}
        data = {"address": f"{username}@{domain}", "password": password}       
        try:
            response = requests.post(url, headers=headers, json=data, proxies=proxy)
            if response.status_code == 201:
                return f"{username}@{domain}", password, first_name, last_name, birthday, otp
            else:
                print(f'{GREEN}[×] Email Error : {response.text}{RESET}')
                return None, None, None, None, None, None
        except Exception as e:
            print(f'{GREEN}[×] Error : {e}{RESET}')
            return None, None, None, None, None, None

# Facebook account registration (Only show OTP for new ID creation)
def register_facebook_account(email, password, first_name, last_name, birthday, otp, proxy=None):
    api_key = '882a8490361da98702bf97a021ddc14d'
    secret = '62f8ce9f74b12f84c123cc23437a4a32'
    gender = random.choice(['M', 'F'])
    
    # **Only Display OTP when new ID is created**
    if otp:
        print(f"{GREEN}Account Created! OTP for verification: {otp}{RESET}")  

    req = {
        'api_key': api_key,
        'attempt_login': True,
        'birthday': birthday.strftime('%Y-%m-%d'),
        'client_country_code': 'EN',
        'fb_api_caller_class': 'com.facebook.registration.protocol.RegisterAccountMethod',
        'fb_api_req_friendly_name': 'registerAccount',
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
    ensig = hashlib.md5((sig + secret).encode()).hexdigest()
    req['sig'] = ensig
    api_url = 'https://b-api.facebook.com/method/user.register'
    reg = _call(api_url, req, proxy)
    
    if reg and 'new_user_id' in reg:
        id = reg['new_user_id']
        token = reg['session_info']['access_token']
        
        print(f"""{GREEN}
-----------GENERATED-----------
EMAIL : {email}
ID : {id}
PASSWORD : {password}
NAME : {first_name} {last_name}
BIRTHDAY : {birthday} 
GENDER : {gender}
OTP : {otp} (Only for Account Creation)
-----------GENERATED-----------
Token : {token}
-----------GENERATED-----------{RESET}""")
    else:
        print(f'{GREEN}[×] Failed to generate Facebook account.{RESET}')

# Helper function for API call
def _call(url, params, proxy=None, post=True):
    headers = {'User-Agent': '[FBAN/FB4A;FBAV/35.0.0.48.273;FBDM/{density=1.33125,width=800,height=1205};FBLC/en_US;FBCR/;FBPN/com.facebook.katana;FBDV/Nexus 7;FBSV/4.1.1;FBBK/0;]'}
    if post:
        response = requests.post(url, data=params, headers=headers, proxies=proxy)
    else:
        response = requests.get(url, params=params, headers=headers, proxies=proxy)
    return response.json()

# Proxy and multithreading setup (unchanged)
def test_proxy(proxy, q, valid_proxies):
    if test_proxy_helper(proxy):
        valid_proxies.append(proxy)
    q.task_done()

def test_proxy_helper(proxy):
    try:
        response = requests.get('https://api.mail.tm', proxies=proxy, timeout=5)
        print(f'{GREEN}Pass: {proxy}{RESET}')
        return response.status_code == 200
    except:
        print(f'{GREEN}Fail: {proxy}{RESET}')
        return False

def load_proxies():
    with open('proxies.txt', 'r') as file:
        proxies = [line.strip() for line in file]
    return [{'http': f'http://{proxy}'} for proxy in proxies]

def get_working_proxies():
    proxies = load_proxies()
    valid_proxies = []
    q = Queue()
    for proxy in proxies:
        q.put(proxy)
    
    for _ in range(10):  
        worker = threading.Thread(target=worker_test_proxy, args=(q, valid_proxies))
        worker.daemon = True
        worker.start()
    
    q.join()  
    return valid_proxies

def worker_test_proxy(q, valid_proxies):
    while True:
        proxy = q.get()
        if proxy is None:
            break
        test_proxy(proxy, q, valid_proxies)

working_proxies = get_working_proxies()

if not working_proxies:
    print(f'{GREEN}[×] No working proxies found. Please check your proxies.{RESET}')
else:
    for i in range(int(input(f'{GREEN}[+] How Many Accounts You Want:  {RESET}'))):
        proxy = random.choice(working_proxies)
        email, password, first_name, last_name, birthday, otp = create_mail_tm_account(proxy)
        if email:
            register_facebook_account(email, password, first_name, last_name, birthday, otp, proxy)

print(GREEN + '\x1b[38;5;208m⇼'*60 + RESET)
