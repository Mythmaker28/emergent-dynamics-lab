# One-command reproduction of the sign-safe consolidation results.
PYcache := /tmp/rpc_paper_v2
reproduce-paper:
	-@rm -rf $(PYcache)
	@PYTHONDONTWRITEBYTECODE=0 PYTHONPYCACHEPREFIX=$(PYcache) PYTHONHASHSEED=0 \
		python3 consolidation/reproduce.py

# NASI (noise-aware) deterministic reproduction + determinism check
NASI_PYC := /tmp/rpc_nasi_v2
reproduce-nasi:
	-@rm -rf $(NASI_PYC)
	@cd noise_aware && PYTHONDONTWRITEBYTECODE=0 PYTHONPYCACHEPREFIX=$(NASI_PYC) PYTHONHASHSEED=0 python3 reproduce_nasi.py

reproduce-paper-all: reproduce-paper reproduce-nasi

# Point-certification (PC) deterministic reproduction
PC_PYC := /tmp/rpc_pc_v2
reproduce-pc:
	-@rm -rf $(PC_PYC)
	@cd point_cert && PYTHONDONTWRITEBYTECODE=0 PYTHONPYCACHEPREFIX=$(PC_PYC) PYTHONHASHSEED=0 python3 reproduce_pc.py

reproduce-all: reproduce-paper reproduce-nasi reproduce-pc
	@cd noise_aware && PYTHONPYCACHEPREFIX=/tmp/rpc python3 verify_freeze.py
	@cd point_cert && PYTHONPYCACHEPREFIX=/tmp/rpc python3 verify_pc_freeze.py
	@cd noise_aware && PYTHONPYCACHEPREFIX=/tmp/rpc python3 -B make_figures.py
	@cd point_cert && PYTHONPYCACHEPREFIX=/tmp/rpc python3 -B make_pc_figure.py
	@echo "reproduce-all: OK (reproductions + freeze verifies + figures)"
