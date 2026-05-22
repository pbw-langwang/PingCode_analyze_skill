import requests
import json
import os
import sys
import argparse
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

if not os.path.exists(CONFIG_PATH):
    print(f'ERROR: config.json not found at {CONFIG_PATH}')
    sys.exit(1)

with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)

parser = argparse.ArgumentParser(description='Fetch work items from PingCode')
parser.add_argument('access_token', help='Access token')
parser.add_argument('project_id', help='Project ID')
parser.add_argument('--type', dest='item_type', default=None,
                    help='Filter by work item type(s), comma-separated (e.g. story,bug,task)')
parser.add_argument('--sprint-id', dest='sprint_id', default=None,
                    help='Filter by sprint ID')
parser.add_argument('--sprint-name', dest='sprint_name', default=None,
                    help='Filter by sprint name (fuzzy match, resolves to sprint_id)')
parser.add_argument('--start-date', dest='start_date', default=None,
                    help='Filter by created_at start date (YYYY-MM-DD)')
parser.add_argument('--end-date', dest='end_date', default=None,
                    help='Filter by created_at end date (YYYY-MM-DD)')
parser.add_argument('--bug-only', dest='bug_only', action='store_true',
                    help='Only output bug items (type=bug or story with bug backlog_type)')
parser.add_argument('--all', dest='output_all', action='store_true',
                    help='Output all work items (not just bugs)')
args = parser.parse_args()

TOKEN = args.access_token
PROJECT_ID = args.project_id
BASE = config['api']['base_url'] + '/v1/project/work_items'
H = {'Authorization': 'Bearer ' + TOKEN}

def resolve_sprint_id(token, project_id, sprint_name):
    sprint_url = config['api']['base_url'] + f'/v1/project/projects/{project_id}/sprints'
    headers = {'Authorization': 'Bearer ' + token}
    all_sprints = []
    page = 0
    while True:
        try:
            r = requests.get(sprint_url, headers=headers, params={
                'page_size': 100,
                'page_index': page
            }, timeout=30)
            if r.status_code != 200:
                break
            d = r.json()
            v = d.get('values', [])
            all_sprints.extend(v)
            if len(v) == 0 or len(all_sprints) >= d.get('total', 0):
                break
            page += 1
        except Exception:
            break

    for s in all_sprints:
        if sprint_name in s.get('name', ''):
            return s.get('id'), s.get('name'), s.get('start_at'), s.get('end_at')
    return None, None, None, None

sprint_id = args.sprint_id
sprint_time_range = None

if args.sprint_name and not sprint_id:
    resolved_id, resolved_name, start_at, end_at = resolve_sprint_id(TOKEN, PROJECT_ID, args.sprint_name)
    if resolved_id:
        sprint_id = resolved_id
        if start_at and end_at:
            sprint_time_range = (start_at, end_at)
        print(f'RESOLVED_SPRINT:{resolved_name} ({resolved_id})', file=sys.stderr)
    else:
        print(f'WARNING: Sprint "{args.sprint_name}" not found, fetching all items', file=sys.stderr)

item_types = []
if args.item_type:
    item_types = [t.strip() for t in args.item_type.split(',')]

if args.bug_only:
    bug_types = ['bug', 'story', 'task']
    for bt in bug_types:
        if bt not in item_types:
            item_types.append(bt)

def fetch_items(project_id, token, item_type=None, sprint_id=None):
    base = config['api']['base_url'] + '/v1/project/work_items'
    headers = {'Authorization': 'Bearer ' + token}
    items = []
    page = 0
    while True:
        try:
            params = {
                'project_id': project_id,
                'page_size': 100,
                'page_index': page
            }
            if item_type:
                params['type'] = item_type
            if sprint_id:
                params['sprint_id'] = sprint_id
            r = requests.get(base, headers=headers, params=params, timeout=30)
            if r.status_code != 200:
                print(f'ERROR: HTTP {r.status_code} at page {page} (type={item_type}, sprint={sprint_id})', file=sys.stderr)
                break
            d = r.json()
            v = d.get('values', [])
            items.extend(v)
            if len(v) == 0 or len(items) >= d.get('total', 0):
                break
            page += 1
        except Exception as e:
            print(f'ERROR at page {page}: {e}', file=sys.stderr)
            break
    return items

if item_types:
    all_items = []
    seen_ids = set()
    for t in item_types:
        fetched = fetch_items(PROJECT_ID, TOKEN, item_type=t, sprint_id=sprint_id)
        for item in fetched:
            if item.get('id') not in seen_ids:
                all_items.append(item)
                seen_ids.add(item.get('id'))
else:
    all_items = fetch_items(PROJECT_ID, TOKEN, sprint_id=sprint_id)

if sprint_time_range and not sprint_id:
    start_ts, end_ts = sprint_time_range
    filtered = []
    for item in all_items:
        ca = item.get('created_at')
        if ca and start_ts <= ca <= end_ts:
            filtered.append(item)
    all_items = filtered

if args.start_date or args.end_date:
    start_ts = None
    end_ts = None
    if args.start_date:
        start_ts = int(datetime.strptime(args.start_date, '%Y-%m-%d').timestamp())
    if args.end_date:
        end_ts = int(datetime.strptime(args.end_date + ' 23:59:59', '%Y-%m-%d %H:%M:%S').timestamp())
    filtered = []
    for item in all_items:
        ca = item.get('created_at')
        if ca:
            if start_ts and ca < start_ts:
                continue
            if end_ts and ca > end_ts:
                continue
            filtered.append(item)
    all_items = filtered

BUG_BACKLOG_TYPE_IDS = {'6966f89927d8ec1063e68c33', '6a06e3ce5919695071aa9619'}

def is_bug(item):
    if item.get('type') == 'bug':
        return True
    if item.get('type') == 'story':
        props = item.get('properties', {}) or {}
        backlog_type = props.get('backlog_type')
        if backlog_type in BUG_BACKLOG_TYPE_IDS:
            return True
    return False

def find_bug_assignees(bug_item, task_map):
    bug_title = bug_item.get('title', '')
    investigators = []
    resolvers = []
    for task_title, names in task_map.items():
        if task_title.startswith('排查：'):
            core = task_title[3:]
            if core in bug_title or bug_title in core:
                for name in names:
                    if name and name not in investigators:
                        investigators.append(name)
        elif task_title.startswith('解决：'):
            core = task_title[3:]
            if core in bug_title or bug_title in core:
                for name in names:
                    if name and name not in resolvers:
                        resolvers.append(name)
    return '、'.join(investigators), '、'.join(resolvers)

task_map = {}
for item in all_items:
    if item.get('type') != 'task':
        continue
    item_title = item.get('title', '')
    if not (item_title.startswith('排查：') or item_title.startswith('解决：')):
        continue
    a = item.get('assignee', {}) or {}
    name = a.get('display_name', '').strip()
    if item_title not in task_map:
        task_map[item_title] = []
    if name and name not in task_map[item_title]:
        task_map[item_title].append(name)

def format_item(item):
    s = item.get('state', {}) or {}
    p = item.get('priority', {}) or {}
    a = item.get('assignee', {}) or {}
    cr = item.get('created_by', {}) or {}
    sp = item.get('sprint', {}) or {}
    pr = item.get('properties', {}) or {}
    ca = item.get('created_at')
    co = item.get('completed_at')
    rh = round((co - ca) / 3600, 1) if ca and co else None
    result = {
        'id': item.get('identifier', ''),
        'title': item.get('title', ''),
        'type': item.get('type', ''),
        'state': s.get('name', ''),
        'state_type': s.get('type', ''),
        'priority': p.get('name', ''),
        'creator': cr.get('display_name', ''),
        'sprint': sp.get('name', ''),
        'module': pr.get('caidanmokuai', '') or '',
        'level': pr.get('Bugjibie', '') or '',
        'origin': pr.get('Bugwentigenyuan', '') or '',
        'created': datetime.fromtimestamp(ca).strftime('%Y-%m-%d') if ca else '',
        'completed': datetime.fromtimestamp(co).strftime('%Y-%m-%d') if co else '',
        'hours': rh
    }
    if is_bug(item):
        inv, res = find_bug_assignees(item, task_map)
        result['investigator'] = inv
        result['resolver'] = res
    else:
        result['assignee'] = a.get('display_name', '')
    return json.dumps(result, ensure_ascii=False)

bugs = [i for i in all_items if is_bug(i)]
print(f'TOTAL_ITEMS:{len(all_items)}')
print(f'TOTAL_BUGS:{len(bugs)}')

if args.output_all:
    for item in all_items:
        print(format_item(item))
else:
    if not bugs and not all_items:
        print('NO_DATA:No work items found for the given filters')
    for b in bugs:
        print(format_item(b))
