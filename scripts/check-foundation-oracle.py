"""Independent SciPy recomputation of release numbers; no network or user data."""
from pathlib import Path
import json, math, datetime, csv
import scipy
from scipy import stats, integrate
root = Path(__file__).resolve().parents[1]
checks = []
def check(label, actual, expected, tol=1e-9):
    assert math.isfinite(actual) and abs(actual-expected) <= tol, (label, actual, expected)
    checks.append(dict(label=label, actual=float(actual), expected=expected, tolerance=tol))
check('F35 df9 t quantile', stats.t.ppf(.975,9), 2.2621571628540993)
check('F38 two-sided t=2.5 df9', 2*stats.t.sf(2.5,9), .033861827487)
check('F39 two-sided t=3 df9', 2*stats.t.sf(3,9), .014956363910414222)
check('F38 exact binomial p', stats.binomtest(120,200,.5).pvalue, .005685155996750306)
check('F33 binomial tail', stats.binom.sf(59,100,.5), .028443966820490392)
check('F31 normalization integral', integrate.quad(lambda x: math.exp(-x*x/2)/math.sqrt(2*math.pi), -math.inf, math.inf)[0], 1)
check('F31 second moment', integrate.quad(lambda x: x*x*math.exp(-x*x/2)/math.sqrt(2*math.pi), -math.inf, math.inf)[0], 1)
for z in [0,.1,1,1.2,1.9,1.96,2,2.5758293035489004,8]:
    check(f'normal SF oracle z={z}', stats.norm.sf(z), .5*math.erfc(z/math.sqrt(2)), 1e-14)
with (root/'public/data/foundation-temperature-change.csv').open() as f:
    values=[float(r['temperature_change_celsius']) for r in csv.DictReader(f)]
r=stats.ttest_1samp(values,8)
check('F39 CSV t', r.statistic, -3); check('F39 CSV p', r.pvalue, .014956363910414222)
for k,n in [(120,200),(0,20),(20,20)]:
    # Match z=1.96 explicitly rather than silently changing the article's rounded critical value.
    level=2*stats.norm.cdf(1.96)-1
    q=stats.binomtest(k,n).proportion_ci(level, method='wilson')
    if k==120: check('F36 Wilson lower',q.low,.5308354385001253);check('F36 Wilson upper',q.high,.6653953603162106)
    if k==0: check('F36 Wilson zero upper',q.high,.16113012549493322)
report={'status':'passed','checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scipy_version':scipy.__version__,'checks':checks,'note':'Independent numerical implementation; not independent human mathematical review.'}
(root/'project-docs/learning-platform-design/12-scipy-oracle.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(f'{len(checks)} independent SciPy checks passed')
