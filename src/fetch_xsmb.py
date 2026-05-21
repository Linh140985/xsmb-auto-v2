import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

TZ = ZoneInfo('Asia/Ho_Chi_Minh')
BASE_URL = 'https://xoso.com.vn/xsmb-{date}.html'
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data'
HISTORY_PATH = DATA_DIR / 'xsmb-history.json'
LATEST_PATH = DATA_DIR / 'latest.json'
TWO_DIGITS_PATH = DATA_DIR / 'xsmb-2-digits.json'

PRIZE_CLASSES: Dict[str, tuple[str, int]] = {
    'special': ('special-prize', 1),
    'prize1': ('prize1', 1),
    'prize2': ('prize2', 2),
    'prize3': ('prize3', 6),
    'prize4': ('prize4', 4),
    'prize5': ('prize5', 6),
    'prize6': ('prize6', 3),
    'prize7': ('prize7', 4),
}

FLAT_PRIZE_ORDER = [
    'special', 'prize1',
    'prize2_1', 'prize2_2',
    'prize3_1', 'prize3_2', 'prize3_3', 'prize3_4', 'prize3_5', 'prize3_6',
    'prize4_1', 'prize4_2', 'prize4_3', 'prize4_4',
    'prize5_1', 'prize5_2', 'prize5_3', 'prize5_4', 'prize5_5', 'prize5_6',
    'prize6_1', 'prize6_2', 'prize6_3',
    'prize7_1', 'prize7_2', 'prize7_3', 'prize7_4',
]


@dataclass
class XSMBResult:
    date: str
    source: str
    special: str
    prize1: str
    prize2_1: str
    prize2_2: str
    prize3_1: str
    prize3_2: str
    prize3_3: str
    prize3_4: str
    prize3_5: str
    prize3_6: str
    prize4_1: str
    prize4_2: str
    prize4_3: str
    prize4_4: str
    prize5_1: str
    prize5_2: str
    prize5_3: str
    prize5_4: str
    prize5_5: str
    prize5_6: str
    prize6_1: str
    prize6_2: str
    prize6_3: str
    prize7_1: str
    prize7_2: str
    prize7_3: str
    prize7_4: str
    special_2d: str
    all_2d: List[str]
    fetched_at: str


def target_date() -> datetime.date:
    now = datetime.now(TZ)
    result_date = now.date()
    # XSMB thường có đủ kết quả khoảng 18:30-18:35. Trước mốc này thì lấy ngày hôm trước.
    if now.time() < time(18, 35):
        result_date -= timedelta(days=1)
    return result_date


def clean_number(value: str) -> str:
    digits = re.sub(r'\D', '', value or '')
    if not digits:
        raise ValueError(f'Empty prize value: {value!r}')
    return digits


def get_texts_by_class(soup: BeautifulSoup, class_name: str) -> List[str]:
    values = []
    for tag in soup.find_all(attrs={'class': class_name}):
        text = tag.get_text(' ', strip=True)
        # Some pages may put multiple numbers inside one node.
        values.extend(re.findall(r'\d+', text))
    return [clean_number(v) for v in values]


def fetch_from_xoso_com_vn(day: datetime.date) -> XSMBResult:
    url = BASE_URL.format(date=day.strftime('%d-%m-%Y'))
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; xsmb-auto-v2/1.0; +https://github.com/Linh140985/xsmb-auto-v2)',
        'Accept-Language': 'vi,en;q=0.9',
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'lxml')
    grouped: Dict[str, List[str]] = {}
    for key, (class_name, expected_count) in PRIZE_CLASSES.items():
        values = get_texts_by_class(soup, class_name)
        if len(values) < expected_count:
            raise ValueError(f'{key}: expected {expected_count}, got {len(values)} from {url}')
        grouped[key] = values[:expected_count]

    flat: Dict[str, str] = {
        'special': grouped['special'][0],
        'prize1': grouped['prize1'][0],
        'prize2_1': grouped['prize2'][0],
        'prize2_2': grouped['prize2'][1],
        'prize3_1': grouped['prize3'][0],
        'prize3_2': grouped['prize3'][1],
        'prize3_3': grouped['prize3'][2],
        'prize3_4': grouped['prize3'][3],
        'prize3_5': grouped['prize3'][4],
        'prize3_6': grouped['prize3'][5],
        'prize4_1': grouped['prize4'][0],
        'prize4_2': grouped['prize4'][1],
        'prize4_3': grouped['prize4'][2],
        'prize4_4': grouped['prize4'][3],
        'prize5_1': grouped['prize5'][0],
        'prize5_2': grouped['prize5'][1],
        'prize5_3': grouped['prize5'][2],
        'prize5_4': grouped['prize5'][3],
        'prize5_5': grouped['prize5'][4],
        'prize5_6': grouped['prize5'][5],
        'prize6_1': grouped['prize6'][0],
        'prize6_2': grouped['prize6'][1],
        'prize6_3': grouped['prize6'][2],
        'prize7_1': grouped['prize7'][0],
        'prize7_2': grouped['prize7'][1],
        'prize7_3': grouped['prize7'][2],
        'prize7_4': grouped['prize7'][3],
    }
    all_2d = [flat[k][-2:].zfill(2) for k in FLAT_PRIZE_ORDER]
    return XSMBResult(
        date=day.isoformat(),
        source=url,
        special=flat['special'],
        prize1=flat['prize1'],
        prize2_1=flat['prize2_1'],
        prize2_2=flat['prize2_2'],
        prize3_1=flat['prize3_1'],
        prize3_2=flat['prize3_2'],
        prize3_3=flat['prize3_3'],
        prize3_4=flat['prize3_4'],
        prize3_5=flat['prize3_5'],
        prize3_6=flat['prize3_6'],
        prize4_1=flat['prize4_1'],
        prize4_2=flat['prize4_2'],
        prize4_3=flat['prize4_3'],
        prize4_4=flat['prize4_4'],
        prize5_1=flat['prize5_1'],
        prize5_2=flat['prize5_2'],
        prize5_3=flat['prize5_3'],
        prize5_4=flat['prize5_4'],
        prize5_5=flat['prize5_5'],
        prize5_6=flat['prize5_6'],
        prize6_1=flat['prize6_1'],
        prize6_2=flat['prize6_2'],
        prize6_3=flat['prize6_3'],
        prize7_1=flat['prize7_1'],
        prize7_2=flat['prize7_2'],
        prize7_3=flat['prize7_3'],
        prize7_4=flat['prize7_4'],
        special_2d=flat['special'][-2:].zfill(2),
        all_2d=all_2d,
        fetched_at=datetime.now(TZ).isoformat(timespec='seconds'),
    )


def validate_result(result: XSMBResult) -> None:
    data = asdict(result)
    if not re.fullmatch(r'\d{2}', result.special_2d):
        raise ValueError(f'Invalid special_2d: {result.special_2d}')
    if len(result.all_2d) != 27:
        raise ValueError(f'Expected 27 two-digit prizes, got {len(result.all_2d)}')
    for number in result.all_2d:
        if not re.fullmatch(r'\d{2}', number):
            raise ValueError(f'Invalid two-digit prize: {number}')
    for key in FLAT_PRIZE_ORDER:
        value = data[key]
        if not str(value).isdigit():
            raise ValueError(f'{key} is not numeric: {value}')


def load_history() -> List[dict]:
    if not HISTORY_PATH.exists():
        return []
    return json.loads(HISTORY_PATH.read_text(encoding='utf-8'))


def save_outputs(result: XSMBResult) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    validate_result(result)
    result_dict = asdict(result)

    history = load_history()
    by_date = {item['date']: item for item in history}
    by_date[result.date] = result_dict
    history = [by_date[key] for key in sorted(by_date.keys())]

    HISTORY_PATH.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    LATEST_PATH.write_text(json.dumps(result_dict, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    two_digits = [
        {
            'date': item['date'],
            'special': item['special_2d'],
            **{f'prize_{i + 1:02d}': number for i, number in enumerate(item['all_2d'])},
        }
        for item in history
    ]
    TWO_DIGITS_PATH.write_text(json.dumps(two_digits, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def main() -> None:
    selected_date = datetime.fromisoformat(os.getenv('XSMB_DATE')).date() if os.getenv('XSMB_DATE') else target_date()
    result = fetch_from_xoso_com_vn(selected_date)
    save_outputs(result)
    print(f'Updated XSMB {result.date}: special={result.special}, special_2d={result.special_2d}')


if __name__ == '__main__':
    main()
