"""Adversarial tests of the delivered verifier, not new scientific experiments."""
import hashlib
import numpy as np
import pytest
from audit_final import verify_sources, radial_quantile

@pytest.mark.parametrize('fault',['missing','size','hash'])
def test_source_corruption_is_rejected(tmp_path,fault):
    original=b'fixed source bytes';p=tmp_path/'input.bin'
    manifest={'files':[dict(path=p.name,bytes=len(original),sha256=hashlib.sha256(original).hexdigest())]}
    if fault=='size':p.write_bytes(original+b'x')
    elif fault=='hash':p.write_bytes(b'X'+original[1:])
    with pytest.raises(AssertionError):verify_sources(tmp_path,manifest)

def test_radius_respects_periodic_seam_and_mass_threshold():
    field=np.zeros((6,6));field[0,0]=1;field[5,0]=8;field[3,0]=1
    assert radial_quantile(field,0,0)==1
    assert radial_quantile(np.roll(field,2,axis=1),0,2)==1
