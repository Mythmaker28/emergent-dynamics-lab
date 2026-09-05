"""Exact untied continuous symmetric-model coverage of the frozen Walsh index choice."""
from common import *
def main():
 n=41;coef=np.array([1],dtype=object)
 for w in range(1,n+1):
  new=np.zeros(len(coef)+w,dtype=object);new[:len(coef)]+=coef;new[w:]+=coef;coef=new
 cumul=0
 for k,c in enumerate(coef):
  cumul+=c
  if cumul>.025*2**n:break
 pairs=read(OUT/'OMLDCT03_PER_PAIR.json');corrections={}
 for name,key in [('duration','E3_DURATION'),('exposure','E3_EXPOSURE')]:
  d=[math.log(r['arms']['SELECTIVE'][key])-math.log(r['arms']['SHAM'][key]) for r in pairs]
  walsh=sorted((x+y)/2 for i,x in enumerate(d) for y in d[i:])
  corrections[name]={'distinct_absolute_differences':len(set(abs(x) for x in d)),
                     'descriptive_corrected_order_interval':[walsh[k-1],walsh[-k]],
                     'frozen_interval':[walsh[k],walsh[-1-k]]}
 out={'n':41,'first_cdf_index_exceeding_alpha_half':k,
      'frozen_interval_coverage_under_continuous_symmetric_untied_model':1-2*float(cumul/2**n),
      'corrected_conservative_coverage_same_model':1-2*float((cumul-coef[k])/2**n),
      'corrections_nonadjudicative':corrections,'frozen_files_modified':False,
      'scope':'Off-by-one in frozen CI endpoints; not a validation of symmetry or iid assumptions for these data.'}
 save('OMLDCT03_INTERVAL_INDEX_AUDIT.json',out);print(json.dumps(out))
if __name__=='__main__':main()
