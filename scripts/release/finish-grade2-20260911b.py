"""Finish an existing, complete G01-G40 course; never synthesize missing lessons.

Invoked by a narrowly scoped GitHub workflow. Every check records its real result.
A source or verification failure never advances main. Parallel main work is preserved.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen
import json
import os
import re
import subprocess
import sys
import time

REPO = 'Matsu71/Statistics_Blog'
SITE = 'https://matsu71.github.io/Statistics_Blog/'
WORK = 'content/grade2-complete-20260911'
RUN = os.environ.get('GITHUB_RUN_ID', 'local')
TOKEN = os.environ.get('GH_TOKEN', '')
OUT = Path('project-docs/grade2/final-release')
ASSETS = Path('review-assets/grade2/final-release')
STATE = {'status': 'in_progress', 'run_id': RUN,
         'workflow_url': f'https://github.com/{REPO}/actions/runs/{RUN}',
         'started_at': datetime.now(timezone.utc).isoformat(), 'steps': [],
         'scope': 'grade2', 'limits': [
             'Independent numerical calculations do not constitute independent human mathematical peer review.',
             'Browser automation does not establish measured learning effectiveness or superiority to competitors.',
             'This release does not implement the future pre-1 and grade-1 courses.']}


def write_state():
    OUT.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    text = json.dumps(STATE, ensure_ascii=False, indent=2) + '\n'
    (OUT/'status.json').write_text(text, encoding='utf-8')
    (ASSETS/'status.json').write_text(text, encoding='utf-8')


def api(endpoint, method='GET', payload=None):
    if not TOKEN:
        raise RuntimeError('Authorized workflow token is required; no alternate credentials are searched.')
    headers = {'Authorization': f'Bearer {TOKEN}', 'Accept': 'application/vnd.github+json',
               'X-GitHub-Api-Version': '2022-11-28', 'User-Agent': 'Statistics-Grade2-Release'}
    data = None if payload is None else json.dumps(payload).encode()
    req = Request('https://api.github.com/repos/'+REPO+'/'+endpoint,
                  data=data, headers=headers, method=method)
    with urlopen(req, timeout=45) as response:
        body = response.read()
        return json.loads(body) if body else {}


def command(label, args, timeout=600):
    ASSETS.mkdir(parents=True, exist_ok=True)
    log = ASSETS/(re.sub(r'[^a-z0-9_-]+', '-', label.lower())+'.log')
    begin = time.monotonic()
    with log.open('w', encoding='utf-8') as stream:
        process = subprocess.run(args, stdout=stream, stderr=subprocess.STDOUT,
                                 timeout=timeout, env={**os.environ, 'ASTRO_TELEMETRY_DISABLED': '1'})
    step = {'name': label, 'returncode': process.returncode,
            'seconds': round(time.monotonic()-begin, 2), 'log': str(log)}
    STATE['steps'].append(step)
    write_state()
    if process.returncode:
        tail = log.read_text(encoding='utf-8', errors='replace')[-12000:]
        print(tail, flush=True)
        raise RuntimeError(f'{label} failed; see {log}')
    print(f'PASS: {label}', flush=True)


def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()


def inventory(directory, prefix):
    result = []
    for file in sorted(Path(directory).glob('*.md')):
        text = file.read_text(encoding='utf-8')
        found = re.search(r'^lesson_id:\s*('+prefix+r'\d{2})\s*$', text, re.M)
        if not found:
            raise AssertionError(f'Unrecognized lesson: {file}')
        match = re.search(r'^slug:\s*([a-z0-9-]+)\s*$', text, re.M)
        if not match:
            raise AssertionError(f'Missing slug: {file}')
        questions = re.findall(r'data-question=[\"\x27]('+prefix+r'\d{2}-Q\d+)[\"\x27]', text)
        for heading in ['## 確認問題','## 詳しく確かめる','## まとめと次の一歩','## 出典・関連資料']:
            if heading not in text:
                raise AssertionError(f'{file}: missing {heading}')
        result.append({'id': found[1], 'slug': match[1], 'path': str(file),
                       'questions': questions, 'source_sha256': sha256(file.read_bytes()).hexdigest()})
    result.sort(key=lambda item: item['id'])
    return result


def has_complete_course(ref):
    listing = git('ls-tree', '-r', '--name-only', ref, '--', 'src/content/grade2')
    return len([x for x in listing.splitlines() if x.endswith('.md')]) == 40


class Markers(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lesson_ids = []
        self.questions = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-lesson-id' in attrs:
            self.lesson_ids.append(attrs['data-lesson-id'])
        if 'data-question' in attrs:
            self.questions.append(attrs['data-question'])


def fetch_public(path):
    url = SITE+quote(path, safe='/')+'?grade2_release='+RUN
    last = None
    for attempt in range(3):
        try:
            req = Request(url, headers={'User-Agent': 'Statistics-Grade2-Public-Verification',
                                        'Accept-Encoding': 'identity'})
            with urlopen(req, timeout=35) as response:
                data = response.read()
                if response.status != 200:
                    raise AssertionError(f'{url}: HTTP {response.status}')
            return data
        except Exception as error:
            last = error
            if attempt < 2:
                time.sleep(2**(attempt+1))
    raise RuntimeError(f'Could not verify {url}: {last}')


def verify_public_resource(item):
    path, expected = item
    route = path.removeprefix('docs/')
    if route.endswith('index.html'):
        route = route[:-10]
    data = fetch_public(route)
    actual = sha256(data).hexdigest()
    if actual != expected:
        raise AssertionError(f'Published content differs from tested artifact: {path}')
    result = {'path': path, 'url': SITE+route, 'http_status': 200,
              'sha256': actual, 'bytes': len(data)}
    if '/learn/grade2/' in path and path.endswith('.html'):
        parser = Markers()
        parser.feed(data.decode('utf-8'))
        if len(parser.lesson_ids) != 1 or not parser.lesson_ids[0].startswith('G'):
            raise AssertionError(f'Incorrect public lesson marker: {path}')
        result['lesson_id'] = parser.lesson_ids[0]
        result['question_ids'] = parser.questions
    return result


def main():
    write_state()
    command('fetch-current-branches', ['git','fetch','origin','main',WORK], 180)
    initial_main = git('rev-parse', 'FETCH_HEAD') if False else api('git/ref/heads/main')['object']['sha']
    candidate = api('git/ref/heads/'+WORK)['object']['sha']
    command('fetch-exact-inputs', ['git','fetch','origin',initial_main,candidate], 180)
    # A finished newer main is authoritative. Never roll it back to an older work branch.
    if has_complete_course(initial_main):
        selected = initial_main
        reason = 'main already contains all 40 grade2 sources; verify and preserve current main'
    else:
        if subprocess.run(['git','merge-base','--is-ancestor',initial_main,candidate]).returncode:
            raise RuntimeError('Main contains parallel work not in the grade2 candidate. Reconcile rather than overwrite.')
        selected = candidate
        reason = 'grade2 candidate descends from current main'
    STATE.update(initial_main=initial_main, selected_source=selected, selection_reason=reason)
    # Python has loaded this program before checkout; changing the worktree cannot change its execution.
    command('checkout-selected-source', ['git','checkout','--detach',selected], 120)
    write_state()
    required = ['scripts/prepare-grade2.mjs','scripts/validate-grade2.mjs',
                'scripts/check-grade2-math.py','scripts/test-grade2-browser.mjs']
    for name in required:
        if not Path(name).is_file():
            raise RuntimeError(f'Missing prepared verification source: {name}')
    if Path('scripts/import-grade2-iris.py').exists():
        command('retrieve-pinned-real-data', ['python3','scripts/import-grade2-iris.py'], 240)
    command('install-locked-node-dependencies', ['npm','ci'], 420)
    command('prepare-existing-grade2-sources', ['node','scripts/prepare-grade2.mjs'], 180)
    grade2 = inventory('src/content/grade2','G')
    foundation = inventory('src/content/lessons','F')
    assert [x['id'] for x in grade2] == [f'G{i:02d}' for i in range(1,41)], 'Missing grade2 lessons; no placeholder substitution'
    assert [x['id'] for x in foundation] == [f'F{i:02d}' for i in range(1,41)], 'Foundation sources must remain intact'
    for lesson in grade2:
        count = 16 if lesson['id']=='G40' else 4
        assert lesson['questions'] == [f"{lesson['id']}-Q{i}" for i in range(1,count+1)], f"Incomplete questions: {lesson['id']}"
    assert sum(len(x['questions']) for x in grade2) == 172
    STATE.update(lesson_count=40, question_count=172, source_inventory=grade2,
                 foundation_lesson_count=len(foundation))
    state_path = Path('src/data/grade2-release.json')
    data = json.loads(state_path.read_text())
    data.update(stage='release_candidate',authored_through='G40',authored_lessons=40,
                authored_questions=172,next='Run all gates, then verify the actual public release.')
    state_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    command('prepare-complete-release', ['node','scripts/prepare-grade2.mjs'], 180)
    command('generate-dictionary-index', ['npm','run','generate:index'], 120)
    command('verify-source-types-build-links', ['npm','run','verify'], 600)
    for name in ['validate-foundation.mjs','test-foundation-math.mjs','test-release-extras.mjs','validate-grade2.mjs']:
        command(name.removesuffix('.mjs'), ['node','scripts/'+name], 240)
    command('install-independent-numerical-library', ['python3','-m','pip','install','--quiet','scipy'], 300)
    command('independent-grade2-numerical-validation', ['python3','scripts/check-grade2-math.py'], 300)
    audit = subprocess.run(['npm','audit','--json'],capture_output=True,text=True,timeout=120)
    try:
        metadata = json.loads(audit.stdout)
        severities = metadata['metadata']['vulnerabilities']
    except Exception as error:
        raise RuntimeError('Dependency audit returned no usable evidence') from error
    (OUT/'dependency-audit.json').write_text(json.dumps(metadata,indent=2)+'\n')
    assert not severities.get('high') and not severities.get('critical'), 'Unresolved high/critical dependency advisory'
    STATE['dependency_advisories'] = severities
    command('install-browser-test-library',['npm','install','--no-save','--package-lock=false','playwright@1.55.0'],300)
    command('install-test-browsers',['npx','playwright','install','--with-deps','chromium','webkit'],600)
    for name in ['test-foundation-browser.mjs','test-learning-labs.mjs','test-grade2-browser.mjs']:
        command(name.removesuffix('.mjs'),['node','scripts/'+name],900)
    content = json.loads(Path('project-docs/grade2/content-validation.json').read_text())
    maths = json.loads(Path('project-docs/grade2/math-validation.json').read_text())
    browser = json.loads(Path('project-docs/grade2/browser-validation.json').read_text())
    assert content.get('authored_lessons') == 40 and content.get('original_questions') == 172
    assert maths.get('status') == 'passed' and browser.get('status') == 'passed'
    checked = maths.get('lessons_checked',[])
    assert set(checked) == {f'G{i:02d}' for i in range(1,41)}, 'Every lesson needs numerical evidence'
    assert all(row.get('status') == 'implemented' for row in content.get('coverage',[]))
    STATE.update(numerical_checks=maths.get('numerical_checks'),browser_assertions=browser.get('assertions'),
                 status='verified_pending_publication')
    marker_file = Path('docs/grade2-build.json')
    assert marker_file.exists(), 'Missing generated public marker'
    marker = json.loads(marker_file.read_text())
    assert marker.get('lesson_count') == 40 and marker.get('question_count') == 172
    STATE['build_marker'] = marker
    fingerprints = {str(p):sha256(p.read_bytes()).hexdigest() for p in Path('docs').rglob('*')
                    if p.is_file() and p.name!='.nojekyll'}
    STATE['generated_fingerprints'] = fingerprints
    write_state()
    command('configure-commit-name',['git','config','user.name','github-actions[bot]'],30)
    command('configure-commit-email',['git','config','user.email','41898282+github-actions[bot]@users.noreply.github.com'],30)
    command('stage-verified-artifact',['git','add','-A','--','docs','src','public','scripts','project-docs/grade2','package.json','package-lock.json'],60)
    if subprocess.run(['git','diff','--cached','--quiet']).returncode:
        command('commit-verified-artifact',['git','commit','-m','release: save fully tested grade2 course and exact verification evidence [skip ci]'],120)
    verified = git('rev-parse','HEAD')
    release_branch = 'release/grade2-audited-'+RUN
    command('save-isolated-release',['git','push','origin','HEAD:refs/heads/'+release_branch],120)
    now_main = api('git/ref/heads/main')['object']['sha']
    command('fetch-main-before-publication',['git','fetch','origin',now_main],120)
    if subprocess.run(['git','merge-base','--is-ancestor',now_main,verified]).returncode:
        raise RuntimeError('Main advanced independently; verified branch saved but main was not overwritten.')
    command('fast-forward-main-without-force',['git','push','origin','HEAD:refs/heads/main'],120)
    STATE.update(verified_commit=verified,release_branch=release_branch,status='published_waiting_for_live_verification')
    write_state()
    try:
        requested = api('pages/builds','POST',{})
        STATE['pages_request'] = {'accepted':True,'status':requested.get('status')}
    except HTTPError as error:
        # A commit can already have triggered a Pages build. Continue only to observe live bytes.
        STATE['pages_request'] = {'accepted':False,'http_status':error.code}
    for attempt in range(60):
        try:
            if json.loads(fetch_public('grade2-build.json')) == marker:
                break
        except Exception:
            pass
        if attempt == 59:
            raise RuntimeError('Published marker did not match the tested build within the observation window.')
        time.sleep(10)
    with ThreadPoolExecutor(max_workers=4) as pool:
        resources = list(pool.map(verify_public_resource, fingerprints.items()))
    lessons = [row for row in resources if row.get('lesson_id')]
    ids = [row['lesson_id'] for row in lessons]
    questions = [q for row in lessons for q in row['question_ids']]
    assert len(ids) == 40 and set(ids) == {f'G{i:02d}' for i in range(1,41)}
    assert len(questions) == len(set(questions)) == 172
    STATE.update(status='published_and_live_verified',completed_at=datetime.now(timezone.utc).isoformat(),
                 html_pages=sum(x['path'].endswith('.html') for x in resources),
                 resources_verified=len(resources),live_lessons=lessons,
                 next='準1級コースの範囲版を確認し、同じ品質基準で設計・制作する。基礎と2級の利用者テスト・訂正対応も行う。')
    write_state()
    (OUT/'publication.json').write_text(json.dumps(STATE,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'README.md').write_text(
        '# 2級コース：全件検証と公開後の照合完了\n\n'
        '全40講座・172問について、既存原稿の全件構造・数値・範囲対応・ブラウザ・基礎コースの回帰検証を実行し、公開したファイルを検証済み生成物のハッシュと照合しました。\n\n'
        '実際の実行結果はpublication.jsonを参照してください。自動テストは独立した人間の数学監修や、競合との学習効果の比較実験を意味しません。\n\n'
        '**次の作業**：準1級の範囲版と前提を確認し、同じ品質基準で講座を制作します。公開済み基礎・2級の利用者テストと訂正対応は継続的な品質向上課題です。\n',encoding='utf-8')
    command('stage-publication-evidence',['git','add','project-docs/grade2/final-release'],60)
    command('commit-publication-evidence',['git','commit','-m','docs: record verified grade2 publication and next work [skip ci]'],120)
    command('checkpoint-publication-branch',['git','push','origin','HEAD:refs/heads/'+release_branch],120)
    try:
        command('checkpoint-publication-main',['git','push','origin','HEAD:refs/heads/main'],120)
    except Exception:
        STATE['evidence_note'] = 'Publication passed; main moved before evidence-only commit. Evidence remains on the release branch and workflow artifact.'
        write_state()
    print(json.dumps({k:v for k,v in STATE.items() if k not in ['source_inventory','generated_fingerprints','live_lessons','steps']},ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        STATE.update(status='failed_or_interrupted',error=str(error),
                     stopped_at=datetime.now(timezone.utc).isoformat(),
                     next='Read the recorded failing step, fix that source or test issue, and rerun without lowering the quality gate.')
        write_state()
        print(json.dumps(STATE,ensure_ascii=False,indent=2),flush=True)
        raise
