# FSQBT00_EVIDENCE_COMPLETENESS_AUDIT

FSQBT00 required `FRESH_CHECKPOINT_AND_MASK_ARCHIVE` (full-field checkpoints), and allowed a support-restricted derivative only IN ADDITION to complete committed evidence. Its original tip committed the 12 masks and the support-restricted sham/active archives (with proven sufficiency), but committed only sha256 DIGESTS of the 12 full-field checkpoints (7.89 MB), keeping the bytes in the workspace (deviation D4). That original tip is therefore **INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES**.

FCRA00 recovers the exact bytes: all 12 checkpoints in the workspace match their FSQBT00-committed digests 12/12, and are committed here under `recovered_full_checkpoints/`. The 12 masks were already committed at the FSQBT00 tip. The full-field sham and active scored-time trajectories (24 + 24) are also present in the workspace and are digested for the record; they are not byte-committed here because the on-support residual autopsy is fully licensed by the committed support-restricted archives, whose bit-for-bit sufficiency is re-proved in commit 4.

`CHECKPOINT_BYTES_STATUS = RECOVERED_EXACT_BYTES_AND_COMMITTED`  
`MASK_EVIDENCE_STATUS = ORIGINAL_EXACT_BYTES_ALREADY_COMMITTED`  
`FSQBT00_ORIGINAL_TIP_DELIVERY_STATUS = INCOMPLETE_MISSING_FULL_CHECKPOINT_BYTES`  
`CURRENT_CHAIN_EVIDENCE_STATUS = COMPLETE_AFTER_APPEND_ONLY_CHILD_RECOVERY`
