import json, math, numpy as np, scipy.sparse, scipy.sparse.linalg, yaml
exec(open('/home/claude/FTCTR01/code/ftctr01_exact.py').read().split('# --- method A')[0])
I=scipy.sparse.identity(NT,format="csr"); A=(I-Q).tocsc()
m1=scipy.sparse.linalg.spsolve(A,np.ones(NT))
m2=scipy.sparse.linalg.spsolve(A,np.ones(NT)+2.0*(Q@m1))     # (I-Q)m2 = 1 + 2 Q m1
E1=float(m1[idx[0,0]]); E2=float(m2[idx[0,0]])
sd_solve=math.sqrt(E2-E1*E1)
# survival-sum second moment, exact identity E[t^2] = sum_{t>=0} (2t+1) P(t>t)
v=np.zeros(NT); v[idx[0,0]]=1.0; S=[]; t=0
while True:
    s=float(v.sum()); S.append(s)
    if s<1e-18 or t>600000: break
    v=Q.T@v; t+=1
S=np.array(S); tt=np.arange(len(S))
E1b=float(S.sum()); E2b=float(((2*tt+1)*S).sum()); sd_surv=math.sqrt(E2b-E1b*E1b)
print(json.dumps({"E1_solve":E1,"E1_survival":E1b,"E2_solve":E2,"E2_survival":E2b,
 "SD_solve":sd_solve,"SD_survival":sd_surv,
 "SD_METHODS_AGREE":abs(sd_solve-sd_surv)<1e-6*sd_solve,
 "tail_steps_used":len(S)},indent=2))
J=json.load(open('/home/claude/FTCTR01/out/FTCTR01_FIRST_PASSAGE.json'))
J.update({"E_tau2_method_A_linear_solve":E2,"E_tau2_method_B_survival_sum":E2b,
 "SD_tau_method_A":sd_solve,"SD_tau_method_B":sd_surv,
 "SD_METHODS_AGREE":bool(abs(sd_solve-sd_surv)<1e-6*sd_solve),"SD_tau":sd_solve,
 "frozen_understates_by_percent_of_exact":100.0*(E1-125.0)/E1,
 "frozen_understates_by_percent_of_frozen":100.0*(E1-125.0)/125.0})
json.dump(J,open('/home/claude/FTCTR01/out/FTCTR01_FIRST_PASSAGE.json','w'),indent=2)
print("understates_pct_of_exact",100.0*(E1-125.0)/E1,"of_frozen",100.0*(E1-125.0)/125.0)
