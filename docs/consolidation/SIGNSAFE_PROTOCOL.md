# EXP-GT-SIGN-SAFE-REFERENCE-IDENTIFICATION-00 — PROTOCOL (committed before fitting)
Instrument: consolidation/signsafe.py (set-identification; 9 statuses; no max-amplitude default).
Inputs per case: drift-free channels v_i, pre-window slopes lam_i, DECLARED clean-anchor flag, DECLARED sign
contract (attenuate/amplify/None) established INDEPENDENTLY (not from amplitude ordering).
Split: dev seeds 51xxxxx, prospective 52xxxxx (bench.py). Prospective opened once after freeze.
Selection rule: fixed here. Correctness = the instrument's status matches the identifiability class implied by the
declared contract, AND when it emits a POINT/INTERVAL the true |q| is contained; when it emits NON_IDENTIFIABLE or
ILL_CONDITIONED that is the correct refusal. A confident POINT excluding the truth is a hard failure.
