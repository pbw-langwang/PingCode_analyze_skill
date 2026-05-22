#!/usr/bin/env python3
"""
PingCode API HTTP 工具
用法:
  python http_tool.py get <url> [headers_json]
  python http_tool.py post <url> <data_json> [headers_json]
  python http_tool.py token <client_id> <client_secret>
"""

import sys
import json
import requests
import urllib.parse

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "get":
        if len(sys.argv) < 3:
            print("ERROR: Missing URL")
            sys.exit(1)
        url = sys.argv[2]
        headers = {}
        if len(sys.argv) > 3:
            headers = json.loads(sys.argv[3])

        try:
            response = requests.get(url, headers=headers, timeout=30)
            print_response(response)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    elif command == "post":
        if len(sys.argv) < 4:
            print("ERROR: Missing URL or data")
            sys.exit(1)
        url = sys.argv[2]
        data = json.loads(sys.argv[3])
        headers = {}
        if len(sys.argv) > 4:
            headers = json.loads(sys.argv[4])

        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            print_response(response)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

    elif command == "token":
        if len(sys.argv) < 4:
            print("ERROR: Missing client_id or client_secret")
            sys.exit(1)
        client_id = sys.argv[2]
        client_secret = sys.argv[3]

        token = get_access_token(client_id, client_secret)
        if token:
            print(f"TOKEN:{token}")
        else:
            print("ERROR: Failed to get token")
            sys.exit(1)

    elif command in ["help", "-h", "--help"]:
        print_help()

    else:
        print(f"ERROR: Unknown command: {command}")
        print_help()
        sys.exit(1)


def get_access_token(client_id, client_secret):
    """通过 client_credentials 获取 access_token（GET 请求方式）"""
    base_url = "https://open.pingcode.com"
    params = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    query_string = urllib.parse.urlencode(params)
    url = f"{base_url}/v1/auth/token?{query_string}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            return response.json().get("access_token")
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None


def print_response(response):
    """打印响应结果"""
    result = {
        "status_code": response.status_code,
        "headers": dict(response.headers),
        "body": None
    }

    try:
        result["body"] = response.json()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except:
        result["body"] = response.text
        print(json.dumps(result, ensure_ascii=False, indent=2))


def print_help():
    print("""
PingCode API HTTP 工具

用法:
  python http_tool.py get <url> [headers_json]
  python http_tool.py post <url> <data_json> [headers_json]
  python http_tool.py token <client_id> <client_secret>

示例:
  # 获取 Access Token
  python http_tool.py token your_client_id your_client_secret

  # GET 请求
  python http_tool.py get "https://open.pingcode.com/v1/project/work_items?project_id=xxx" \\
    '{"Authorization": "Bearer your_token"}'

  # POST 请求
  python http_tool.py post "https://example.com/api" '{"key": "value"}' \\
    '{"Content-Type": "application/json"}'
""")


if __name__ == "__main__":
    main()
