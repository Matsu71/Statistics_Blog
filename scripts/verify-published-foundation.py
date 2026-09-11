"""Recheck published bytes against the successful release, without changing the site."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
import json
import os
import time

ROOT = Path.cwd()
OUT = ROOT / 'project-docs/foundation-release/postrelease-integrity.json'
BASE = 'https://matsu71.github.io/Statistics_Blog/'

class LessonParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lessons: list[str] = []
        self.questions: list[str] = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-lesson-id' in attrs:
            self.lessons.append(attrs['data-lesson-id'])
        if 'data-question' in attrs:
            self.questions.append(attrs['data-question'])

def check_one(item):
    relative, expected = item
    public_path = relative.removeprefix('docs/')
    if public_path.endswith('index.html'):
        public_path = public_path[:-len('index.html')]
    url = BASE + public_path
    result = {'path': relative, 'url': url, 'expected_sha256': expected}
    # A deployment in flight or transient network failure is retried, never marked as passed.
    for attempt in range(3):
        try:
            request = Request(url + '?integrity=' + os.environ.get('GITHUB_RUN_ID', 'manual'),
                              headers={'User-Agent': 'Statistics-Lab-Public-Integrity/1.0',
                                       'Accept-Encoding': 'identity'})
            with urlopen(request, timeout=30) as response:
                data = response.read()
                result['http_status'] = response.status
            actual = sha256(data).hexdigest()
            result.update(actual_sha256=actual, bytes=len(data), attempts=attempt + 1)
            if result['http_status'] != 200 or actual != expected:
                raise ValueError('Published bytes do not match the verified release')
            if relative.startswith('docs/learn/') and relative.endswith('index.html'):
                parser = LessonParser()
                parser.feed(data.decode('utf-8'))
                if len(parser.lessons) != 1:
                    raise ValueError('Expected exactly one lesson marker')
                result.update(lesson_id=parser.lessons[0], question_ids=parser.questions)
                if 'katex-error' in data.decode('utf-8'):
                    raise ValueError('Math rendering error in live page')
            if public_path == 'foundation-build.json':
                result['marker'] = json.loads(data)
            result['status'] = 'passed'
            result.pop('error', None)
            return result
        except Exception as exc:
            result.update(status='failed', error=str(exc), attempts=attempt + 1)
            if attempt < 2:
                time.sleep(2 ** (attempt + 1))
    return result

def main():
    gates = json.loads((ROOT / 'project-docs/foundation-release/final-gates.json').read_text())
    publication = json.loads((ROOT / 'project-docs/foundation-release/publication.json').read_text())
    assert publication['status'] == 'published_and_live_verified'
    assert gates['math_status'] == gates['browser_status'] == 'passed'
    expected_marker = publication['publication']['live_marker']
    assert expected_marker['source_commit'] == gates['source_commit']
    entries = []
    for relative, digest in gates['generated_sha256'].items():
        local = ROOT / relative
        assert local.is_file(), f'Missing committed file: {relative}'
        assert sha256(local.read_bytes()).hexdigest() == digest, f'Changed release file: {relative}'
        if relative != 'docs/.nojekyll':  # Build control file, not a public learning resource.
            entries.append((relative, digest))
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(check_one, entries))
    failures = [r for r in results if r['status'] != 'passed']
    lessons = [r for r in results if r.get('lesson_id')]
    ids = [r['lesson_id'] for r in lessons]
    questions = [q for r in lessons for q in r.get('question_ids', [])]
    markers = [r['marker'] for r in results if 'marker' in r]
    checks = {
        'all_resources_match': not failures,
        'all_40_lesson_ids': len(ids) == 40 and set(ids) == {f'F{i:02d}' for i in range(1, 41)},
        'all_130_unique_questions': len(questions) == len(set(questions)) == 130,
        'exact_public_marker': len(markers) == 1 and markers[0] == expected_marker,
        'committed_release_hashes': True,
    }
    report = {
        'status': 'passed' if all(checks.values()) else 'failed',
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'checked_repository_commit': os.environ.get('GITHUB_SHA'),
        'released_source_commit': gates['source_commit'],
        'workflow_run_id': os.environ.get('GITHUB_RUN_ID'),
        'workflow_url': f"https://github.com/Matsu71/Statistics_Blog/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}",
        'html_pages': sum(r['path'].endswith('.html') for r in results),
        'resources_checked': len(results), 'lesson_count': len(lessons),
        'question_count': len(questions), 'checks': checks,
        'failures': failures, 'resources': results,
        'limits': ['This recheck verifies deployed bytes and structure, not new mathematical peer review.',
                   'The earlier successful release tests and competitor review remain separate evidence.',
                   'No user data, account state, or remote service settings were changed.'],
        'next': '基礎コースの利用者テスト・訂正対応と、同じ品質基準による2級コースの実装。',
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k != 'resources'}, ensure_ascii=False, indent=2))
    if report['status'] != 'passed':
        raise SystemExit(1)
    progress = ROOT / 'project-docs/learning-platform-design/11-completion-progress.md'
    old = progress.read_text(encoding='utf-8')
    marker = '<!-- FOUNDATION_PUBLIC_INTEGRITY_20260911 -->'
    if marker not in old:
        header = (marker + '\n# 公開後の再確認まで完了\n\n'
                  + report['checked_at'] + '\n\n'
                  + f"全{report['html_pages']}公開HTMLページを含む{len(results)}ファイルを、検証済み生成物のSHA-256と照合しました。"
                  + '全40講座・130問、配信ビルド識別子の一致を確認しました。\n\n'
                  + '詳細：`project-docs/foundation-release/postrelease-integrity.json`。'
                  + '公開状態の正本は`publication.json`とこの再確認記録です。'
                  + '`src/data/foundation-release.json`のrelease_candidateはビルド時点の仕様であり、現在も未公開という意味ではありません。\n\n'
                  + '**次に行うこと**：基礎の利用者テスト・訂正対応と、同じ品質基準で2級コースを制作します。'
                  + '独立した人間の数学監修・学習効果の比較実験は未実施であり、今回の完了範囲に含めません。\n\n---\n\n')
        progress.write_text(header + old, encoding='utf-8')

if __name__ == '__main__':
    main()
