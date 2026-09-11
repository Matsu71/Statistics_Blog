"""Check numerical examples in P07-P08 drafts; not a release or theorem proof."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json, math, os, re
import numpy as np
from scipy import integrate, stats

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'project-docs/pregrade1/drafts'
SOURCES={}
for p in FOLDER.glob('*.md'):
    text=p.read_text(encoding='utf-8')
    match=re.search(r'^lesson_id: (P\d{2})$',text,re.M)
    if match:
        assert re.search(r'^status: draft$',text,re.M), 'Draft location must not claim publication'
        assert len(re.findall('data-question=',text))==4
        SOURCES[match[1]]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest(),'text':text}
checks=[]
def check(lesson,label,actual,expected,anchors=(),atol=1e-10):
    for s in anchors: assert s in SOURCES[lesson]['text'],(lesson,s)
    a=np.asarray(actual,dtype=float);e=np.asarray(expected,dtype=float)
    assert a.shape==e.shape and np.all(np.isfinite(a))
    assert np.allclose(a,e,atol=atol,rtol=0),(lesson,label,a,e)
    checks.append({'lesson':lesson,'name':label,'computed':a.tolist(),'expected':e.tolist(),'atol':atol,'status':'passed'})
assert set(SOURCES)=={'P07','P08'}
check('P07','log estimate and ordinary versus transformed standard errors',
      [math.log(.4),math.sqrt(.4*.6/400),math.sqrt(.6/(400*.4))],
      [-.916290731874155,.02449489742783178,.06123724356957945],anchors=['0.061237','0.024495'])
h=1e-5
check('P07','local derivative of log versus analytic reciprocal',
      (math.log(.4+h)-math.log(.4-h))/(2*h),2.5,atol=1e-8)
check('P07','variance of a standard normal divided by two',
      integrate.quad(lambda x:(x/2)**2*stats.norm.pdf(x),-10,10)[0],.25,anchors=['分散1/4'])
for x in [.2,1.,4.]:
    check('P07',f'squared normal CDF matches chi square at {x}',
          stats.norm.cdf(math.sqrt(x))-stats.norm.cdf(-math.sqrt(x)),stats.chi2.cdf(x,1))
check('P07','maximum exact tail versus its limiting approximation',
      [stats.beta.cdf(.98,100,1),math.exp(-2)],
      [.13261955589475294,.1353352832366127],anchors=['0.132620','0.135335'])
check('P07','maximum mean and distance from the endpoint',
      [integrate.quad(lambda m:100*m**100,0,1)[0],stats.beta.mean(100,1)],
      [100/101,100/101],anchors=['n/(n+1)'])
check('P07','reciprocal at finite n does not approximate a finite inverse at zero',
      [1/(1/10),1/(1/1000)],[10,1000])

n=6;p=np.array([.2,.3,.5]);states=np.array([(i,j,n-i-j) for i in range(n+1) for j in range(n-i+1)])
probs=stats.multinomial.pmf(states,n,p)
manual=np.array([math.factorial(n)/math.prod(math.factorial(int(x)) for x in k)*math.prod(float(a)**int(b) for a,b in zip(p,k)) for k in states])
check('P08','all finite-support probabilities match factorial counting',probs,manual)
check('P08','probability normalization and target count',
      [probs.sum(),stats.multinomial.pmf([1,2,3],n,p)],[1,.135],anchors=['0.135','60通り'])
mean=probs@states
check('P08','mean vector by complete enumeration',mean,[1.2,1.8,3.])
centered=states-mean
cov=np.einsum('n,ni,nj->ij',probs,centered,centered)
expected=np.array([[.96,-.36,-.6],[-.36,1.26,-.9],[-.6,-.9,1.5]])
check('P08','covariance from complete joint distribution',cov,expected,anchors=['−0.36','1.26'])
check('P08','covariance compared with library implementation',stats.multinomial.cov(n,p),expected)
check('P08','fixed total and singular covariance',[np.ones(3)@cov@np.ones(3),np.linalg.det(cov)],[0,0])
combined=states[:,0]+states[:,1]
combined_p=np.array([probs[combined==k].sum() for k in range(n+1)])
check('P08','combining disjoint categories yields a binomial marginal',combined_p,stats.binom.pmf(np.arange(n+1),n,.5))
check('P08','variance after combining A and B',probs@(combined-3.)**2,1.5)
mask=states[:,0]==1
conditional=probs[mask]/probs[mask].sum()
check('P08','conditional probabilities after fixing the A count',conditional,stats.binom.pmf(states[mask,1],5,.375))
check('P08','conditional B expectation',(conditional@states[mask,1]),1.875,anchors=['1.875','0.375'])
conditional_poisson=np.prod(stats.poisson.pmf(states,np.array([2.,3.,5.])),axis=1)/stats.poisson.pmf(n,10)
check('P08','independent Poissons conditioned on total match every multinomial cell',conditional_poisson,probs)
t=np.array([.1,-.2,.3])
check('P08','joint MGF by enumeration versus independent trial formula',probs@np.exp(states@t),(p@np.exp(t))**n)
report={'status':'draft_numerical_checks_passed','checked_at':datetime.now(timezone.utc).isoformat(),
        'source_commit':os.environ.get('GITHUB_SHA'),'draft_lessons':2,'draft_questions':8,'numerical_checks':len(checks),
        'sources':{k:{a:b for a,b in v.items() if a!='text'} for k,v in SOURCES.items()},'checks':checks,
        'limits':['Drafts are not integrated into the published collection and have not passed its browser/release gates.',
                  'Finite numerical agreement does not prove an asymptotic theorem or allow exchange of moments and limits.',
                  'No independent human mathematical peer review or learner outcome study is claimed.'],
        'next':'Integrate P07-P08 with updated coverage counts and full-course numerical/browser checks; publish only their verified build.'}
out=FOLDER/'numerical-checks.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['checks','sources']},ensure_ascii=False,indent=2))
