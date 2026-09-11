"""Release gates and public verification. No branch is force-pushed by this module."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen
import argparse
import json
import os
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / 'project-docs/grade2/release'
SITE = 'https://matsu71.github.io/Statistics_Blog/'
REPOSITORY = 'Matsu71/Statistics_Blog'
REPORTS.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def write(name, value):
    path = REPORTS / name
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def git(*arguments):
    return subprocess.check_output(['git', *arguments], cwd=ROOT, text=True).strip()


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


class LessonParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lesson_ids = []
        self.question_ids = []
        self.math_errors = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'article' and 'data-lesson-id' in attrs:
            self.lesson_ids.append(attrs['data-lesson-id'])
        if 'data-question' in attrs:
            self.question_ids.append(attrs['data-question'])
        if 'katex-error' in attrs.get('class', '').split():
            self.math_errors += 1


def inspect_lessons():
    result = {}
    for path in sorted((ROOT / 'docs/learn').rglob('index.html')):
        parser = LessonParser()
        parser.feed(path.read_text(encoding='utf-8'))
        if not parser.lesson_ids:
            continue
        if len(parser.lesson_ids) != 1:
            raise ValueError(f'Multiple lesson markers in {path}')
        lesson_id = parser.lesson_ids[0]
        if lesson_id in result or parser.math_errors:
            raise ValueError(f'Duplicate lesson or math error: {lesson_id}')
        if len(parser.question_ids) != len(set(parser.question_ids)):
            raise ValueError(f'Duplicate question in {lesson_id}')
        result[lesson_id] = {'path': str(path.relative_to(ROOT)), 'sha256': file_hash(path),
                             'question_ids': parser.question_ids, 'question_count': len(parser.question_ids)}
    foundation = {key for key in result if re.fullmatch(r'F\d{2}', key)}
    grade2 = {key for key in result if re.fullmatch(r'G\d{2}', key)}
    if foundation != {f'F{i:02}' for i in range(1, 41)}:
        raise ValueError('The 40 foundation lessons must remain present')
    if grade2 != {f'G{i:02}' for i in range(1, 41)}:
        raise ValueError('All 40 grade2 lessons must be rendered')
    if sum(result[k]['question_count'] for k in foundation) != 130:
        raise ValueError('The 130 foundation questions must be preserved')
    if sum(result[k]['question_count'] for k in grade2) != 172:
        raise ValueError('Exactly 172 grade2 questions are required')
    all_questions = [q for item in result.values() for q in item['question_ids']]
    if len(all_questions) != len(set(all_questions)):
        raise ValueError('Question IDs must be unique across both courses')
    return result


def capture():
    if os.environ.get('GITHUB_REPOSITORY', REPOSITORY) != REPOSITORY:
        raise ValueError('This release is restricted to its authorized repository')
    baseline = {str(p.relative_to(ROOT)): file_hash(p) for p in sorted((ROOT / 'src/content/lessons').glob('*.md'))}
    if len(baseline) != 40:
        raise ValueError('Expected 40 foundation manuscripts before release preparation')
    report = {'status': 'captured', 'captured_at': now(),
              'starting_commit': git('rev-parse', 'HEAD'), 'expected_main': git('rev-parse', 'origin/main'),
              'workflow_source_commit': os.environ.get('GITHUB_SHA'),
              'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'foundation_sources': baseline,
              'next': 'Import the real data and run all verification gates.'}
    write('starting-point.json', report)
    print(json.dumps({k:v for k,v in report.items() if k!='foundation_sources'}, ensure_ascii=False))


def marker():
    sources = {str(p.relative_to(ROOT)): file_hash(p) for p in sorted((ROOT / 'src/content/grade2').glob('*.md'))}
    if len(sources) != 40:
        raise ValueError('A release marker cannot be made for an incomplete course')
    count = sum(len(re.findall(r'data-question="G\d{2}-Q\d+"', (ROOT / p).read_text(encoding='utf-8'))) for p in sources)
    if count != 172:
        raise ValueError('A release marker requires all 172 questions')
    data = {'release': 'grade2-1.0', 'source_commit': os.environ.get('GITHUB_SHA', git('rev-parse','HEAD')),
            'workflow_run_id': os.environ.get('GITHUB_RUN_ID'), 'built_at': now(),
            'lesson_count': 40, 'question_count': 172,
            'foundation_lesson_count': 40, 'foundation_question_count': 130,
            'lesson_source_sha256': sources}
    (ROOT/'public/grade2-release-marker.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Created source-bound release marker; no publication has occurred.')


def gate():
    beginning = read('project-docs/grade2/release/starting-point.json')
    for relative, digest in beginning['foundation_sources'].items():
        if file_hash(ROOT / relative) != digest:
            raise ValueError(f'Foundation manuscript changed unexpectedly: {relative}')
    numerical = read('project-docs/grade2/math-validation.json')
    browser = read('project-docs/grade2/browser-validation.json')
    references = read('project-docs/grade2/reference-validation.json')
    iris = read('project-docs/grade2/iris-analysis.json')
    dependencies = read('project-docs/grade2/release/npm-audit.json')
    if numerical.get('status') != 'passed' or set(numerical.get('covered_lessons', [])) != {f'G{i:02}' for i in range(1,41)}:
        raise ValueError('All-lesson numerical checks are incomplete')
    for key, record in numerical['sources'].items():
        if file_hash(ROOT / record['path']) != record['sha256']:
            raise ValueError(f'Numerical evidence predates the current manuscript: {key}')
    if browser.get('status') != 'passed':
        raise ValueError('Grade2 browser checks did not pass')
    if iris.get('status') != 'passed' or file_hash(ROOT/'public/data/grade2-iris.csv') != iris.get('csv_sha256'):
        raise ValueError('Real-data case not verified against current data')
    if references.get('missing_urls') or references.get('status') == 'failed':
        raise ValueError('Missing cited pages remain')
    vulnerabilities = dependencies.get('metadata', {}).get('vulnerabilities')
    if not isinstance(vulnerabilities, dict) or vulnerabilities.get('high', 0) or vulnerabilities.get('critical', 0):
        raise ValueError('Dependency release gate did not pass')
    lessons = inspect_lessons()
    for route in ['docs/courses/grade2/index.html', 'docs/coverage/grade2/index.html', 'docs/grade2-release-marker.json']:
        if not (ROOT / route).is_file():
            raise ValueError(f'Missing release route: {route}')
    manifests = {str(p.relative_to(ROOT)): file_hash(p) for p in sorted((ROOT/'docs').rglob('*')) if p.is_file()}
    report = {'status': 'verified_pending_publication', 'release': 'grade2-1.0', 'checked_at': now(),
              'source_commit': os.environ.get('GITHUB_SHA'), 'workflow_run_id': os.environ.get('GITHUB_RUN_ID'),
              'workflow_url': f"https://github.com/{REPOSITORY}/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}",
              'expected_main': beginning['expected_main'], 'lesson_count': 40, 'question_count': 172,
              'foundation_lesson_count': 40, 'foundation_question_count': 130,
              'numerical_checks': numerical['check_count'], 'math_status': numerical['status'],
              'browser_status': browser['status'], 'browser_report': 'project-docs/grade2/browser-validation.json',
              'references_unconfirmed': references.get('unconfirmed_urls', []),
              'dependency_advisories': vulnerabilities,
              'html_pages': sum(p.endswith('.html') for p in manifests),
              'generated_sha256': manifests, 'lessons': lessons,
              'limitations': ['No independent human mathematical peer review or controlled learning-outcome comparison is claimed.',
                             'Browser automation and screenshots are distinct from human usability evaluation.',
                             'Unavailable external pages are not recorded as newly read.',
                             'Pre-grade1 and grade1 course completion is not included.'],
              'next': 'Publish only this verified artifact without overwriting newer work, then verify the actual public pages.'}
    write('final-gates.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ['generated_sha256','lessons']},ensure_ascii=False,indent=2))


def api(method, endpoint):
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError('Authorized GitHub token is required for the requested publication')
    req = Request('https://api.github.com/repos/'+REPOSITORY+endpoint, method=method,
                  headers={'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.github+json',
                           'User-Agent':'Statistics-Lab-Grade2-Release/1.0'},
                  data=b'{}' if method=='POST' else None)
    with urlopen(req, timeout=30) as response:
        return {'http_status': response.status, 'body': response.read().decode('utf-8')[:2000]}


def public_get(relative, attempts=3):
    public_path = relative.removeprefix('docs/')
    if public_path.endswith('index.html'):
        public_path = public_path[:-len('index.html')]
    url = SITE+quote(public_path,safe='/._-')
    query = '?release_check='+quote(os.environ.get('GITHUB_RUN_ID','manual'))
    error = None
    for attempt in range(attempts):
        try:
            request = Request(url+query, headers={'User-Agent':'Statistics-Lab-Grade2-Integrity/1.0','Accept-Encoding':'identity'})
            with urlopen(request, timeout=25) as response:
                data = response.read()
                if response.status != 200:
                    raise ValueError(f'HTTP {response.status}')
            return url, data, attempt+1
        except Exception as exc:
            error=exc
            if attempt+1<attempts:
                time.sleep(2*(attempt+1))
    raise RuntimeError(f'{url}: {error}')


def publish():
    gates = read('project-docs/grade2/release/final-gates.json')
    if gates['status']!='verified_pending_publication':
        raise ValueError('Verified release gates are required')
    observations={'status':'publication_started_not_yet_verified','started_at':now(),
                  'verified_commit':os.environ.get('GRADE2_VERIFIED_COMMIT'), 'attempts':[]}
    expected_marker=(ROOT/'docs/grade2-release-marker.json').read_bytes()
    try:
        try:
            observations['attempts'].append({'method':'request_pages_build',**api('POST','/pages/builds')})
        except HTTPError as exc:
            # GitHub may have already queued a build. It must still pass live verification below.
            observations['attempts'].append({'method':'request_pages_build','http_status':exc.code,'error':str(exc)})
            if exc.code not in (409,422,429):
                raise
        marker_found=False
        for number in range(60):
            try:
                url,data,_=public_get('docs/grade2-release-marker.json',attempts=1)
                if data==expected_marker:
                    marker_found=True
                    observations['live_marker']=json.loads(data)
                    break
            except Exception as exc:
                observations['last_marker_error']=str(exc)
            time.sleep(5)
        if not marker_found:
            raise ValueError('The newly verified build marker did not become public')
        manifests=gates['generated_sha256']
        tasks=[(p,h) for p,h in manifests.items() if p!='docs/.nojekyll']
        def check_file(item):
            path,expected=item
            result={'path':path,'expected_sha256':expected}
            try:
                url,data,attempts=public_get(path)
                actual=sha256(data).hexdigest()
                result.update(url=url,http_status=200,actual_sha256=actual,bytes=len(data),attempts=attempts)
                if actual!=expected:
                    raise ValueError('Public bytes do not match the verified build')
                if path.startswith('docs/learn/') and path.endswith('index.html'):
                    parsed=LessonParser();parsed.feed(data.decode('utf-8'))
                    if parsed.lesson_ids:
                        if len(parsed.lesson_ids)!=1 or parsed.math_errors:
                            raise ValueError('Live lesson marker or math error')
                        result.update(lesson_id=parsed.lesson_ids[0],question_ids=parsed.question_ids)
                result['status']='passed'
            except Exception as exc:
                result.update(status='failed',error=str(exc))
            return result
        with ThreadPoolExecutor(max_workers=4) as executor:
            resources=list(executor.map(check_file,tasks))
        failures=[r for r in resources if r['status']!='passed']
        live={r['lesson_id']:r for r in resources if 'lesson_id'in r}
        if failures:
            observations['resource_failures']=failures
            raise ValueError(f'{len(failures)} public resources failed verification')
        for lesson_id,expected in gates['lessons'].items():
            if lesson_id not in live or live[lesson_id].get('question_ids')!=expected['question_ids']:
                raise ValueError(f'Published lesson questions differ: {lesson_id}')
        report={'status':'published_and_live_verified','release':'grade2-1.0','completed_at':now(),
                'verified_commit':os.environ.get('GRADE2_VERIFIED_COMMIT'),
                'source_commit':gates['source_commit'], 'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
                'workflow_url':gates['workflow_url'], 'site':SITE+'courses/grade2/',
                'lesson_count':40,'question_count':172,'foundation_lesson_count':40,'foundation_question_count':130,
                'public_html_pages':sum(r['path'].endswith('.html') for r in resources),
                'resources_checked':len(resources),'failures':[],
                'live_marker':observations['live_marker'],'resources':resources,
                'limitations':gates['limitations'],'next':'準1級コースの設計・本文・独自問題の制作。基礎・2級の訂正と利用者による品質確認を継続する。'}
        write('publication.json',report)
        progress=(ROOT/'project-docs/grade2/README.md')
        progress.write_text('# 2級コース：全40講座の公開確認完了\n\n'+report['completed_at']+'\n\n'
                           +'全40講座・172問を検証し、公開中の実ファイルとのハッシュ・講座ID・問題IDの一致を確認しました。基礎40講座・130問も維持しています。\n\n'
                           +'公開コース：https://matsu71.github.io/Statistics_Blog/courses/grade2/\n\n'
                           +'検証の正本：[公開前](release/final-gates.json) ／ [公開後](release/publication.json)。個別の数値・ブラウザ・参照先・実データの記録も同フォルダ群に保持します。\n\n'
                           +'[全件の編集上の点検](03-full-course-review.md) ／ [比較と改善](04-comparison-and-remediation.md)。\n\n'
                           +'**次の制作対象は準1級コースです。** 受験時期に対応する公式範囲を確認し、前提数学・手法選択・独自問題・詳細な導出を同じ品質基準で実装します。基礎と2級の訂正対応と、実際の利用者による理解・操作の確認を並行する品質向上課題とします。\n\n'
                           +'独立した人間の数学監修、学習効果の比較実験、準1級・1級の全講座の制作は今回の完了範囲に含みません。手動の確認マークを習得・合格の自動判定とは表示しません。\n',encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k!='resources'},ensure_ascii=False,indent=2))
    except Exception as exc:
        observations.update(status='failed_or_unconfirmed',observed_at=now(),error=str(exc),
                            next='Inspect the recorded failing gate and preserve the last verified public version.')
        write('publication-attempt.json',observations)
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['capture','marker','gate','publish'])
    arguments=parser.parse_args()
    globals()[arguments.action]()
