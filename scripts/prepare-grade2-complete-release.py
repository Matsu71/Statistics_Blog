"""Prepare the complete grade2 candidate without changing any foundation manuscript."""
from pathlib import Path
import hashlib
import json
import re
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
changed = []


def patch(path, replacements):
    target = ROOT / path
    text = target.read_text(encoding='utf-8')
    updated = text
    for old, new in replacements:
        updated = updated.replace(old, new)
    if updated != text:
        target.write_text(updated, encoding='utf-8')
        changed.append({'path': path, 'before': hashlib.sha256(text.encode()).hexdigest(),
                        'after': hashlib.sha256(updated.encode()).hexdigest()})


for file in (ROOT / 'src/content/grade2').glob('*.md'):
    patch(str(file.relative_to(ROOT)), [
        ('https://www.statlect.com/fundamentals-of-probability/joint-probability-mass-function',
         'https://www.statlect.com/glossary/joint-probability-mass-function'),
        ('[NIST: One-sample t-test](https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm)',
         '[NIST：t検定の関連資料](https://www.itl.nist.gov/div898/handbook/eda/section3/eda353.htm)'),
        ('},\\\n\\frac', '},\\quad\\frac'),
    ])
patch('scripts/check-grade2-complete-math.py', [
    ('[math.sqrt(.85),25.410662824],tolerance=.001',
     '[math.sqrt(.85),Fraction(49419,1945)],tolerance=1e-9')
])
comparison = ROOT / 'project-docs/grade2/04-comparison-and-remediation.md'
if comparison.exists():
    patch(str(comparison.relative_to(ROOT)), [('転載は禁止転載', '無断転載')])

records = []
for file in sorted((ROOT / 'src/content/grade2').glob('*.md')):
    text = file.read_text(encoding='utf-8')
    match = re.search(r'^lesson_id:\s*(G\d{2})\s*$', text, re.M)
    if not match:
        raise ValueError(f'Missing ID: {file}')
    if not re.search(r'^status:\s*published\s*$', text, re.M):
        raise ValueError(f'Unpublished lesson after case generation: {match[1]}')
    questions = re.findall(r'data-question="(G\d{2}-Q\d+)"', text)
    expected_count = 16 if match[1] == 'G40' else 4
    if len(questions) != expected_count:
        raise ValueError(f'{match[1]} has {len(questions)} questions, expected {expected_count}')
    records.append({'id': match[1], 'path': str(file.relative_to(ROOT)), 'questions': len(questions)})
if {r['id'] for r in records} != {f'G{i:02d}' for i in range(1, 41)} or len(records) != 40:
    raise ValueError('The complete release requires exactly G01–G40')
if sum(r['questions'] for r in records) != 172:
    raise ValueError('The complete release requires 172 original questions')

state_path = ROOT / 'src/data/grade2-release.json'
state = json.loads(state_path.read_text(encoding='utf-8'))
state.update(stage='release_candidate', version='grade2-1.0.0', target_lessons=40,
             authored_through='G40', questions=172, scope='grade2',
             next='Run all content, numerical, reference, foundation regression, browser and public deployment checks.',
             limitations=['Not independent human mathematical peer review.',
                          'Not a controlled comparison of learning outcomes.',
                          'Pre-grade1 and grade1 complete course texts are not part of this release.'])
state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Keep the ordinary branch workflow aligned with the new, all-lesson verifier.
workflow = ROOT / '.github/workflows/verify-grade2.yml'
if workflow.exists():
    text = workflow.read_text(encoding='utf-8')
    text = re.sub(r'python(?:3)? scripts/check-grade2-math\.py',
                  'python scripts/check-grade2-complete-math.py', text)
    if 'enrich-grade2-iris-case.py' not in text:
        pattern = re.compile(r'^(\s*)(?:python(?:3)? scripts/import-grade2-iris\.py)\s*$', re.M)
        text = pattern.sub(lambda m: m[1] + 'python scripts/import-grade2-iris.py\n' +
                          m[1] + 'python scripts/enrich-grade2-iris-case.py', text)
    workflow.write_text(text, encoding='utf-8')

report = {'status': 'candidate_prepared_not_yet_verified',
          'prepared_at': datetime.now(timezone.utc).isoformat(),
          'lesson_count': 40, 'question_count': 172, 'corrections': changed,
          'next': 'Execute the complete quality gates. Do not mark published before live verification.',
          'foundation_manuscripts_modified_by_this_script': False}
out = ROOT / 'project-docs/grade2/release-preparation.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
