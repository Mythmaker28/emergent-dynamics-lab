"""Recompute existing evidence only. No world construction, predictor simulation or API.

The source manifest is a pinned input, never rewritten by this command. Optional PQEC
verification checks a locally extracted external archive; it is not required to rebuild
the source-response paper's figures. Run this script before reconcile.py.
"""
import argparse
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import sys
import numpy as np
from scipy.stats import t
from paths import ROOT, PKG, PROV, read, digest, dump, require

def near(a, b, label, atol=1e-11):
    require(np.allclose(a, b, rtol=1e-11, atol=atol, equal_nan=False), f'{label}: {a} != {b}')

def verify_sources(root=ROOT, manifest=None):
    manifest = manifest or json.loads((PROV/'SOURCE_MANIFEST.json').read_text())
    for r in manifest['files']:
        p = root/r['path']
        require(p.is_file(), f'missing source: {r["path"]}')
        require(p.stat().st_size == r['bytes'], f'size mismatch: {r["path"]}')
        require(digest(p) == r['sha256'], f'hash mismatch: {r["path"]}')
    return len(manifest['files'])

def radial_quantile(field, y, x):
    L = len(field)
    yy, xx = np.indices(field.shape)
    dy, dx = np.abs(yy-y), np.abs(xx-x)
    d = np.hypot(np.minimum(dy,L-dy), np.minimum(dx,L-dx)).ravel()
    order = np.argsort(d,kind='stable')
    c = np.cumsum(field.ravel()[order])/field.sum()
    return float(d[order[np.searchsorted(c,.8,side='left')]])

def fresh():
    frz, val = read('OBFOR01/out/_freeze.json'), read('OBFOR01/out/_validation.json')
    seeds = frz['SEEDS']['FRESH_OBFOR01_SEEDS']
    expected = {(c,s) for c,ss in seeds.items() for s in ss}
    require(len(expected)==28 and all(len(v)==14 for v in seeds.values()),'frozen 14+14 allocation')
    require(len({s for _,s in expected})==28,'duplicate fresh seeds')
    require(not {s for _,s in expected}.intersection(frz['SEEDS']['RETIRED_SEEDS']),'retired seed reused')
    require(expected=={(a['condition'],a['seed']) for a in val['ARMS']},'arm register mismatch')
    files = list((ROOT/'OBFOR01/raw').glob('*.npz'))
    require(len(files)==28,'extra or missing raw arm')
    records=[]
    for a in val['ARMS']:
        rel=f'OBFOR01/raw/{a["tag"].replace("/","__")}.npz'
        with np.load(ROOT/rel,allow_pickle=False) as z:
            require(z['series'].shape==(11000,29),'series shape')
            require(z['hop_ledger'].shape==(44000,4),'hop shape')
            require(z['source_substep_ledger'].shape==(44000,6),'source ledger shape')
            require(z['birth_substep_ledger'].shape==(11000,6),'birth ledger shape')
            frames=[json.loads(str(s)) for s in z['frames']]
            require([f['step'] for f in frames]==list(range(50,11001,50)),'frame cadence/order')
            win=[f for f in frames if f['step']>2000]
            v=np.asarray([f['r80_organiser'] for f in win],float)
            require(len(v)==180 and np.isfinite(v).all(),'incomplete fresh window')
            nx=np.asarray([f['N_X'] for f in win],float)
            h=hashlib.sha256()
            for s in ('X','Y','SX','SY','WX','WY'):
                field=z[f'n{s}_final']; require(field.shape==(36,36),'lattice dimensions')
                require((field>=0).all(),'negative occupancy')
                h.update(np.ascontiguousarray(field).tobytes())
            h.update(b'11000')
            require(h.hexdigest()==a['state_hash_final'],'final state digest')
            yy,xx=np.nonzero(z['nY_final'])
            require(z['nY_final'].sum()==1,'single-source final state')
            near(radial_quantile(z['nX_final'],int(yy[0]),int(xx[0])),frames[-1]['r80_organiser'],'final frame quantile')
            near(z['nX_final'].sum(),frames[-1]['N_X'],'final frame population')
            hop=z['hop_ledger']; hx=hop[hop[:,1]==0]
            blocked=float(hx[:,3].sum()/hx[:,2].sum())
            vals={'r80_median':float(np.median(v)), 'r80_mean':float(v.mean()),
                  'r80_sd':float(v.std(ddof=1)), 'N_X_window_mean':float(nx.mean())}
            for k,vv in vals.items(): near(vv,a[k],f'{a["tag"]}/{k}')
            near(blocked,a['blocked_fraction']['X'],'blocking')
            require(not a['EXTINCT'] and a['tracker_consistent_with_counts'],'valid arm flags')
            records.append(dict(tag=a['tag'],condition=a['condition'],seed=a['seed'],
                frames=180,final_state_sha256=h.hexdigest(),blocked_fraction=blocked,**vals))
    records.sort(key=lambda x:(x['condition'],x['seed']))
    near(np.mean([r['blocked_fraction'] for r in records]),read('OBFOR01/out/_adjudication.json')['TECHNICAL']['blocked_fraction_X_mean'],'global blocking mean')
    means={c:np.array([a['r80_median'] for a in records if a['condition']==c]) for c in ('S','M')}
    repair=read('SEAL01/out/OBFOR01_SEAL_REPAIR_EVIDENCE.json')
    endpoints={}
    for name,c,ky in [('static','S','STATIC'),('mobile','M','MOBILE')]:
        v=means[c]; pred=frz['PRIMARY_PREDICTIONS'][ky+'_ABSOLUTE_PROFILE_COMPATIBILITY']['predicted_r80_median']
        m=float(v.mean()); se=float(v.std(ddof=1)/math.sqrt(len(v))); rel=100*(m/pred-1)
        post_se=100*se/pred
        sigma=repair['R3_PREDICTION_MONTE_CARLO_SD'][name+'_percent']
        e=dict(n=len(v),predicted=pred,observed=m,relative_error_percent=rel,se_percent=post_se,
               prediction_mc_sd_percent=sigma,point_pass=abs(rel)<=2.9,
               diagnostic_t95=[rel-t.ppf(.975,13)*post_se,rel+t.ppf(.975,13)*post_se],
               diagnostic_tost_p=float(t.sf((2.9-abs(rel))/post_se,13)))
        r=repair['R6_FRESH_STATISTICS_RESTATED'][name]
        near(m,r['observed'],name+' observation');near(rel,r['relative_error_percent'],name+' error')
        near(e['diagnostic_tost_p'],r['TOST_p_t_13_df__CORRECTED'],name+' corrected TOST',atol=1e-10)
        endpoints[name]=e
    s,m=endpoints['static'],endpoints['mobile']
    pred=frz['PRIMARY_PREDICTIONS']['MOBILE_STATIC_RATIO_COMPATIBILITY']['predicted_ratio_under_M6']
    ratio=m['observed']/s['observed']; rel=100*(ratio/pred-1)
    # Exact delta-method scaling for a ratio expressed relative to a fixed prediction.
    relative_se=math.hypot(m['se_percent']*m['predicted']/100/m['observed'],s['se_percent']*s['predicted']/100/s['observed'])
    corrected_se=100*ratio/pred*relative_se
    endpoints['ratio']=dict(n_static=14,n_mobile=14,predicted=pred,observed=ratio,
        relative_error_percent=rel,se_percent=corrected_se,
        historical_se_percent=100*relative_se,prediction_mc_sd_percent=repair['R6_FRESH_STATISTICS_RESTATED']['ratio']['PREDICTION_MONTE_CARLO_SD_percent'],
        point_pass=abs(rel)<=2.9,diagnostic_note='Delta SE corrected by observed/predicted; no new confirmatory criterion.')
    near(ratio,repair['R6_FRESH_STATISTICS_RESTATED']['ratio']['observed'],'ratio')
    with (PROV/'FRESH_ARM_RECOMPUTATION.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
    return records,endpoints

def ideal_r80(L,mobile,p_hop=.10263340389897246,mu=.004):
    # Reproduce the frozen reference implementation, not a new claim of kernel exactness.
    q=p_hop/4
    a=2*q*(1-q)*(2 if mobile else 1)
    k=2*np.pi*np.arange(L)/L
    one=1-a*(1-np.cos(k))
    f=np.maximum(np.fft.ifft2(1/(1-(1-mu)*one[:,None]*one[None,:])).real,0)
    return radial_quantile(f,0,0)

def historical():
    rows=[]
    for prog,prefix,mobile in [('OBDI02','L',True),('OBTC02','S__',False),('OBTC02','P__',True)]:
        for p in sorted((ROOT/prog/'raw').glob(prefix+'*.npz')):
            with np.load(p,allow_pickle=False) as z:
                frames=[json.loads(str(s)) for s in z['frames']]
                v=np.array([f['r80_organiser'] for f in frames if f['step']>2000 and f.get('r80_organiser') is not None and np.isfinite(f['r80_organiser'])])
                rows.append(dict(file=p.name,programme=prog,mobile=mobile,L=len(z['nX_final']),
                    final_X=int(z['nX_final'].sum()),final_Y=int(z['nY_final'].sum()),frames=len(v),median=float(np.median(v)) if len(v) else None))
    mob=[r for r in rows if r['programme']=='OBDI02' and r['final_Y']>=1]
    levels={}
    sealed=read('SEAL01/out/OBFOR01_SEAL_REPAIR_EVIDENCE.json')
    for key,pred in [('A_mission_rule__nX_final_ge_40_and_ge_50_frames',lambda r:r['final_X']>=40 and r['frames']>=50),
                     ('B_drop_the_population_threshold__keep_ge_50_frames',lambda r:r['frames']>=50),
                     ('C_no_outcome_dependent_threshold_at_all',lambda r:r['frames']>=1)]:
        selected=[r for r in mob if pred(r)]
        v=np.array([r['median']/ideal_r80(r['L'],True) for r in selected])
        levels[key]=dict(n=len(v),percent=float(100*(v.mean()-1)),se_percent=float(100*v.std(ddof=1)/math.sqrt(len(v))))
        for k,x in levels[key].items():near(x,sealed['R5_INCLUSION_RULE_SENSITIVITY']['LEVELS'][key][k],'historical '+key+'/'+k)
    S=[r['median'] for r in rows if not r['mobile'] and r['final_Y']>=1 and r['final_X']>=40 and r['frames']>=50]
    M=[r['median'] for r in mob if r['L']==36 and r['final_X']>=40 and r['frames']>=50]
    baseline=dict(static=float(np.mean(S)),mobile=float(np.mean(M)),n_static=len(S),n_mobile=len(M))
    baseline['ratio']=baseline['mobile']/baseline['static']
    for nm in ['static','mobile']:
        near(baseline[nm],sealed['R4_DISCRIMINATING_POWER']['NULL_BASELINE'][f'predicted_{nm}_r80_median'],'historical baseline '+nm)
    with (PROV/'HISTORICAL_ARM_RECOMPUTATION.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    return levels,baseline,len(rows)

def replicates():
    repair=read('SEAL01/out/OBFOR01_SEAL_REPAIR_EVIDENCE.json')
    with np.load(ROOT/'SEAL01/out/_repair_replicates.npz',allow_pickle=False) as z:
        require(set(z.files)=={'mobile_empirical','mobile_poisson','static_empirical','mobile_poisson_2B'},'replicate keys')
        vals={k:(100*(z[k]/ideal_r80(36,k!='static_empirical')-1)).tolist() for k in z.files}
        for v in vals.values():require(len(v)==16 and np.isfinite(v).all(),'16 finite stored replicates')
    stats={k:dict(mean=float(np.mean(v)),sd=float(np.std(v,ddof=1))) for k,v in vals.items()}
    for nm,ky in [('static','static_empirical'),('mobile','mobile_empirical')]:
        near(stats[ky]['sd'],repair['R3_PREDICTION_MONTE_CARLO_SD'][nm+'_percent'],'predictor sigma '+nm)
    diff=stats['mobile_empirical']['mean']-stats['mobile_poisson']['mean']
    se=math.hypot(stats['mobile_empirical']['sd'],stats['mobile_poisson']['sd'])/4
    near(diff,repair['R1_BIRTH_FLUX_ABLATION_REPLICATED']['difference_pp'],'birth flux effect')
    near(se,repair['R1_BIRTH_FLUX_ABLATION_REPLICATED']['se_pp'],'birth flux effect SE')
    return dict(values=vals,stats=stats,difference_pp=diff,se_pp=se)

def pqec(path):
    man=read('PQEC01/out/PQEC01_RAW_MANIFEST.json')
    base=Path(path)
    require(len(list(base.glob('*.npz')))==man['N_ARCHIVES'],'PQEC archive count')
    rows=[]
    for r in man['ARCHIVES']:
        p=base/r['file'];require(p.stat().st_size==r['bytes'],'PQEC size '+p.name)
        require(digest(p)==r['sha256'],'PQEC hash '+p.name)
        with np.load(p,allow_pickle=False) as z:
            require(sorted(z.files)==sorted(r['keys']),'PQEC schema '+p.name)
            rows.append(dict(file=p.name,bytes=p.stat().st_size,sha256=r['sha256'],shapes={k:list(z[k].shape) for k in ['scalars','final','ybirth','src']}))
    result=dict(status='PASS',archives=len(rows),total_bytes=sum(r['bytes'] for r in rows),rows=rows)
    dump(PROV/'PQEC01_EXTERNAL_RAW_AUDIT.json',result)
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pqec-raw');args=ap.parse_args()
    n=verify_sources()
    arms,endpoints=fresh();levels,baseline,historical_n=historical();reps=replicates()
    scores=read('SEAL01/out/OBFOR01_SEAL_REPAIR_EVIDENCE.json')['R4_DISCRIMINATING_POWER']['NULL_SCORED_ON_THE_THREE_FROZEN_ENDPOINTS']
    for name in ('static','mobile','ratio'):
        near(100*(endpoints[name]['observed']/baseline[name]-1),scores[name]['relative_error_percent'],'baseline error '+name)
    if args.pqec_raw: pqec(args.pqec_raw)
    data=dict(status='PASS',source_files_verified=n,scientific_world_starts=0,new_predictor_simulations=0,
       fresh_arms=arms,endpoints=endpoints,historical_levels=levels,historical_baseline=baseline,historical_archives_read=historical_n,
       replicates=reps,sealed_disposition=read('SEAL01/out/_seal_adjudication.json')['FINAL_DISPOSITION'],
       limits=['Stored per-frame radii audited; full intermediate lattice states are absent from OBFOR01 NPZ files.',
               'Final lattice radius independently recomputed for each arm; full engine trajectories not rerun.',
               'Prediction Monte Carlo replicas are existing SEAL01 arrays, not new samples.',
               'Historical reference profile reproduces the frozen operator implementation; no new proof of full kernel exactness.'])
    dump(PROV/'AUDIT_RESULTS.json',data)
    print(json.dumps({k:data[k] for k in ['status','source_files_verified','scientific_world_starts','new_predictor_simulations','historical_archives_read']}))
    print('Fresh: 28 arms, 5040 analysis frames; historical selection:',[r['n'] for r in levels.values()])

if __name__=='__main__':main()
