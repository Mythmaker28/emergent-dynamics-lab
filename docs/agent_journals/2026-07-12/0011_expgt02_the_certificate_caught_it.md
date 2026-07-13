# EXP-GT-02 — the certificate caught it before I could believe anything (2026-07-12)

The S head is repaired, and it now reads every known memory word exactly — including across a held-out layout, and
including **1010 vs 0101**, the case where the old head returned 0.000 and told me two different programs were
identical.

The old probe was not badly weighted. It was **blind**: a stride-20 scan starting at column 20, on channels whose
tracks sit at 34, 74, 114 and 154. It never touched a single one. You cannot tune a distance function into sight, and
if I had "improved" it until (e) passed I would have been fitting noise from a sensor pointed at a wall.

## The bug the certificate caught
The repaired probe's first run read `010` for both 1010 and 0101 — still wrong. The cause was not physics. The
deletion arm summed the output over **272 frames** against a **281-frame baseline**, so it registered a "drop" at
**every column in the scan, including empty space**. A pure accounting artefact, firing everywhere, indistinguishable
from a beautifully sensitive instrument if you only looked at the summary.

I found it in one diagnostic because the coverage certificate *demanded I read a word I already knew the answer to*
before being allowed to read one I didn't. That requirement — prove you can measure the known before you measure the
unknown — is now the most valuable rule in this project, and it came from the user, not from me.

## What is still broken
A and F are still confounded: I am comparing a transient post-handoff frame against a fresh initialization, which
compares clock phases, not architectures. That is a phase-matching repair, not a tuning one. L must still demonstrate
it will say **INDETERMINATE** on exact copies rather than inventing a lineage difference.

Droplets stay blocked. Nothing promoted. But for the first time in this whole metrology arc, one head is not lying.
