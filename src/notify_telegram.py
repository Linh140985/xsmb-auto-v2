import json
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
LATEST_PATH = ROOT / 'data' / 'latest.json'


def build_message() -> str:
    if not LATEST_PATH.exists():
        return '⚠️ XSMB v2: chưa có file data/latest.json sau khi chạy.'

    latest = json.loads(LATEST_PATH.read_text(encoding='utf-8'))
    repo_url = os.getenv('GITHUB_SERVER_URL', 'https://github.com') + '/' + os.getenv('GITHUB_REPOSITORY', 'Linh140985/xsmb-auto-v2')
    return (
        '✅ XSMB v2 đã cập nhật\n'
        f"Ngày: {latest.get('date')}\n"
        f"Đặc biệt: {latest.get('special')}\n"
        f"Đề 2 số: {latest.get('special_2d')}\n"
        f"Nguồn: {latest.get('source')}\n"
        f"Repo: {repo_url}"
    )


def main() -> None:
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print('Telegram secrets are not configured. Skip notification.')
        return

    response = requests.post(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data={
            'chat_id': chat_id,
            'text': build_message(),
            'disable_web_page_preview': 'true',
        },
        timeout=30,
    )
    response.raise_for_status()
    print('Telegram notification sent.')


if __name__ == '__main__':
    main()
