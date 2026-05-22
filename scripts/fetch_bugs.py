import requests
import json
import os
import sys
from collections import Counter
from datetime import datetime
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config.json')

def read_config():
    if not os.path.exists(CONFIG_PATH):
        print(f'ERROR: config.json not found at {CONFIG_PATH}')
        print('Please create config.json in the skill root directory.')
        sys.exit(1)
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_token(config):
    api = config['api']
    url = (
        f"{api['base_url']}/v1/auth/token"
        f"?grant_type={api['grant_type']}"
        f"&client_id={api['client_id']}"
        f"&client_secret={api['client_secret']}"
    )
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        print(f'ERROR: Failed to get token, HTTP {resp.status_code}')
        sys.exit(1)
    return resp.json()['access_token']

def list_projects(config, token):
    base_url = config['api']['base_url'] + '/v1/project/projects'
    headers = {'Authorization': f'Bearer {token}'}
    try:
        resp = requests.get(base_url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print(f'ERROR: Failed to list projects, HTTP {resp.status_code}')
            return []
        data = resp.json()
        return data.get('values', data.get('items', []))
    except Exception as e:
        print(f'ERROR: Failed to list projects: {e}')
        return []

def resolve_project_id(config, token, arg=None):
    if arg:
        projects = list_projects(config, token)
        for p in projects:
            if p.get('id') == arg or p.get('identifier') == arg or p.get('name') == arg:
                return p['id'], p.get('name', p.get('identifier', arg))
        return arg, arg
    default_id = config.get('project', {}).get('default_project_id')
    if default_id:
        return default_id, default_id
    projects = list_projects(config, token)
    if not projects:
        print('ERROR: No projects found. Please specify a project ID.')
        sys.exit(1)
    print('Available projects:')
    for p in projects:
        print(f"  {p.get('identifier', '')}\t{p.get('name', '')}\t{p.get('id', '')}")
    print('\nPlease specify a project: py fetch_bugs.py <project_id_or_identifier>')
    sys.exit(1)

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

def fetch_all_bugs(config, token, project_id):
    base_url = config['api']['base_url'] + '/v1/project/work_items'
    headers = {'Authorization': f'Bearer {token}'}

    all_bugs = []
    all_items = []
    seen_ids = set()
    all_items_count = 0

    for item_type in ['bug', 'story', 'task']:
        page_index = 0
        while True:
            url = f'{base_url}?project_id={project_id}&type={item_type}&page_size=100&page_index={page_index}'
            try:
                resp = requests.get(url, headers=headers, timeout=30)
                if resp.status_code != 200:
                    print(f'Error page {page_index} (type={item_type}): HTTP {resp.status_code}')
                    break
                data = resp.json()
                values = data.get('values', [])
                total = data.get('total', 0)

                for item in values:
                    if item.get('id') not in seen_ids:
                        seen_ids.add(item.get('id'))
                        all_items.append(item)
                        all_items_count += 1
                        if is_bug(item):
                            all_bugs.append(item)

                if page_index % 10 == 0:
                    print(f'Page {page_index} (type={item_type}): got {len(values)} items, total bugs so far: {len(all_bugs)}')

                if len(values) == 0 or all_items_count >= total:
                    break
                page_index += 1
            except Exception as e:
                print(f'Error at page {page_index} (type={item_type}): {e}')
                break

    return all_bugs, all_items, all_items_count

def build_task_map(all_items):
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
    return task_map

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

def print_report(all_bugs, all_items, all_items_count):
    print(f'\nTotal items fetched: {all_items_count}')
    print(f'Total bugs found: {len(all_bugs)}')

    print(f'\n=== Bug 统计报告 ===')
    print(f'Bug 总数: {len(all_bugs)}')

    print('\n--- 1. Bug 状态分布 ---')
    status_counter = Counter()
    for bug in all_bugs:
        state = bug.get('state', {}) or {}
        status_counter[state.get('name', 'unknown')] += 1
    for status, count in status_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {status}: {count} ({pct:.1f}%)')

    print('\n--- 2. Bug 优先级分布 ---')
    priority_counter = Counter()
    for bug in all_bugs:
        priority = bug.get('priority', {}) or {}
        priority_counter[priority.get('name', '未设置')] += 1
    for p, count in priority_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {p}: {count} ({pct:.1f}%)')

    print('\n--- 3. Bug 负责人分布 ---')
    assignee_counter = Counter()
    for bug in all_bugs:
        assignee = bug.get('assignee', {}) or {}
        assignee_counter[assignee.get('display_name', '未分配')] += 1
    for a, count in assignee_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {a}: {count} ({pct:.1f}%)')

    print('\n--- 4. Bug 创建人分布 ---')
    creator_counter = Counter()
    for bug in all_bugs:
        creator = bug.get('created_by', {}) or {}
        creator_counter[creator.get('display_name', 'unknown')] += 1
    for c, count in creator_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {c}: {count} ({pct:.1f}%)')

    print('\n--- 5. Bug 所属迭代分布 ---')
    sprint_counter = Counter()
    for bug in all_bugs:
        sprint = bug.get('sprint', {}) or {}
        sprint_counter[sprint.get('name', '无迭代')] += 1
    for s, count in sprint_counter.most_common(20):
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {s}: {count} ({pct:.1f}%)')

    print('\n--- 6. Bug 按月创建趋势 ---')
    month_counter = Counter()
    for bug in all_bugs:
        created_at = bug.get('created_at')
        if created_at:
            month_counter[datetime.fromtimestamp(created_at).strftime('%Y-%m')] += 1
        else:
            month_counter['unknown'] += 1
    for m, count in sorted(month_counter.items()):
        print(f'  {m}: {count} {"#" * min(count, 50)}')

    print('\n--- 7. Bug 所属模块分布 ---')
    module_counter = Counter()
    for bug in all_bugs:
        props = bug.get('properties', {}) or {}
        module = props.get('caidanmokuai', '未分类') or '未分类'
        module_counter[module] += 1
    for m, count in module_counter.most_common(20):
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {m}: {count} ({pct:.1f}%)')

    print('\n--- 8. Bug 级别分布 ---')
    level_counter = Counter()
    for bug in all_bugs:
        props = bug.get('properties', {}) or {}
        level = props.get('Bugjibie', '未设置') or '未设置'
        level_counter[level] += 1
    for l, count in level_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {l}: {count} ({pct:.1f}%)')

    print('\n--- 9. Bug 问题根源分布 ---')
    origin_counter = Counter()
    for bug in all_bugs:
        props = bug.get('properties', {}) or {}
        origin = props.get('Bugwentigenyuan', '未设置') or '未设置'
        origin_counter[origin] += 1
    for o, count in origin_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {o}: {count} ({pct:.1f}%)')

    print('\n--- 10. Bug 状态类型汇总 ---')
    state_type_counter = Counter()
    for bug in all_bugs:
        state = bug.get('state', {}) or {}
        state_type_counter[state.get('type', 'unknown')] += 1
    for st, count in state_type_counter.most_common():
        pct = count / len(all_bugs) * 100 if all_bugs else 0
        print(f'  {st}: {count} ({pct:.1f}%)')

    print('\n--- 11. 未关闭的 Bug ---')
    unresolved = [b for b in all_bugs if b.get('state', {}).get('type', '') != 'completed']
    print(f'未关闭 Bug 总数: {len(unresolved)}')
    for bug in unresolved[:30]:
        title = bug.get('title', 'No title')[:60]
        state = bug.get('state', {}).get('name', 'unknown')
        priority = bug.get('priority', {}).get('name', 'unknown')
        assignee = bug.get('assignee', {}).get('display_name', '未分配')
        sprint = bug.get('sprint', {}).get('name', '无迭代')
        identifier = bug.get('identifier', '')
        print(f'  [{identifier}] [{state}] [{priority}] {title} - {assignee} ({sprint})')

    print('\n--- 12. 最近30天创建的 Bug ---')
    now = time.time()
    thirty_days = 30 * 24 * 3600
    recent_bugs = [b for b in all_bugs if b.get('created_at') and (now - b['created_at']) < thirty_days]
    print(f'最近30天新增 Bug: {len(recent_bugs)}')
    for bug in recent_bugs[:20]:
        title = bug.get('title', 'No title')[:60]
        state = bug.get('state', {}).get('name', 'unknown')
        identifier = bug.get('identifier', '')
        created = datetime.fromtimestamp(bug['created_at']).strftime('%Y-%m-%d')
        print(f'  [{identifier}] [{state}] {title} (创建于 {created})')

    print('\n--- 13. Bug 解决时长分析 ---')
    resolved_bugs = [b for b in all_bugs if b.get('completed_at') and b.get('created_at')]
    if resolved_bugs:
        resolution_times = [(b['completed_at'] - b['created_at']) / 3600 for b in resolved_bugs]
        avg_hours = sum(resolution_times) / len(resolution_times)
        print(f'  已解决 Bug 数: {len(resolved_bugs)}')
        print(f'  平均解决时长: {avg_hours:.1f} 小时 ({avg_hours/24:.1f} 天)')
        print(f'  最短解决时长: {min(resolution_times):.1f} 小时')
        print(f'  最长解决时长: {max(resolution_times):.1f} 小时 ({max(resolution_times)/24:.1f} 天)')

    print('\n--- 14. Bug 排查人/解决人分布 ---')
    task_map = build_task_map(all_items)
    investigator_counter = Counter()
    resolver_counter = Counter()
    for bug in all_bugs:
        inv, res = find_bug_assignees(bug, task_map)
        if inv:
            for name in inv.split('、'):
                investigator_counter[name] += 1
        if res:
            for name in res.split('、'):
                resolver_counter[name] += 1
    print('  排查人分布:')
    if investigator_counter:
        for name, count in investigator_counter.most_common():
            pct = count / len(all_bugs) * 100 if all_bugs else 0
            print(f'    {name}: {count} 次 ({pct:.1f}%)')
    else:
        print('    无排查人信息')
    print('  解决人分布:')
    if resolver_counter:
        for name, count in resolver_counter.most_common():
            pct = count / len(all_bugs) * 100 if all_bugs else 0
            print(f'    {name}: {count} 次 ({pct:.1f}%)')
    else:
        print('    无解决人信息')

    if not all_bugs:
        print('\nNO_DATA:No bugs found for this project')

    print(f'\n=== 统计完成 ===')

if __name__ == '__main__':
    config = read_config()
    token = get_token(config)
    project_arg = sys.argv[1] if len(sys.argv) > 1 else None
    project_id, project_name = resolve_project_id(config, token, project_arg)
    print(f'Project: {project_name} ({project_id})')
    all_bugs, all_items, all_items_count = fetch_all_bugs(config, token, project_id)
    print_report(all_bugs, all_items, all_items_count)
