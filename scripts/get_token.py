import requests
import json
import urllib.parse
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

if not os.path.exists(CONFIG_PATH):
    print(f'ERROR: config.json not found at {CONFIG_PATH}')
    sys.exit(1)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

api = config['api']
url = api['base_url'] + '/v1/auth/token?' + urllib.parse.urlencode({
    'grant_type': api['grant_type'],
    'client_id': api['client_id'],
    'client_secret': api['client_secret']
})

try:
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        print(f'ERROR: HTTP {resp.status_code}')
        print(resp.text)
        sys.exit(1)
    token = resp.json().get('access_token', '')
    if not token:
        print('ERROR: No access_token in response')
        sys.exit(1)
    print(token)
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
