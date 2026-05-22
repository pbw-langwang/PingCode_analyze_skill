import requests
import json
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

token = sys.argv[1] if len(sys.argv) > 1 else None
if not token:
    print('ERROR: Usage: py list_projects.py <access_token>')
    sys.exit(1)

base_url = config['api']['base_url']
url = base_url + '/v1/project/projects'
headers = {'Authorization': 'Bearer ' + token}

try:
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        print(f'ERROR: HTTP {resp.status_code}')
        print(resp.text)
        sys.exit(1)
    projects = resp.json().get('values', [])
    for p in projects:
        identifier = p.get('identifier', '')
        name = p.get('name', '')
        pid = p.get('id', '')
        print(f'{identifier}\t{name}\t{pid}')
except Exception as e:
    print(f'ERROR: {e}')
    sys.exit(1)
