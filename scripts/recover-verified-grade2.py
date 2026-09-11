"""Recover a previously tested artifact and separately verify public delivery.

No manuscript is generated and no test success is fabricated here. The artifact
is tied to its actual numerical/browser reports and every generated-file hash.
Only the working branch is checkpointed; promotion to main is a separate action.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from urllib.request import Request, urlopen
import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import tarfile
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPO = 'Matsu71/Statistics_Blog'
ARTIFACT = 10195520868
ARTIFACT_SHA = '58b1645a7db7ba149bccdad1e1836582137f5703cecf41208ba2e8012a2680b2'
TEST_SOURCE = 'e05ccb06ffacd982c98d083f9b28067b727341bf'
EXPECTED_MAIN = '907657df5aa273b1a8d69e393c2b1dff6dccff8b'
REPORTS = ROOT / 'project-docs/grade2/release'
SITE = 'https://matsu71.github.io/Statistics_Blog/'


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def now():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()


def save(name, report):
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / name).write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def recover():
    git('fetch', 'origin', 'main:refs/remotes/origin/main')
    assert git('rev-parse', 'origin/main') == EXPECTED_MAIN, 'Reconcile newer main before restoration'
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        archive = temp / 'artifact.zip'
        with archive.open('wb') as output:
            subprocess.run(['gh', 'api', f'repos/{REPO}/actions/artifacts/{ARTIFACT}/zip'], stdout=output, check=True)
        assert digest(archive) == ARTIFACT_SHA, 'Artifact bytes changed'
        with zipfile.ZipFile(archive) as z:
            member = 'review-assets/grade2-resume/source-review.tar.gz'
            tar_path = temp / 'source.tar.gz'
            tar_path.write_bytes(z.read(member))
        snapshot = temp / 'source'
        snapshot.mkdir()
        with tarfile.open(tar_path) as t:
            t.extractall(snapshot, filter='data')
        gates = load(snapshot/'project-docs/grade2/release/final-gates.json')
        review = load(snapshot/'project-docs/grade2/review-workspace.json')
        math = load(snapshot/'project-docs/grade2/math-validation.json')
        browser = load(snapshot/'project-docs/grade2/browser-validation.json')
        assert gates['source_commit'] == TEST_SOURCE and gates['workflow_run_id'] == '34589747612'
        assert gates['math_status'] == gates['browser_status'] == math['status'] == browser['status'] == 'passed'
        assert gates['lesson_count'] == 40 and gates['question_count'] == 172
        assert review['status'] == 'verified_candidate_sealed'
        assert review['final_gates_sha256'] == digest(snapshot/'project-docs/grade2/release/final-gates.json')
        for record in review['records']:
            for folder in ['src/content/grade2', 'review/grade2/20260911/candidate', 'review/grade2/20260911/verified']:
                assert digest(snapshot/folder/record['name']) == record['candidate_sha256']
            assert math['sources'][record['id']]['sha256'] == record['candidate_sha256']
        beginning = load(snapshot/'project-docs/grade2/release/starting-point.json')
        for relative, expected in beginning['foundation_sources'].items():
            assert sha256(subprocess.check_output(['git', 'show', f'origin/main:{relative}'], cwd=ROOT)).hexdigest() == expected
        # Source files from later commits are retained. Conflicting later edits
        # are not silently replaced by an older snapshot.
        changes = []
        protected_newer = []
        for path in sorted(snapshot.rglob('*')):
            if not path.is_file():
                continue
            rel = path.relative_to(snapshot).as_posix()
            if rel.split('/')[0] not in {'src', 'scripts', 'public', 'docs', 'review', 'project-docs'}:
                continue
            target = ROOT / rel
            changed_after_test = bool(git('diff', '--name-only', TEST_SOURCE, 'HEAD', '--', rel))
            if changed_after_test and target.exists() and digest(target) != digest(path):
                if rel.startswith('project-docs/'):
                    protected_newer.append(rel)
                    continue
                raise ValueError(f'Newer source conflicts with tested snapshot: {rel}')
            if not target.exists() or digest(target) != digest(path):
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, target)
                changes.append(rel)
        # The review archive omits font binaries. Retain the repository's own
        # existing KaTeX assets only when they exactly match the test manifest.
        manifest = gates['generated_sha256']
        for relative, expected in manifest.items():
            target = ROOT / relative
            assert target.is_file(), f'Missing generated resource: {relative}'
            assert digest(target) == expected, f'Generated resource mismatch: {relative}'
        for path in (ROOT/'docs').rglob('*'):
            if path.is_file() and path.relative_to(ROOT).as_posix() not in manifest:
                path.unlink()
        save('recovery.json', {
            'status': 'verified_artifact_recovered_not_yet_promoted', 'checked_at': now(),
            'artifact_id': ARTIFACT, 'artifact_sha256': ARTIFACT_SHA,
            'verified_source_commit': TEST_SOURCE, 'verification_run_id': '34589747612',
            'expected_main': EXPECTED_MAIN, 'recovery_source_commit': os.environ.get('GITHUB_SHA'),
            'generated_resources': len(manifest), 'lesson_count': 40, 'question_count': 172,
            'numerical_checks': gates['numerical_checks'], 'browser_assertions': browser['assertions'],
            'changed_paths': changes, 'preserved_newer_documents': protected_newer,
            'workflow_files_modified': False,
            'next': 'Promote this saved verified candidate to main without force, then verify public delivery.'
        })
        print(f'Restored {len(changes)} paths, verified {len(manifest)} generated hashes; main not changed.')


def public():
    gates = load(REPORTS/'final-gates.json')
    for relative, expected in gates['generated_sha256'].items():
        assert digest(ROOT/relative) == expected, relative
    spec = importlib.util.spec_from_file_location('grade2_control', ROOT/'scripts/grade2-release-control.py')
    control = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(control)
    assert len(control.inspect_lessons()) == 80
    marker_path = 'docs/grade2-release-marker.json'
    expected_marker = (ROOT/marker_path).read_bytes()
    for attempt in range(75):
        try:
            _, data, _ = control.public_get(marker_path, attempts=1)
            if data == expected_marker:
                break
        except Exception:
            pass
        time.sleep(5)
    else:
        raise RuntimeError('The promoted marker is not yet live; main content is saved but publication not confirmed')
    def check(item):
        relative, expected = item
        url, data, tries = control.public_get(relative)
        actual = sha256(data).hexdigest()
        assert actual == expected, f'Delivery mismatch: {relative}'
        result = {'path': relative, 'url': url, 'sha256': actual, 'http_status': 200, 'status': 'passed'}
        if relative.startswith('docs/learn/') and relative.endswith('.html'):
            parser = control.LessonParser()
            parser.feed(data.decode('utf-8'))
            if parser.lesson_ids:
                assert len(parser.lesson_ids) == 1 and parser.math_errors == 0
                result.update(lesson_id=parser.lesson_ids[0], question_ids=parser.question_ids)
        return result
    tasks = [(p,h) for p,h in gates['generated_sha256'].items() if p != 'docs/.nojekyll']
    with ThreadPoolExecutor(max_workers=4) as executor:
        resources = list(executor.map(check,tasks))
    lessons = [r for r in resources if 'lesson_id' in r]
    assert {r['lesson_id'] for r in lessons} == {f'{prefix}{i:02}' for prefix in ['F','G'] for i in range(1,41)}
    qs = [q for r in lessons for q in r['question_ids']]
    assert len(qs) == len(set(qs)) == 302
    report = {
        'status': 'published_and_live_verified', 'checked_at': now(),
        'verified_commit': os.environ.get('GITHUB_SHA'), 'tested_source_commit': gates['source_commit'],
        'workflow_run_id': os.environ.get('GITHUB_RUN_ID'),
        'workflow_url': f"https://github.com/{REPO}/actions/runs/{os.environ.get('GITHUB_RUN_ID','')}",
        'lesson_count': 40, 'question_count': 172, 'foundation_lesson_count': 40, 'foundation_question_count': 130,
        'html_pages': gates['html_pages'], 'resources_verified': len(resources),
        'numerical_checks': gates['numerical_checks'],
        'browser_assertions': load(ROOT/'project-docs/grade2/browser-validation.json')['assertions'],
        'public_marker': json.loads(expected_marker), 'resources': resources,
        'references_unconfirmed': gates['references_unconfirmed'],
        'limits': gates['limitations'],
        'next': '準1級の公式範囲・前提・講座順を整理し、最初の講座から同じ品質基準で制作する。'
    }
    save('publication.json',report)
    p=ROOT/'project-docs/grade2/README.md'
    old=p.read_text(encoding='utf-8')
    marker='<!-- GRADE2_LIVE_RECOVERY_COMPLETE -->'
    if marker not in old:
        note=marker+'\n# 2級コース：main反映・公開後確認完了\n\n'
        note+='基礎40講座・130問を維持し、2級40講座・172問を公開しました。'
        note+=f"全{len(resources)}配信ファイルを検証済み生成物と照合しました。\n\n"
        note+='正本：[公開確認](release/publication.json)・[最終ゲート](release/final-gates.json)・[回収記録](release/recovery.json)。以前の「未確認」はその時点の記録です。\n\n'
        note+='**次の制作対象は準1級コースです。** 未実施の人間による数学監修や学習効果の比較実験は、自動検証と区別します。\n\n---\n\n'
        p.write_text(note+old,encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['resources','public_marker']},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('phase',choices=['recover','public'])
    {'recover':recover,'public':public}[parser.parse_args().phase]()
