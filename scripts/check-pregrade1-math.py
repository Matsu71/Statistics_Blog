"""Recalculate the initial P01-P06 examples; analytic proofs remain editorial work."""
from datetime import datetime, timezone
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json, math, os, re
import numpy as np
import scipy
from scipy import integrate, stats
from numpy.polynomial import polynomial as poly

ROOT=Path(__file__).resolve().parents[1]
SOURCES={}
for p in (ROOT/'src/content/pregrade1').glob('*.md'):
    text=p.read_text(encoding='utf-8')
    key=re.search(r'^lesson_id: (P\d{2})$',text,re.M)[1]
    SOURCES[key]={'path':p.relative_to(ROOT).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest(),'text':text}
checks=[]
def check(lesson,name,actual,expected,anchors=(),tol=1e-10):
    assert lesson in SOURCES
    for a in anchors: assert a in SOURCES[lesson]['text'],(lesson,'missing displayed anchor',a)
    x=np.asarray(actual,dtype=float);y=np.asarray(expected,dtype=float)
    assert x.shape==y.shape and np.all(np.isfinite(x)),(lesson,name,x)
    assert np.allclose(x,y,atol=tol,rtol=0),(lesson,name,x,y)
    checks.append({'lesson':lesson,'name':name,'computed':x.tolist(),'expected':y.tolist(),
                   'absolute_tolerance':tol,'displayed_anchors':list(anchors),'status':'passed'})

joint=[[F(15,100),F(45,100),F(15,100)],[F(5,100),F(5,100),F(15,100)]]
y=[F(0),F(2),F(4)];weights=[sum(row) for row in joint]
conditional=[[p/w for p in row] for row,w in zip(joint,weights)]
means=[sum(v*p for v,p in zip(y,row)) for row in conditional]
second=[sum(v*v*p for v,p in zip(y,row)) for row in conditional]
EY=sum(w*m for w,m in zip(weights,means));EY2=sum(w*m for w,m in zip(weights,second))
check('P01','joint normalizes and conditional rows normalize',[sum(weights),*[sum(r) for r in conditional]],[1,1,1])
check('P01','conditional means from exact rational table',means,[2,2.8],anchors=['2.8','0.7/0.25'])
check('P01','tower expectation vs direct marginal expectation',[EY,sum(y[j]*sum(row[j] for row in joint) for j in range(3))],[2.2,2.2],anchors=['2.2','2.4'])
check('P01','conditional second moment is not squared mean',[second[1],means[1]**2],[10.4,7.84],anchors=['10.4','7.84'])
xz=[(x,z,x*z) for x in (1,2) for z in (-1,1)]
check('P01','constant conditional mean but unequal conditional distributions',
      [np.mean([y for x,z,y in xz if x==1]),np.mean([y for x,z,y in xz if x==2]),
       np.mean([abs(y)==1 for x,z,y in xz if x==1]),np.mean([abs(y)==1 for x,z,y in xz])],[0,0,1,.5])

variances=[q-m*m for q,m in zip(second,means)]
within=sum(w*v for w,v in zip(weights,variances));between=sum(w*(m-EY)**2 for w,m in zip(weights,means))
check('P02','within-group variances',variances,[1.6,2.56],anchors=['1.60','2.56'])
check('P02','total variance via conditioning vs original joint table',[within,between,EY2-EY*EY],[1.84,.12,1.96],anchors=['1.84','0.12','1.96'])
check('P02','constant groups can have nonzero total variance',np.var([8,12]),4,anchors=['分散4'])
mean_risk=sum(p*(v-m)**2 for row,m in zip(joint,means) for p,v in zip(row,y))
constant_risk=sum(p*(v-EY)**2 for row in joint for p,v in zip(row,y))
check('P02','prediction risks by enumerating every cell',[mean_risk,constant_risk],[1.84,1.96])
count=np.arange(0,60);pr=stats.poisson.pmf(count,3)
random_mean=np.sum(pr*5*count);random_second=np.sum(pr*(4*count+25*count**2))
check('P02','random sum from Poisson mixture moments',[random_mean,random_second-random_mean**2],[15,87],anchors=['87','75'])

values=np.array([-2.,1.]);probs=np.array([.4,.6]);mgf=lambda t:np.sum(probs*np.exp(t*values))
check('P03','finite-support MGF at zero and log(2)',[mgf(0),mgf(math.log(2))],[1,1.3],anchors=['1.3'])
mu=probs@values;moment2=probs@(values**2)
check('P03','first two moments and variance by direct expectation',[mu,moment2,moment2-mu**2],[-.2,2.2,2.16],anchors=['2.16'])
z=3*values+4
check('P03','affine transformation calculated on actual support',[probs@z,probs@(z*z)-(probs@z)**2],[3.4,19.44],anchors=['3.4','19.44'])
check('P03','dependent double vs independent sum MGF',[mgf(2*math.log(2)),mgf(math.log(2))**2],[2.425,1.69],anchors=['2.425','1.69'])
exp_mgf=integrate.quad(lambda x:2*math.exp(-x),0,np.inf)[0]
exp_first=integrate.quad(lambda x:x*2*math.exp(-2*x),0,np.inf)[0]
exp_second=integrate.quad(lambda x:x*x*2*math.exp(-2*x),0,np.inf)[0]
check('P03','exponential MGF integral and moments',[exp_mgf,exp_first,exp_second-exp_first**2],[2,.5,.25],anchors=['t<2','M_X(1)=2'])
for k in [1,2,3]:
    result=integrate.quad(lambda z:math.exp(k*z-z*z/2)/math.sqrt(2*math.pi),-15,15)[0]
    check('P03',f'lognormal finite moment k={k}',result,math.exp(k*k/2),tol=1e-8)

coeff=np.array([.2,.5,.3]);d1=poly.polyder(coeff);d2=poly.polyder(d1)
check('P04','PGF boundary values and coefficient recovery',[poly.polyval(0,coeff),poly.polyval(1,coeff),poly.polyval(0,d2)/2],[.2,1,.3],anchors=['0.2','0.6'])
a=poly.polyval(1,d1);b=poly.polyval(1,d2)
check('P04','factorial moment and variance',[a,b,b+a-a*a],[1.1,.6,.49],anchors=['1.7','0.49'])
convolution=poly.polymul(coeff,coeff)
enumerated=sum(coeff[i]*coeff[j] for i in range(3) for j in range(3) if i+j==2)
check('P04','independent sum coefficient vs direct enumeration',[convolution[2],enumerated,coeff[1]],[.37,.37,.5],anchors=['0.37','0.5'])
n=np.arange(0,70);pcount=stats.poisson.pmf(n,4)
check('P04','thinning empty probability from conditional binomial formula',np.sum(pcount*stats.binom.pmf(0,n,.25)),math.exp(-1),anchors=['0.367879'])
check('P04','thinning expected count via Poisson mixture',np.sum(pcount*n*.25),1)
for s in [0,.3,.7,1]:
    check('P04',f'PGF composition thinning at s={s}',np.sum(pcount*(.75+.25*s)**n),math.exp(s-1))

inverse=np.array([[.5,.5],[.5,-.5]])
check('P05','inverse Jacobian determinant',abs(np.linalg.det(inverse)),.5,anchors=['1/2'])
lo=lambda s:max(-s,s-2);hi=lambda s:min(s,2-s)
check('P05','support cross-sections',[lo(.5),hi(.5),lo(1),hi(1),lo(1.5),hi(1.5)],[-.5,.5,-1,1,-.5,.5],anchors=['−0.5<D<0.5'])
area=integrate.quad(lambda s:hi(s)-lo(s),0,2,points=[1])[0]
check('P05','transformed density normalizes',.5*area,1)
prob=integrate.quad(lambda s:.5*(hi(s)-lo(s)),0,.5)[0]
check('P05','sum CDF at one half by transformed-region integral',prob,.125,anchors=['0.125'])
first=integrate.quad(lambda s:s*.5*(hi(s)-lo(s)),0,2,points=[1])[0]
second_sum=integrate.quad(lambda s:s*s*.5*(hi(s)-lo(s)),0,2,points=[1])[0]
check('P05','sum mean and variance from density',[first,second_sum-first**2],[1,1/6],anchors=['1/6'])
check('P05','impossible pair reconstructed to negative Y',(np.array([.5,.8])@inverse.T)[1],-.15,anchors=['−0.15'])
ratio_density=integrate.quad(lambda s:4*s*math.exp(-2*s),0,np.inf)[0]
check('P05','exponential ratio marginal integrates to one and P(R<=.25)',[ratio_density,ratio_density*.25],[1,.25],anchors=['0.25'])
# The mathematical range argument for non-independence is analytic, not inferred from a scatterplot.
pd=integrate.quad(lambda d:1-d,.75,1)[0]
check('P05','positive marginal events with impossible joint event',[.125,pd,0],[.125,1/32,0])

check('P06','Chebyshev bound at two sample sizes',[4/(1000*.2**2),4/(10000*.2**2)],[.1,.01],anchors=['0.1','0.01'])
check('P06','rare-spike finite-n probability and moments',[1/100,100/100,100**2/100],[.01,1,100],anchors=['0.01','E[Y_n]=1'])
for n in [1,2,7,20]:
    check('P06',f'alternating same-law variables at n={n}',np.mean([abs((-1)**n*z-z)>1 for z in [-1,1]]),n%2)
check('P06','CDF counterexample discontinuity and continuity points',
      [float(1/100<=0),float(0<=0),float(1/100<=.1),float(0<=.1)],[0,1,1,1],anchors=['F_n(0)=0','F(0)=1'])
check('P06','typewriter interval length at n=37',1/(2**int(math.log2(37))),1/32)
for u in [0.,.125,.314159,.999]:
    for k in [1,3,6]:
        hits=sum(j/2**k<=u<(j+1)/2**k for j in range(2**k))
        check('P06',f'typewriter one visit per block for u={u}, k={k}',hits,1)

assert set(c['lesson'] for c in checks)==set(SOURCES)=={f'P{i:02}' for i in range(1,7)}
report={'status':'passed','checked_at':datetime.now(timezone.utc).isoformat(),'source_commit':os.environ.get('GITHUB_SHA'),
        'lesson_count':6,'numerical_checks':len(checks),'checks':checks,
        'sources':{k:{a:b for a,b in v.items() if a!='text'} for k,v in SOURCES.items()},
        'environment':{'numpy':np.__version__,'scipy':scipy.__version__},
        'limits':['Finite numerical checks do not prove asymptotic convergence, existence or uniqueness theorems.',
                  'Proof assumptions and nonnumerical explanations are reviewed separately.',
                  'No independent human mathematical peer review is claimed.']}
output=ROOT/'project-docs/pregrade1/checks/math.json';output.parent.mkdir(parents=True,exist_ok=True)
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['checks','sources']},ensure_ascii=False,indent=2))
