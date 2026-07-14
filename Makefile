# One-command reproduction of the sign-safe consolidation results.
PYcache := /tmp/reproduce_pycache
reproduce-paper:
	@rm -rf $(PYcache)
	@PYTHONDONTWRITEBYTECODE=0 PYTHONPYCACHEPREFIX=$(PYcache) PYTHONHASHSEED=0 \
		python3 consolidation/reproduce.py
