"""Check cited destinations; distinguish a missing page from blocked or unavailable retrieval."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html import unescape
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen
import json
import re
import time

ROOT = Path(__file__).resolve().parents[1]
references = {}
for path in sorted((ROOT / 'src/content/grade2').glob('*.md')):
    text = path.read_text(encoding='utf-8')
    for label, url in re.findall(r'\[([^\]]+)\]\((https://[^\s)]+)\)', text):
        split = urlsplit(url)
        canonical = urlunsplit((split.scheme, split.netloc, split.path, split.query, ''))
        entry = references.setdefault(canonical, {'url': canonical, 'citations': []})
        entry['citations'].append({'path': str(path.relative_to(ROOT)), 'label': label})


def fetch(item):
    result = dict(item)
    for attempt in range(3):
        try:
            req = Request(item['url'], headers={'User-Agent': 'Statistics-Lab-Reference-Check/1.0',
                                               'Accept': 'text/html,application/pdf;q=0.9,*/*;q=0.5'})
            with urlopen(req, timeout=25) as response:
                data = response.read(2_000_001)
                result.update(http_status=response.status, final_url=response.url,
                              content_type=response.headers.get('Content-Type', ''),
                              bytes_read=len(data), attempts=attempt + 1)
            if len(data) > 2_000_000:
                result['content_hash_scope'] = 'first 2000001 bytes only'
            else:
                result['content_hash_scope'] = 'complete response body'
            result['response_sha256'] = sha256(data).hexdigest()
            if 'html' in result['content_type']:
                title = re.search(rb'<title[^>]*>([\s\S]*?)</title>', data, re.I)
                if title:
                    result['title'] = unescape(re.sub('<[^>]+>', '', title[1].decode('utf-8', errors='replace'))).strip()[:300]
            result['status'] = 'reachable'
            return result
        except HTTPError as exc:
            result.update(http_status=exc.code, attempts=attempt + 1, error=str(exc))
            if exc.code in (404, 410):
                result['status'] = 'missing'
                if attempt < 2:
                    time.sleep(1 + attempt)
                    continue
                return result
            if exc.code in (401, 403):
                result['status'] = 'retrieval_blocked_not_content_verified'
                return result
        except (URLError, TimeoutError, OSError) as exc:
            result.update(error=str(exc), attempts=attempt + 1)
        if attempt < 2:
            time.sleep(1 + attempt)
    result['status'] = 'retrieval_unconfirmed'
    return result

with ThreadPoolExecutor(max_workers=4) as pool:
    records = sorted(pool.map(fetch, references.values()), key=lambda x: x['url'])
missing = [r['url'] for r in records if r['status'] == 'missing']
unconfirmed = [r['url'] for r in records if r['status'] != 'reachable']
report = {'status': 'failed' if missing else 'passed_with_retrieval_limits' if unconfirmed else 'passed',
          'checked_at': datetime.now(timezone.utc).isoformat(),
          'unique_urls': len(records), 'missing_urls': missing, 'unconfirmed_urls': unconfirmed,
          'records': records,
          'limits': ['HTTP success and a matching title establish reachability, not a full mathematical source audit.',
                     'Blocked or unconfirmed pages are not described as newly read or verified.',
                     'PDF availability is not evidence that its tables were visually inspected by this script.']}
out = ROOT / 'project-docs/grade2/reference-validation.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({k: v for k, v in report.items() if k != 'records'}, ensure_ascii=False, indent=2))
if missing:
    raise SystemExit('At least one cited page is missing; correct its citation before release.')
