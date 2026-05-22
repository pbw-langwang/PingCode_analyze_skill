import json
import requests
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

client_id = config['api']['client_id']
client_secret = config['api']['client_secret']
project_id = config['project']['default_project_id']
base_url = config['api'].get('base_url', 'https://open.pingcode.com')

print("=== PingCode Bug 统计测试 ===")
print()

print("步骤 1: 获取 Access Token...")
token_url = f"{base_url}/v1/auth/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
response = requests.get(token_url, timeout=30)

if response.status_code == 200:
    token = response.json().get('access_token')
    print(f"Token 获取成功: {token[:20]}...")
else:
    print(f"Token 获取失败: HTTP {response.status_code}")
    sys.exit(1)

print()
print("步骤 2: 获取并筛选 Bug 数据...")
api_url = f"{base_url}/v1/project/work_items"
headers = {'Authorization': f'Bearer {token}'}

all_bugs = []
page = 0
max_pages = 10

while page < max_pages:
    params = {
        'project_id': project_id,
        'page_size': 100,
        'page_index': page
    }
    response = requests.get(api_url, headers=headers, params=params, timeout=30)

    if response.status_code == 200:
        data = response.json()
        items = data.get('values', [])
        bugs_in_page = [item for item in items if item.get('type') == 'bug']
        all_bugs.extend(bugs_in_page)

        total = data.get('total', 0)
        print(f"   第 {page + 1} 页: 找到 {len(bugs_in_page)} 个 Bug")

        if (page + 1) * 100 >= total:
            break
        page += 1
    else:
        print(f"第 {page + 1} 页获取失败: HTTP {response.status_code}")
        break

print()
print("=== Bug 统计结果 ===")
print(f"Bug 总数: {len(all_bugs)}")

status_counts = {}
for bug in all_bugs:
    status = bug.get('status_identifier', 'unknown')
    status_counts[status] = status_counts.get(status, 0) + 1

print("\n按状态分布:")
for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
    percentage = (count / len(all_bugs)) * 100
    print(f"  - {status}: {count} 个 ({percentage:.1f}%)")

priority_counts = {}
for bug in all_bugs:
    priority = bug.get('priority', {})
    if isinstance(priority, dict):
        priority_name = priority.get('name', 'unknown')
    else:
        priority_name = str(priority)
    priority_counts[priority_name] = priority_counts.get(priority_name, 0) + 1

print("\n按优先级分布:")
for priority, count in sorted(priority_counts.items(), key=lambda x: -x[1]):
    percentage = (count / len(all_bugs)) * 100
    print(f"  - {priority}: {count} 个 ({percentage:.1f}%)")

print("\nBug 详情（前10个）:")
for i, bug in enumerate(all_bugs[:10], 1):
    title = bug.get('title', '无标题')[:50] + '...' if len(bug.get('title', '')) > 50 else bug.get('title', '无标题')
    status = bug.get('status_identifier', 'unknown')
    priority = bug.get('priority', {})
    priority_name = priority.get('name', 'unknown') if isinstance(priority, dict) else str(priority)
    assignee = bug.get('assignee', {}) or {}
    assignee_name = assignee.get('display_name', '未分配')
    print(f"{i}. [{status}] [{priority_name}] {title} - 负责人: {assignee_name}")

print()
print("=== 统计完成 ===")
