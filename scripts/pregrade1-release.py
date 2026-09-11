"""Bind tests to the initial course artifact and separately verify the live site."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request,urlopen
import argparse,json,os,subprocess,time

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/'project-docs/pregrade1/release'
SITE='https://matsu71.github.io/Statistics_Blog/'

def now():return datetime.now(timezone.utc).isoformat()
def load(path):return json.loads(path.read_text(encoding='utf-8'))
def digest(path):return sha256(path.read_bytes()).hexdigest()
def save(name,data):
    REPORT.mkdir(parents=True,exist_ok=True)
    (REPORT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT).decode().strip()

def capture():
    paths=[p for directory in ['src/content/lessons','src/content/grade2'] for p in (ROOT/directory).glob('*.md')]
    assert len(paths)==80
    source_hashes={p.relative_to(ROOT).as_posix():digest(p) for p in paths}
    save('starting-point.json',{'status':'captured','at':now(),'expected_main':git('rev-parse','origin/main'),
        'source_commit':os.environ.get('GITHUB_SHA'),'preserved_manuscripts':source_hashes})

def gate():
    start=load(REPORT/'starting-point.json');content=load(ROOT/'project-docs/pregrade1/checks/content.json')
    numeric=load(ROOT/'project-docs/pregrade1/checks/math.json');browser=load(ROOT/'project-docs/pregrade1/checks/browser.json')
    for report in [content,numeric,browser]:
        assert report['status']=='passed'
        assert report['source_commit']==os.environ['GITHUB_SHA'],'Evidence from another source commit'
    assert content['lesson_count']==6 and content['question_count']==24 and content['planned_lessons']==72
    for record in content['records']:
        assert digest(ROOT/record['path'])==record['source_sha256']==numeric['sources'][record['id']]['sha256']
        assert digest(ROOT/f"docs/learn/pregrade1/{record['slug']}/index.html")==record['html_sha256']
    for path,h in start['preserved_manuscripts'].items():assert digest(ROOT/path)==h,f'Existing manuscript changed: {path}'
    for path in ['project-docs/learning-platform-design/10-foundation-validation.json','project-docs/grade2/browser-validation.json','project-docs/grade2/math-validation.json']:
        assert load(ROOT/path)['status']=='passed',f'Missing regression result {path}'
    audit=load(REPORT/'npm-audit.json')
    assert audit['metadata']['vulnerabilities']['high']==audit['metadata']['vulnerabilities']['critical']==0
    files={p.relative_to(ROOT).as_posix():digest(p) for p in sorted((ROOT/'docs').rglob('*')) if p.is_file()}
    save('final-gates.json',{'status':'verified_pending_promotion','checked_at':now(),'source_commit':os.environ['GITHUB_SHA'],
        'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'lesson_count':6,'question_count':24,'planned_lessons':72,
        'numerical_checks':numeric['numerical_checks'],'browser_assertions':browser['assertions'],
        'preserved_lessons':80,'preserved_questions':302,'html_pages':sum(p.endswith('.html') for p in files),
        'generated_sha256':files,'marker':load(ROOT/'docs/pregrade1-build.json'),
        'next':'Check the saved candidate, promote without force, verify the actual delivery, then author P07 onward.',
        'limits':['This initial release does not complete the 72-lesson plan.','Numerical and browser checks are not independent human mathematical peer review.','External user studies have not been performed.']})
    print(f"Bound {len(files)} generated files to passing checks. Existing 80 manuscripts unchanged.")

class LessonParser(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.questions=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'data-lesson-id'in a:self.ids.append(a['data-lesson-id'])
        if 'data-question'in a:self.questions.append(a['data-question'])

def fetch(relative):
    p=relative.removeprefix('docs/')
    if p.endswith('index.html'):p=p[:-10]
    url=SITE+p
    request=Request(url+'?verify='+os.environ.get('GITHUB_RUN_ID','local'),headers={'User-Agent':'Statistics-Lab-Public-Verification/1.0','Accept-Encoding':'identity'})
    with urlopen(request,timeout=30) as response:
        assert response.status==200
        return url,response.read()

def public():
    gates=load(REPORT/'final-gates.json')
    for path,h in gates['generated_sha256'].items():assert digest(ROOT/path)==h,'Committed output no longer matches passing artifact'
    expected=(ROOT/'docs/pregrade1-build.json').read_bytes()
    for attempt in range(75):
        try:
            _,data=fetch('docs/pregrade1-build.json')
            if data==expected:break
        except Exception:pass
        time.sleep(5)
    else:raise RuntimeError('The exact promoted marker has not yet reached the public site')
    def one(item):
        path,h=item
        error=None
        for attempt in range(3):
            try:
                url,data=fetch(path);assert sha256(data).hexdigest()==h,'Public hash differs'
                result={'path':path,'url':url,'http_status':200,'sha256':h,'status':'passed'}
                if path.startswith('docs/learn/')and path.endswith('.html'):
                    parser=LessonParser();parser.feed(data.decode('utf-8'))
                    assert len(parser.ids)==1 and 'katex-error'not in data.decode('utf-8')
                    result.update(lesson_id=parser.ids[0],question_ids=parser.questions)
                return result
            except Exception as exc:
                error=exc;time.sleep(attempt+1)
        raise RuntimeError(f'{path}: {error}')
    with ThreadPoolExecutor(max_workers=4)as executor:
        resources=list(executor.map(one,[(p,h)for p,h in gates['generated_sha256'].items()if p!='docs/.nojekyll']))
    lessons=[r for r in resources if'lesson_id'in r]
    expected_ids={f'{prefix}{i:02}'for prefix in ['F','G']for i in range(1,41)}|{f'P{i:02}'for i in range(1,7)}
    assert {r['lesson_id']for r in lessons}==expected_ids and len(lessons)==86
    q=[q for r in lessons for q in r['question_ids']];assert len(q)==len(set(q))==326
    report={'status':'published_and_live_verified','checked_at':now(),'verified_commit':os.environ.get('GITHUB_SHA'),
        'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),'source_commit':gates['source_commit'],
        'lesson_count':6,'question_count':24,'planned_lessons':72,'total_lessons':86,'total_questions':326,
        'resources_verified':len(resources),'html_pages':gates['html_pages'],
        'numerical_checks':gates['numerical_checks'],'browser_assertions':gates['browser_assertions'],
        'resources':resources,'next':'P07の極限定理・デルタ法を制作し、P08以降の分布へ進む。残る66講座と1級は未完成。',
        'limits':gates['limits']}
    save('publication.json',report)
    path=ROOT/'project-docs/pregrade1/README.md';old=path.read_text(encoding='utf-8');marker='<!-- PRE1_FIRST_SIX_PUBLIC -->'
    if marker not in old:
        header=marker+'\n# 初期6講座・24問の公開確認完了\n\n'
        header+='P01〜P06をmainへ反映し、公開された全86講座・326問と全配信ファイルの一致を確認しました。基礎・2級の原稿は変更していません。\n\n'
        header+='正本：[公開確認](release/publication.json)・[検証結果](release/final-gates.json)。全72講座が完成したわけではなく、残る66講座は準備中です。\n\n'
        header+='**次の制作対象はP07（連続写像・スルツキー・デルタ法と極値）と、P08以降の分布です。**\n\n---\n\n'
        path.write_text(header+old,encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items()if k!='resources'},ensure_ascii=False,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=['capture','gate','public'])
    {'capture':capture,'gate':gate,'public':public}[parser.parse_args().phase]()
