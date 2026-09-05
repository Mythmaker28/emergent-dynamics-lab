"""Analytic fixtures only; no scientific world or engine initialized."""
import itertools,unittest
import numpy as np
from scipy.stats import rankdata
from common import groups_centres,signed_rank
class AuditTests(unittest.TestCase):
 def test_pratt_exact_ties_and_zero_against_enumeration(self):
  for d in [[0,1,-1,2,-3],[0,0,0],[1,2,3,4,5]]:
   r=rankdata(np.abs(d));nz=[v for v,x in zip(r,d) if x];obs=sum(v for v,x in zip(r,d) if x>0);mid=sum(nz)/2
   weights=[sum(v*s for v,s in zip(nz,bits)) for bits in itertools.product([0,1],repeat=len(nz))]
   exact=sum(abs(x-mid)>=abs(obs-mid) for x in weights)/len(weights)
   self.assertEqual(signed_rank(d)['exact_two_sided_p'],exact)
 def test_sign_reversal(self):
  a=signed_rank([0,1,-1,2,-3]);b=signed_rank([0,-1,1,-2,3]);self.assertEqual(a['exact_two_sided_p'],b['exact_two_sided_p'])
  self.assertEqual(a['hodges_lehmann'],-b['hodges_lehmann'])
 def test_torus_and_nonlocal_separation(self):
  g,c=groups_centres([[0,35],[0,0],[18,18]])
  self.assertEqual(g,[[0,1],[2]]);np.testing.assert_array_equal(c,[[0,35.5],[18,18]])
 def test_inclusive_radius(self):
  self.assertEqual(len(groups_centres([[0,0],[3,4]])[0]),1)
  self.assertEqual(len(groups_centres([[0,0],[4,4]])[0]),2)
if __name__=='__main__':unittest.main()
