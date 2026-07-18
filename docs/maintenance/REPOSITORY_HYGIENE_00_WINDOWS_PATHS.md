# Windows historical-path handling

## Scope

Historical commit f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77 contains 19
tracked generated cache names that cannot be materialized by ordinary Git for
Windows because each name contains the forbidden vertical-bar character.

The maintenance branch does not rewrite that commit. It removes every current
results/_tomo_cache artefact from its own tip: 19 invalid names plus 15 valid
hash-named cache files, 34 files total. The directory is now ignored precisely
by results/_tomo_cache/.

## Exact invalid paths

1. results/_tomo_cache/BASE|1111|ph0|rg(0, 20, 0, 100).pkl
2. results/_tomo_cache/BASE|1111|ph0|rgNone.pkl
3. results/_tomo_cache/BASE|1111|ph15|rgNone.pkl
4. results/_tomo_cache/BASE|1111|ph30|rgNone.pkl
5. results/_tomo_cache/BASE|1111|ph45|rgNone.pkl
6. results/_tomo_cache/DECOY_EATERS|1111|ph0|rgNone.pkl
7. results/_tomo_cache/DELAY_k1|1111|ph0|rgNone.pkl
8. results/_tomo_cache/DELAY_k2|1111|ph0|rgNone.pkl
9. results/_tomo_cache/DELAY_k4|1111|ph0|rgNone.pkl
10. results/_tomo_cache/DELAY_k8|1111|ph0|rgNone.pkl
11. results/_tomo_cache/DIRECT_1PATH|1|ph0|rgNone.pkl
12. results/_tomo_cache/FIVE_CHAN|11111|ph0|rgNone.pkl
13. results/_tomo_cache/GATE3|1110|ph0|rgNone.pkl
14. results/_tomo_cache/INERT_DECOR|1111|ph0|rgNone.pkl
15. results/_tomo_cache/REDUNDANT_2PATH|1|ph0|rgNone.pkl
16. results/_tomo_cache/SP45|1111|ph0|rgNone.pkl
17. results/_tomo_cache/T10|1111|ph0|rgNone.pkl
18. results/_tomo_cache/T20|1111|ph0|rgNone.pkl
19. results/_tomo_cache/XINHIB|1111|ph0|rgNone.pkl

The path/blob/size inventory is also machine-readable in
external_recovery_manifest.json under windows_invalid_head_paths.

## Safe historical worktree command

Choose a target path that does not exist:

~~~powershell
.\scripts\New-IsolatedWorktree.ps1 -Repository 'C:\Users\tommy\Documents\ising v3' -Path 'C:\Users\tommy\Documents\ising-v3-historical' -Commitish f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77
~~~

To create a new branch rather than a detached worktree:

~~~powershell
.\scripts\New-IsolatedWorktree.ps1 -Repository 'C:\Users\tommy\Documents\ising v3' -Path 'C:\Users\tommy\Documents\ising-v3-historical-branch' -Commitish f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77 -Branch maintenance/example-historical-view
~~~

The helper refuses:

- an occupied filesystem target;
- an already registered target whose directory is absent;
- an existing branch name;
- an unresolved commit;
- any Windows-invalid path outside results/_tomo_cache;
- a final HEAD, index-tree, sparse-skip, or clean-status mismatch.

Sparse materialization changes only which files appear in the filesystem.
Verification requires git write-tree to equal the requested commit tree. The
19 excluded paths remain in the index as skip-worktree entries and therefore
remain part of the historical commit.

If validation fails after registration, the helper attempts a normal,
non-force removal of only the worktree it just created. A helper-created branch
is removed only with an expected-value ref update while it still points to the
resolved requested commit. If cleanup cannot be proven safe, the diagnostic
registration is preserved and the error gives its exact path.

## Qualified evidence

Synthetic tests cover:

- exact tree preservation with an invalid cache path;
- refusal to overwrite an occupied target;
- refusal of an undocumented invalid path;
- literal sparse handling of star and question-mark metacharacters.

Real f3921a4 qualification on Windows produced:

- requested HEAD: f3921a4d2eb4f3c5d8c88855048d32bcd0c02a77;
- expected and actual tree: 8672babd1bc11d5912cf4820b06fa5947ebcd04b;
- exact skip count: 19;
- status entries: 0.

The temporary qualified worktree was removed after the clean verification.
