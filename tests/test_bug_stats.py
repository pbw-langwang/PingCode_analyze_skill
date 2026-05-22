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

print("=== 步骤 1: 读取配置 ===")
print(f"Client ID: {client_id}")
print(f"Project ID: {project_id}")
print()

print("=== 步骤 2: 获取 Access Token ===")
base_url = config['api'].get('base_url', 'https://open.pingcode.com')
token_url = f"{base_url}/v1/auth/token?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"
response = requests.get(token_url, timeout=30)

if response.status_code == 200:
    token = response.json().get('access_token')
    print(f"Token 获取成功: {token[:20]}...")
else:
    print(f"Token 获取失败: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

print()
print("=== 步骤 3: 获取项目工作项 ===")
api_url = f"{base_url}/v1/project/work_items?project_id={project_id}&page_size=20"
headers = {'Authorization': f'Bearer {token}'}
response = requests.get(api_url, headers=headers, timeout=30)

if response.status_code == 200:
    data = response.json()
    total = data.get('total', 0)
    items = data.get('values', [])
    print(f"数据获取成功")
    print(f"   总工作项数: {total}")
    print(f"   当前页工作项数: {len(items)}")

    bugs = [item for item in items if item.get('type') == 'bug']
    print(f"   当前页 Bug 数: {len(bugs)}")
    print()

    status_counts = {}
    for bug in bugs:
        status = bug.get('status_identifier', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

    print("=== Bug 统计结果 ===")
    print(f"Bug 总数: {len(bugs)}")
    print("按状态分布:")
    for status, count in status_counts.items():
        print(f"  - {status}: {count} 个")

    print()
    print("Bug 列表:")
    for i, bug in enumerate(bugs[:5], 1):
        title = bug.get('title', '无标题')
        status = bug.get('status_identifier', 'unknown')
        assignee = bug.get('assignee', {}) or {}
        assignee_name = assignee.get('display_name', '未分配')
        print(f"{i}. [{status}] {title} - 负责人: {assignee_name}")

    if len(bugs) > 5:
        print(f"... 还有 {len(bugs) - 5} 个 Bug")
else:
    print(f"数据获取失败: HTTP {response.status_code}")
    print(response.text)
    sys.exit(1)

print()
print("=== 完成 ===")
