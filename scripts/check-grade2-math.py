"""Recalculate selected displayed examples; do not claim automated proof verification."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json, math, os, re
import numpy as np
from scipy import stats

ROOT = Path('.')
SOURCES = {}
for p in (ROOT / 'src/content/grade2').glob('*.md'):
    text = p.read_text(encoding='utf-8')
    match = re.search(r'^lesson_id: (G\d{2})$', text, re.M)
    if match:
        SOURCES[match.group(1)] = {'text': text, 'path': str(p), 'sha256': sha256(p.read_bytes()).hexdigest()}
checks = []

def check(lesson, name, computed, expected, tolerance=1e-9, anchors=()):
    if lesson not in SOURCES:
        return
    for anchor in anchors:
        assert anchor in SOURCES[lesson]['text'], f'{lesson}: missing displayed evidence {anchor!r}'
    actual = np.asarray(computed, dtype=float)
    target = np.asarray(expected, dtype=float)
    assert actual.shape == target.shape and np.all(np.isfinite(actual)), (lesson, name, actual)
    assert np.allclose(actual, target, rtol=0, atol=tolerance), (lesson, name, actual, target)
    checks.append({'lesson': lesson, 'name': name, 'calculated': actual.tolist(), 'expected': target.tolist(),
                   'absolute_tolerance': tolerance, 'displayed_anchors': list(anchors), 'status': 'passed'})

x = np.array([2,4,6,8], dtype=float)
check('G01', 'mean, sum, squared sum and n-1 variance', [x.mean(), x.sum(), (x*x).sum(), x.var(ddof=1)], [5,20,120,20/3], anchors=['120','400','20/3'])
check('G01', 'constant appears once per observation', (x-2).sum(), 12, anchors=['20−4×2=12'])
y = np.array([0,0,1,3], dtype=float)
check('G02', 'empirical moments and Fisher/Pearson conventions', [stats.skew(y,bias=True),stats.kurtosis(y,bias=True,fisher=False),stats.kurtosis(y,bias=True,fisher=True),y.var(ddof=1)], [math.sqrt(2/3),2,-1,2], anchors=['0.8165','尖度は2'])
check('G02', 'negative linear transform', [stats.skew(10-2*y,bias=True),stats.kurtosis(10-2*y,bias=True,fisher=False)], [-math.sqrt(2/3),2])
v = np.array([0,10,10,20],dtype=float)
gini = np.abs(v[:,None]-v[None,:]).sum()/(2*len(v)*v.sum())
check('G03', 'pairwise Gini and trapezoidal Lorenz area', [gini, np.trapezoid(np.r_[0,np.cumsum(np.sort(v))/v.sum()], np.linspace(0,1,5))], [.375,.3125], anchors=['G=0.375','A=0.3125'])
check('G03', 'finite-n maximum', np.abs(np.array([0,0,0,40])[:,None]-np.array([0,0,0,40])[None,:]).sum()/320, .75, anchors=['G=0.75'])
check('G04', 'constant compounded growth rate', math.sqrt(1.08)-1, .0392304845413265, anchors=['3.92%'])
p0=np.array([2,4]); q0=np.array([10,5]); pt=np.array([3,5]); qt=np.array([8,6])
check('G04', 'Laspeyres and Paasche use different fixed weights', [100*(pt@q0)/(p0@q0),100*(pt@qt)/(p0@qt)], [137.5,135], anchors=['137.5','135'])
a=np.arange(1.,5); centered=a-a.mean()
check('G04', 'lag-one definition uses full-series center and sum of squares', (centered[1:]@centered[:-1])/(centered@centered), .25, anchors=['0.25'])
check('G05', 'finite population correction with N-1 population variance', [(1-20/100)*25/20, .6*12+.4*18], [1,14.4], anchors=['14.4','標準誤差は1'])
pop=np.array([2,4,8,10],float)
means=np.array([np.mean(c) for c in combinations(pop,2)])
check('G05', 'enumerated SRS variance agrees with finite-population formula', means.var(), (1-2/4)*pop.var(ddof=1)/2)
check('G06', 'complete enumeration of 2/4 treatment assignments', len(list(combinations(range(4),2))), 6, anchors=['6$ 通り'])
check('G06', 'within-block differences', np.array([9,13])-np.array([7,11]), [2,2])
check('G07', 'total probability and Bayes posterior', [.6*.02+.4*.05,.4*.05/(.6*.02+.4*.05),.1*.05/(.9*.02+.1*.05)], [.032,.625,5/23], anchors=['62.5%','21.74%'])
check('G07', 'independent union and complement', [.4+.5-.4*.5,(1-.4)*(1-.5)], [.7,.3])
joint=np.array([[.4,.1],[.2,.3]])
check('G08', 'joint marginals and conditional probabilities', [joint[:,1].sum(),joint[1,:].sum(),joint[1,1]/joint[1,:].sum(),joint[1,1]/joint[:,1].sum()], [.4,.5,.6,.75], anchors=['0.6','0.75'])
check('G08', 'covariance, correlation and sum distribution', [.3-.5*.4,.1/math.sqrt(.25*.24),joint[0,0],joint[0,1]+joint[1,0],joint[1,1]], [.1,.408248290463863,.4,.3,.3], anchors=['0.4082'])

# Later batches append their separately derived numerical fixtures before the report below.
covered = sorted({c['lesson'] for c in checks})
report = {
    'status': 'passed', 'checked_at': datetime.now(timezone.utc).isoformat(),
    'source_commit': os.environ.get('GITHUB_SHA'), 'implementation': 'Python, NumPy and SciPy, separate from displayed lesson arithmetic',
    'numerical_checks': len(checks), 'lessons_checked': covered,
    'source_fingerprints': {k: {'path':v['path'],'sha256':v['sha256']} for k,v in SOURCES.items()},
    'checks': checks,
    'limitations': ['Selected worked examples and counterexamples were recalculated; not every statement is machine-verifiable.',
                   'Analytic proofs, wording and applicability conditions require separate editorial review.',
                   'This is not independent human mathematical peer review.']
}
if json.loads((ROOT/'src/data/grade2-release.json').read_text())['stage'] == 'release_candidate':
    assert set(covered) == set(SOURCES) == {f'G{i:02d}' for i in range(1,41)}, 'Every release lesson needs numerical evidence'
(ROOT/'project-docs/grade2').mkdir(parents=True,exist_ok=True)
(ROOT/'project-docs/grade2/math-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
