import requests
import json
import os
import sys
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

if not os.path.exists(CONFIG_PATH):
    print(f'ERROR: config.json not found at {CONFIG_PATH}')
    sys.exit(1)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

if len(sys.argv) < 3:
    print('ERROR: Usage: py list_sprints.py <access_token> <project_id>')
    sys.exit(1)

TOKEN = sys.argv[1]
PROJECT_ID = sys.argv[2]
BASE = config['api']['base_url'] + f'/v1/project/projects/{PROJECT_ID}/sprints'
H = {'Authorization': 'Bearer ' + TOKEN}

all_sprints = []
page = 0

while True:
    try:
        r = requests.get(BASE, headers=H, params={
            'page_size': 100,
            'page_index': page
        }, timeout=30)
        if r.status_code != 200:
            print(f'ERROR: HTTP {r.status_code} at page {page}')
            break
        d = r.json()
        v = d.get('values', [])
        all_sprints.extend(v)
        if len(v) == 0 or len(all_sprints) >= d.get('total', 0):
            break
        page += 1
    except Exception as e:
        print(f'ERROR at page {page}: {e}')
        break

for s in all_sprints:
    sid = s.get('id', '')
    name = s.get('name', '')
    status = s.get('status', '')
    start_at = s.get('start_at', '')
    end_at = s.get('end_at', '')
    start_str = datetime.fromtimestamp(start_at).strftime('%Y-%m-%d') if start_at else ''
    end_str = datetime.fromtimestamp(end_at).strftime('%Y-%m-%d') if end_at else ''
    print(json.dumps({
        'id': sid,
        'name': name,
        'status': status,
        'start_at': start_str,
        'end_at': end_str
    }, ensure_ascii=False))
