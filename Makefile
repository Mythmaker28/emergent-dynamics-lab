# One-command reproduction of the sign-safe consolidation results.
PYcache := /tmp/reproduce_pycache
reproduce-paper:
	@rm -rf $(PYcache)
	@PYTHONDONTWRITEBYTECODE=0 PYTHONPYCACHEPREFIX=$(PYcache) PYTHONHASHSEED=0 \
		python3 consolidation/reproduce.py

# NASI (noise-aware) deterministic reproduction + determinism check
NASI_PYC := /tmp/nasi_reproduce_pyc
reproduce-nasi:
	@rm -rf $(NASI_PYC)
	@cd noise_aware && PYTHONDONTWRITEBYTECODE=0 PYTHONPYCACHEPREFIX=$(NASI_PYC) PYTHONHASHSEED=0 python3 reproduce_nasi.py

reproduce-paper-all: reproduce-paper reproduce-nasi
