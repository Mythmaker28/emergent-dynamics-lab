"""Audit-only helpers. No engine imports or simulation entry points."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.stats import rankdata
HERE=Path(__file__).resolve().parents[1]
REPO=HERE.parents[1]
REC=HERE/'recovery'
OUT=HERE/'results'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,obj):
 OUT.mkdir(exist_ok=True)
 (OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
def groups_centres(cells,L=36,radius=5):
 """Dense adjacency + graph traversal, integer squared torus distance."""
 cells=np.asarray(cells,dtype=int).reshape(-1,2)
 delta=np.abs(cells[:,None]-cells[None,:]); delta=np.minimum(delta,L-delta)
 adjacency=(delta**2).sum(axis=2)<=radius**2
 todo=set(range(len(cells))); groups=[]; centres=[]
 while todo:
  start=min(todo); todo.remove(start); g={start}; frontier=[start]
  while frontier:
   neighbours=set(np.flatnonzero(adjacency[frontier.pop()])) & todo
   todo-=neighbours; g|=neighbours;frontier.extend(neighbours)
  idx=sorted(g); groups.append(idx)
  anchor=cells[idx[0]]; offsets=(cells[idx]-anchor+L/2)%L-L/2
  centres.append(((anchor+offsets.mean(axis=0))%L).tolist())
 return groups,np.asarray(centres).reshape(-1,2)
def signed_rank(d):
 """Exact sign distribution by generating polynomial; Pratt includes zeros in ranks."""
 d=np.asarray(d,float); ranks=rankdata(abs(d),method='average')
 weights=[int(2*r) for r,x in zip(ranks,d) if x!=0]
 coeff=np.array([1],dtype=object)
 for w in weights:
  nxt=np.zeros(len(coeff)+w,dtype=object); nxt[:len(coeff)]+=coeff;nxt[w:]+=coeff;coeff=nxt
 observed=int(2*sum(ranks[d>0])); total=sum(weights)
 tail=sum(v for i,v in enumerate(coeff) if abs(2*i-total)>=abs(2*observed-total))
 p=float(tail/(2**len(weights)))
 walsh=sorted((float(x)+float(y))/2 for i,x in enumerate(d) for y in d[i:])
 # Reproduce frozen untied Walsh-order interval. NOT a new coverage proof for ties/zeros.
 untied=np.array([1],dtype=object)
 for w in range(1,len(d)+1):
  nxt=np.zeros(len(untied)+w,dtype=object);nxt[:len(untied)]+=untied;nxt[w:]+=untied;untied=nxt
 target=.025*2**len(d);cumulative=0
 for cut,v in enumerate(untied):
  cumulative+=v
  if cumulative>target:break
 return {'W_plus':observed/2,'exact_two_sided_p':p,'median_difference':float(np.median(d)),
         'hodges_lehmann':float(np.median(walsh)),'hl_interval':[walsh[cut],walsh[-1-cut]],
         'n_zero':int(sum(d==0)),'n_nonzero':int(sum(d!=0))}
