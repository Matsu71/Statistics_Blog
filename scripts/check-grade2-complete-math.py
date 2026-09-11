"""Numerical checks for G01–G40. These do not claim independent human peer review."""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from datetime import datetime, timezone
import json
import math
import os
import re
import statistics
import numpy as np
import scipy
from scipy import integrate, stats

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'project-docs/grade2/math-validation.json'
SOURCES = {}
for path in sorted((ROOT / 'src/content/grade2').glob('*.md')):
    text = path.read_text(encoding='utf-8')
    match = re.search(r'^lesson_id:\s*(G\d{2})\s*$', text, re.M)
    if match:
        if match[1] in SOURCES:
            raise ValueError(f'Duplicate lesson ID {match[1]}')
        SOURCES[match[1]] = {'path': str(path.relative_to(ROOT)), 'text': text,
                           'sha256': sha256(text.encode()).hexdigest()}
expected_ids = {f'G{i:02}' for i in range(1, 41)}
if set(SOURCES) != expected_ids:
    raise ValueError(f'Missing or unexpected lessons: {sorted(expected_ids ^ set(SOURCES))}')
checks = []

def check(lesson, name, computed, expected, tolerance=1e-9, relative=1e-9):
    actual_array = np.asarray(computed, dtype=float)
    expected_array = np.asarray(expected, dtype=float)
    passed = (actual_array.shape == expected_array.shape and np.isfinite(actual_array).all()
              and np.allclose(actual_array, expected_array, rtol=relative, atol=tolerance))
    record = {'lesson_id': lesson, 'name': name, 'actual': actual_array.tolist(),
              'expected': expected_array.tolist(), 'absolute_tolerance': tolerance,
              'relative_tolerance': relative, 'status': 'passed' if passed else 'failed'}
    checks.append(record)
    if not passed:
        raise AssertionError(json.dumps(record, ensure_ascii=False))


def cov(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.mean((a - a.mean()) * (b - b.mean())))


def ci_mean(values, confidence=.95):
    values = np.asarray(values, float)
    se = values.std(ddof=1) / math.sqrt(len(values))
    return values.mean() + np.array([-1, 1]) * stats.t.ppf((1 + confidence) / 2, len(values) - 1) * se


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float)
    coefficients = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ coefficients
    df = len(y) - np.linalg.matrix_rank(x)
    if df <= 0:
        raise ValueError('Residual degrees of freedom must be positive')
    sse = float(residual @ residual)
    mse = sse / df
    vcov = mse * np.linalg.inv(x.T @ x)
    return coefficients, residual, sse, df, mse, vcov


def run():
    x = np.array([2., 4., 6., 8.])
    check('G01', 'sum, mean and sum of squares', [x.sum(), x.mean(), x @ x, x.sum() ** 2], [20, 5, 120, 400])
    check('G01', 'population and sample variance', [x.var(), x.var(ddof=1)], [5, Fraction(20, 3)])
    check('G01', 'sum of deviations from an arbitrary center', (x - 2).sum(), 12)
    x = np.array([0., 0., 1., 3.]); centered = x - x.mean()
    moments = [np.mean(centered ** k) for k in [2, 3, 4]]
    check('G02', 'central moments', moments, [1.5, 1.5, 4.5])
    check('G02', 'moment skew and raw/excess kurtosis', [stats.skew(x, bias=True), stats.kurtosis(x, fisher=False, bias=True), stats.kurtosis(x, fisher=True, bias=True)], [math.sqrt(2 / 3), 2, -1])
    check('G02', 'unbiased variance', np.var(x, ddof=1), 2)
    def gini(values):
        a = np.asarray(values, float)
        return np.abs(a[:, None] - a).sum() / (2 * len(a) * a.sum())
    check('G03', 'pairwise Gini', gini([0, 10, 10, 20]), .375)
    check('G03', 'translation is not scale invariance', gini([10, 20, 20, 30]), .1875)
    check('G03', 'Lorenz trapezoids', np.trapezoid([0, 0, .25, .5, 1], [0, .25, .5, .75, 1]), .3125)
    check('G04', 'geometric growth rate', stats.gmean([1.2, .9]) - 1, math.sqrt(1.08) - 1)
    p0, q0, pt, qt = map(np.array, [[2, 4], [10, 5], [3, 5], [8, 6]])
    check('G04', 'Laspeyres and Paasche price indices', [100 * (pt @ q0) / (p0 @ q0), 100 * (pt @ qt) / (p0 @ qt)], [137.5, 135])
    z = np.arange(1., 5.); d = z - z.mean()
    check('G04', 'full-mean lag-one autocorrelation', d[1:] @ d[:-1] / (d @ d), .25)
    check('G04', 'Pearson correlation of shifted slices is different', stats.pearsonr(z[:-1], z[1:]).statistic, 1)
    check('G05', 'stratified weighted mean', np.average([12, 18], weights=[60, 40]), 14.4)
    check('G05', 'finite population variance using N-1 convention', (1 - 20 / 100) * 25 / 20, 1)
    means = np.array([np.mean(pair) for pair in combinations([2, 4, 8, 10], 2)])
    check('G05', 'enumerated simple random sample means', [means.mean(), means.var()], [6, Fraction(10, 3)])
    check('G06', 'blocked differences', np.array([9, 13]) - [7, 11], [2, 2])
    check('G06', 'allocation count', len(list(combinations(range(4), 2))), 6)
    check('G07', 'total defect probability', .6 * .02 + .4 * .05, .032)
    check('G07', 'posterior factory B', (.4 * .05) / (.6 * .02 + .4 * .05), .625)
    check('G07', 'changed prior factory B', (.1 * .05) / (.9 * .02 + .1 * .05), Fraction(5, 23))
    check('G07', 'independent union', .4 + .5 - .4 * .5, .7)
    prob = np.array([[.4, .1], [.2, .3]])
    ex = prob[1].sum(); ey = prob[:, 1].sum(); exy = prob[1, 1]
    check('G08', 'marginal means and covariance', [ex, ey, exy - ex * ey], [.5, .4, .1])
    check('G08', 'correlation', (exy - ex * ey) / math.sqrt(ex * (1 - ex) * ey * (1 - ey)), 1 / math.sqrt(6))
    check('G08', 'zero covariance with nonlinear dependence', cov([-1, 0, 1], [1, 0, 1]), 0)
    sums = np.array([[0, 1], [1, 2]]); differences = np.array([[0, -1], [1, 0]])
    moment = lambda a: float((prob * a).sum())
    check('G09', 'sum moments', [moment(sums), moment(sums ** 2) - moment(sums) ** 2], [.9, .69])
    check('G09', 'difference moments', [moment(differences), moment(differences ** 2) - moment(differences) ** 2], [.1, .29])
    linear = np.array([[5, 4], [7, 6]])
    check('G09', 'linear combination moments', [moment(linear), moment(linear ** 2) - moment(linear) ** 2], [5.6, .84])
    check('G09', 'correlated standard deviations', [2 * 3 * .5, 4 + 9 + 2 * 2 * 3 * .5], [3, 19])
    check('G10', 'density normalization and moments by quadrature', [integrate.quad(lambda x: 2*x, 0, 1)[0], integrate.quad(lambda x: 2*x*x, 0, 1)[0], integrate.quad(lambda x: 2*x**3, 0, 1)[0]], [1, Fraction(2, 3), .5])
    check('G10', 'density probability', integrate.quad(lambda x: 2*x, 0, .5)[0], .25)
    check('G10', 'uniform probability mean variance', [stats.uniform.cdf(5, loc=0, scale=6)-stats.uniform.cdf(2, loc=0, scale=6), stats.uniform.mean(loc=0, scale=6), stats.uniform.var(loc=0, scale=6)], [.5, 3, 3])
    check('G10', 'two inverse branches', stats.uniform.cdf(.5, loc=-1, scale=2)-stats.uniform.cdf(-.5, loc=-1, scale=2), .5)
    check('G11', 'binomial probability mean variance', [stats.binom.pmf(2, 5, .4), stats.binom.mean(5, .4), stats.binom.var(5, .4)], [.3456, 2, 1.2])
    check('G11', 'hypergeometric probability mean variance', [stats.hypergeom.pmf(2, 10, 4, 3), stats.hypergeom.mean(10, 4, 3), stats.hypergeom.var(10, 4, 3)], [.3, 1.2, .56])
    check('G11', 'binomial counterpart', stats.binom.pmf(2, 3, .4), .288)
    check('G12', 'geometric trials', [stats.geom.pmf(3, .3), stats.geom.mean(.3), stats.geom.var(.3)], [.147, Fraction(10, 3), Fraction(70, 9)])
    check('G12', 'negative-binomial failures correspond to total five', stats.nbinom.pmf(3, 2, .3), .12348)
    check('G12', 'failure moments', [stats.nbinom.mean(2, .3), stats.nbinom.var(2, .3)], [Fraction(14, 3), Fraction(140, 9)])
    check('G12', 'memoryless residual wait', stats.geom.sf(7, .3) / stats.geom.sf(5, .3), .49)
    check('G13', 'one-hour count probability', stats.poisson.cdf(1, 2), 3 * math.exp(-2))
    check('G13', 'continuous waiting probability', stats.expon.sf(.5, scale=.5), math.exp(-1))
    check('G13', 'two-hour count probability', stats.poisson.pmf(2, 4), 8 * math.exp(-4))
    check('G13', 'waiting moments', [stats.expon.mean(scale=.5), stats.expon.var(scale=.5)], [.5, .25])
    sigma = np.array([[4., 3.], [3., 9.]])
    check('G14', 'conditional mean and variance', [20 + sigma[1, 0] / sigma[0, 0] * 2, sigma[1, 1] - sigma[1, 0] ** 2 / sigma[0, 0]], [21.5, 6.75])
    weights = np.array([2., -1.])
    check('G14', 'linear combination variance', weights @ sigma @ weights, 13)
    check('G14', 'standardized tail', stats.norm.sf((13.92 - 10) / 2), stats.norm.sf(1.96))
    check('G15', 'sample mean variance and standard error', [12**2 / 16, 12 / math.sqrt(16)], [9, 3])
    check('G15', 'sample proportion variance and SE', [.3 * .7 / 100, math.sqrt(.3 * .7 / 100)], [.0021, math.sqrt(.0021)])
    check('G15', 'sample variance from observed values', statistics.variance([2,4,6,8]), Fraction(20,3))
    matrix = np.full((4,4), 3.); np.fill_diagonal(matrix, 9.)
    check('G15', 'dependent mean variance', np.ones(4) @ matrix @ np.ones(4) / 16, 4.5)
    check('G16', 'Chebyshev mean bound', 3**2/(100*1**2), .09)
    check('G16', 'binomial exact central tail by symmetry', stats.binom.cdf(50,100,.5), .5 + .5 * math.comb(100,50)/2**100)
    check('G16', 'continuity corrected central tail', stats.norm.cdf(.1), .53983, tolerance=5e-6)
    check('G16', 'continuity corrected right tail', stats.norm.sf(.9), .18406, tolerance=5e-6)
    check('G17', 't15 critical value', stats.t.ppf(.975,15), 2.131449545559323)
    check('G17', 't15 two-sided probability', 2*stats.t.sf(2,15), .06395, tolerance=6e-6)
    check('G17', 't statistic and df', [(54-50)/(8/math.sqrt(16)),16-1],[2,15])
    check('G18', 'chi-square moments', [stats.chi2.mean(9),stats.chi2.var(9)],[9,18])
    check('G18', 'chi-square2 quantiles via exponential', stats.chi2.ppf([.05,.95],2), [-2*math.log(.95),-2*math.log(.05)])
    check('G18', 'F2,2 inverse quantiles', stats.f.ppf([.05,.95],2,2), [1/19,19])
    check('G18', 'F reciprocal with unequal degrees', stats.f.ppf(.025,5,8),1/stats.f.ppf(.975,8,5))
    check('G19', 'MSE decomposition example', 3+2**2,7)
    for mu, answer in [(2,.8),(10,4.64)]:
        values=np.array([mu-1.,mu+1.])
        check('G19',f'shrinkage MSE at mu={mu}', np.mean((.8*values-mu)**2), answer)
    check('G20', 'known-sigma confidence interval', 52+np.array([-1,1])*1.96*8/4,[48.08,55.92])
    check('G20', 'unknown-sigma confidence interval', 52+np.array([-1,1])*stats.t.ppf(.975,15)*2,[47.7371,56.2629],tolerance=2e-6)
    check('G20', 'sample size and half-width',1.96*8/math.sqrt(64),1.96)
    a,b=4/10,9/20
    df=(a+b)**2/(a*a/9+b*b/19)
    se=math.sqrt(a+b)
    check('G21','Welch SE and degrees of freedom',[se,df],[math.sqrt(.85),25.410662824],tolerance=.001)
    pooled=(9*4+19*9)/28
    check('G21','pooled variance',pooled,Fraction(207,28))
    paired=[1,2,2,3,2]
    check('G21','paired mean variance and SE',[statistics.mean(paired),statistics.variance(paired),stats.sem(paired)],[2,.5,math.sqrt(.1)])
    check('G21','paired confidence interval',ci_mean(paired),2+np.array([-1,1])*stats.t.ppf(.975,4)*math.sqrt(.1))
    check('G22','one proportion Wald interval',.4+np.array([-1,1])*1.96*math.sqrt(.24/100),[.30398,.49602],tolerance=5e-6)
    check('G22','difference of proportions Wald interval',.1+np.array([-1,1])*1.96*math.sqrt(.00345),[-.01512,.21512],tolerance=5e-6)
    confidence=2*stats.norm.cdf(1.96)-1
    wilson=stats.binomtest(0,10).proportion_ci(confidence_level=confidence,method='wilson')
    check('G22','Wilson boundary by quadratic',[wilson.low,wilson.high],[0,1.96**2/(10+1.96**2)])
    check('G23','normal variance interval',36/stats.chi2.ppf([.975,.025],9),[1.89,13.33],tolerance=.006)
    check('G23','variance ratio interval',2/stats.f.ppf([.975,.025],2,2),[2/39,78])
    check('G23','positive transformations of intervals',[math.sqrt(4),math.sqrt(25),1/4,1/.5],[2,5,.25,2])
    rxy,rxz,ryz=.8,.5,.6
    check('G24','partial correlation',(rxy-rxz*ryz)/math.sqrt((1-rxz**2)*(1-ryz**2)),.5/math.sqrt(.48))
    fisher=np.tanh(np.arctanh(.5)+np.array([-1,1])*1.96/math.sqrt(17))
    check('G24','rounded Fisher confidence interval',fisher,[.074,.772],tolerance=.001)
    check('G24','null-correlation t statistic',.5*math.sqrt(18/(1-.5**2)),math.sqrt(6))
    check('G25','upper lower and two-sided probabilities',[stats.norm.sf(2),stats.norm.cdf(2),2*stats.norm.sf(2)],[.02275,.97725,.04550],tolerance=5e-6)
    check('G25','data-selected one-sided rejection rate',2*stats.norm.sf(stats.norm.ppf(.95)),.1)
    power=stats.norm.sf(stats.norm.ppf(.95)-5*math.sqrt(25)/10)
    check('G26','power for specified positive effect',power,.804,tolerance=.0006)
    continuous_n=((stats.norm.ppf(.95)+stats.norm.ppf(.8))*10/5)**2
    check('G26','ceiling of one-sided known-variance sample size',math.ceil(continuous_n),25)
    check('G26','reducing alpha lowers power at fixed positive effect',float(stats.norm.sf(stats.norm.ppf(.99)-2.5)<power),1)
    check('G27','same statistic different reference distributions',[2*stats.norm.sf(2),2*stats.t.sf(2,24)],[.04550,.05694],tolerance=5e-6)
    check('G27','unknown-variance interval',104+np.array([-1,1])*stats.t.ppf(.975,24)*2,[99.8722,108.1278],tolerance=5e-5)
    check('G28','Welch statistic',3/se,3.25396,tolerance=5e-6)
    check('G28','pooled standard error and statistic',[math.sqrt(pooled*(1/10+1/20)),3/math.sqrt(pooled*(1/10+1/20))],[1.05306,2.84885],tolerance=6e-6)
    paired_test=stats.ttest_1samp(paired,0)
    check('G28','paired t',paired_test.statistic,math.sqrt(40))
    check('G28','paired two-sided probability',paired_test.pvalue,.0032,tolerance=5e-6)
    check('G29','one-proportion null standard error and statistic',[math.sqrt(.25/100),(.6-.5)/math.sqrt(.25/100)],[.05,2])
    pooled_p=(40+60)/(100+200)
    z=(.4-.3)/math.sqrt(pooled_p*(1-pooled_p)*(1/100+1/200))
    check('G29','two-proportion null z and p',[z,2*stats.norm.sf(abs(z))],[math.sqrt(3),.08326],tolerance=5e-6)
    check('G29','small-binomial exact lower tail',stats.binomtest(0,10,.1,alternative='less').pvalue,.9**10)
    check('G30','variance test statistic and rejection',[9*25/9,float(25>stats.chi2.ppf(.975,9))],[25,1])
    check('G30','equal-tail F test',2*min(stats.f.cdf(2,2,2),stats.f.sf(2,2,2)),Fraction(2,3))
    fit=stats.chisquare([18,22,28,32],[25,25,25,25])
    check('G31','Pearson goodness-of-fit statistic',fit.statistic,4.64)
    check('G31','goodness-of-fit tail',fit.pvalue,stats.chi2.sf(4.64,3))
    check('G31','zero observed positive expected contribution',(0-10)**2/10,10)
    table=np.array([[30,20],[20,30]])
    pearson=stats.chi2_contingency(table,correction=False)
    corrected=stats.chi2_contingency(table,correction=True)
    check('G32','independence expected table',pearson.expected_freq,np.full((2,2),25))
    check('G32','uncorrected independence test',[pearson.statistic,pearson.dof,pearson.pvalue],[4,1,2*stats.norm.sf(2)])
    check('G32','Yates versus uncorrected result',[corrected.statistic,corrected.pvalue],[3.24,2*stats.norm.sf(1.8)])
    xr=np.arange(1.,7.);yr=np.array([2.,4.,5.,4.,6.,9.])
    design=np.column_stack([np.ones(6),xr])
    coef,resid,sse,rdof,mse,vcov=ols(design,yr)
    simple=stats.linregress(xr,yr)
    check('G33','OLS coefficients versus exact algebra',coef,[1,Fraction(8,7)])
    check('G33','OLS residuals',resid,np.array([-1,5,4,-11,-5,8])/7)
    check('G33','residual variance',[sse,rdof,mse],[Fraction(36,7),4,Fraction(9,7)])
    check('G33','slope and intercept variance',np.diag(vcov),[Fraction(39,35),Fraction(18,245)])
    check('G33','library slope standard error',simple.stderr,math.sqrt(18/245))
    t_slope=coef[1]/math.sqrt(vcov[1,1])
    check('G34','slope t and overall F',[t_slope,t_slope*t_slope],[4*math.sqrt(10)/3,Fraction(160,9)])
    check('G34','linear regression p value',simple.pvalue,2*stats.t.sf(abs(t_slope),4))
    mean_vector=np.array([1.,3.5])
    mean_var=float(mean_vector@vcov@mean_vector)
    check('G34','mean-response and prediction estimated variances',[mean_var,mean_var+mse],[Fraction(3,14),1.5])
    check('G34','rounded response intervals',5+np.array([-1,1])*stats.t.ppf(.975,4)*math.sqrt(mean_var),[3.71,6.29],tolerance=.01)
    x=np.tile(np.arange(1.,5.),2);dummy=np.repeat([0.,1.],4)
    y=np.array([13.,13.,15.,19.,16.,16.,18.,22.])
    design2=np.column_stack([np.ones(8),x,dummy])
    c2,e2,sse2,df2,mse2,vcov2=ols(design2,y)
    check('G35','multiple regression coefficients',c2,[10,2,3])
    check('G35','multiple-regression residuals',e2,[1,-1,-1,1,1,-1,-1,1])
    check('G35','residual square sum and df',[sse2,df2,mse2],[8,5,1.6])
    check('G35','interaction example is a separate model',3+1.5*3,7.5)
    sst=float(((y-y.mean())**2).sum())
    r2=1-sse2/sst;adjusted=1-(sse2/df2)/(sst/(len(y)-1))
    check('G36','R-squared and adjusted R-squared',[sst,r2,adjusted],[66,Fraction(29,33),Fraction(137,165)])
    check('G36','VIF from auxiliary R-squared',1/(1-.9),10)
    groups=[[8.,9.,10.],[10.,11.,12.],[12.,13.,14.]]
    grand=np.mean([v for g in groups for v in g])
    ssb=sum(len(g)*(np.mean(g)-grand)**2 for g in groups)
    ssw=sum(sum((v-np.mean(g))**2 for v in g) for g in groups)
    anova=stats.f_oneway(*groups)
    check('G37','one-way ANOVA square sums',[ssb,ssw,ssb+ssw],[24,6,30])
    check('G37','one-way ANOVA F and exact tail',[anova.statistic,anova.pvalue],[12,.008])
    check('G38','coefficient variances reconstructed from design',np.diag(vcov2),[1.4,.16,.8])
    overall=((sst-sse2)/2)/(sse2/df2)
    check('G38','overall F with two predictors',overall,18.125)
    check('G38','overall F analytic tail',stats.f.sf(overall,2,5),(4/33)**2.5)
    case=json.loads((ROOT/'project-docs/grade2/iris-analysis.json').read_text(encoding='utf-8'))
    if case.get('status')!='passed':raise ValueError('Real-data case was not verified')
    csv_hash=sha256((ROOT/'public/data/grade2-iris.csv').read_bytes()).hexdigest()
    if case.get('csv_sha256')!=csv_hash:raise ValueError('Case data changed after analysis')
    check('G39','preserved case row count',case['row_count'],150)
    check('G39','source standard deviations and standard errors',
          [s['se_mean']*math.sqrt(s['n']) for s in case['summaries'].values()],
          [s['sd_ddof1'] for s in case['summaries'].values()])
    cw=case['welch']
    check('G39','reported Welch t',cw['difference']/cw['se'],cw['t'])
    check('G39','reported Welch probability',2*stats.t.sf(abs(cw['t']),cw['df']),cw['p_two_sided'])
    qdata=np.array([1.,3.,5.])
    check('G40','Q1 sum notation',[qdata.mean(),qdata@qdata,qdata.sum()**2,qdata.var(ddof=1)],[3,35,81,4])
    check('G40','Q2 Gini',gini([0,0,10,10]),.5)
    check('G40','Q3 geometric growth',stats.gmean([1.5,.8])-1,math.sqrt(1.2)-1)
    check('G40','Q4 finite population correction',(1-10/50)*20/10,1.6)
    check('G40','Q5 conditional probability',[.2*.8+.8*.1,.2*.8/(.2*.8+.8*.1)],[.24,Fraction(2,3)])
    check('G40','Q6 covariance and difference variance',[.4-.5*.6,.25+.24-2*(.4-.5*.6)],[.1,.29])
    check('G40','Q7 nonreplacement probability',stats.hypergeom.pmf(2,8,3,2),Fraction(3,28))
    check('G40','Q8 geometric probability and mean',[stats.geom.pmf(4,.25),stats.geom.mean(.25)],[Fraction(27,256),4])
    check('G40','Q9 sample mean tail',stats.norm.sf(21.96,loc=20,scale=4/math.sqrt(16)),stats.norm.sf(1.96))
    check('G40','Q10 known-sigma interval',10+np.array([-1,1])*1.96*.5,[9.02,10.98])
    check('G40','Q11 MSE comparison',[2,1+.5**2],[2,1.25])
    check('G40','Q12 paired t',stats.ttest_1samp([1,2,3,4],0).statistic,math.sqrt(15))
    goodness=stats.chisquare([12,18,30],[20,20,20])
    check('G40','Q13 goodness-of-fit',[goodness.statistic,goodness.pvalue],[8.4,math.exp(-4.2)])
    c,e,sse,df,mse,vc=ols(np.column_stack([np.ones(4),np.arange(4.)]),[1,2,2,5])
    check('G40','Q14 OLS coefficients and residual variance',[c[0],c[1],sse,mse],[.7,1.2,1.8,.9])
    check('G40','Q15 ANOVA table',[(24/2)/(6/6),stats.f.sf(12,2,6)],[12,.008])
    check('G40','Q16 actual case byte provenance',float(case['csv_sha256']==csv_hash),1)

failure=None
try:
    run()
except Exception as exc:
    failure=f'{type(exc).__name__}: {exc}'
covered=sorted({c['lesson_id'] for c in checks if c['status']=='passed'})
if failure is None and set(covered)!=expected_ids:
    failure=f'Numerical fixtures do not cover all lessons: {sorted(expected_ids-set(covered))}'
report={'status':'failed' if failure else 'passed','checked_at':datetime.now(timezone.utc).isoformat(),
        'source_commit':os.environ.get('GITHUB_SHA'), 'workflow_run_id':os.environ.get('GITHUB_RUN_ID'),
        'lesson_count':len(SOURCES),'covered_lessons':covered,'numerical_checks':len(checks),'check_count':len(checks),
        'checks':checks,'failure':failure,
        'sources':{k:{j:v for j,v in s.items() if j!='text'} for k,s in sorted(SOURCES.items())},
        'environment':{'numpy':np.__version__,'scipy':scipy.__version__},
        'limits':['Examples and stated calculations are independently recomputed; this is not proof of every textual assertion.',
                  'Editorial assumptions, explanations, and references require the separately documented content review.',
                  'This is not independent human mathematical peer review or a learning-outcome experiment.']}
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['checks','sources']},ensure_ascii=False,indent=2))
if failure:raise SystemExit(1)
