# Verdict français — liaison d'autorisation 03I

La défaillance était limitée au contrat d'autorisation : la phrase acceptée contenait un placeholder littéral au
lieu du SHA-256 calculé du sceau final.

Le manifeste fige maintenant un template unique avec `{final_seal_sha256}`. Le runner calcule le SHA-256 canonique
du futur sceau, exige le même hash minuscule de 64 caractères dans le champ indépendant `final_seal_sha256`,
substitue ce hash dans la phrase, puis compare `approval_phrase` exactement, sans normaliser la casse, les espaces,
la ponctuation, la longueur ou Unicode.

Les placeholders littéraux `{final_seal_sha256}` et `<FINAL_SEAL_SHA256>` sont rejetés. Le test synthétique correct,
lié au hash dans les deux emplacements, est accepté par le validateur. Tout échec survient avant l'initialisation du
registre et avant l'import du moteur.

La régression est complète : 03G 7/7 avec A–F, 03E 18/18, 03C 9/9, tracker 10/10, tracer/événements, chaîne DEV,
compilation, puissance et environnement propre. Le replay DEV n'a pas initialisé le moteur et conserve
strictement les sous-arbres scientifiques et de faisabilité du seed déjà ouvert 50001.

Aucun seed `54xxx` n'a été exécuté. Aucun répertoire prospectif, sceau final ou autorisation humaine valide n'a été
créé. L'ancien sceau
`536cf0351bd65e6fc7efafb2d4a5acc86b99e244abe69c1bbcd8baad04022f62` est marqué
**RETIRED — AUTHORIZATION TEMPLATE BINDING DEFECT** et ne peut pas être réutilisé.

Un auditeur indépendant doit maintenant produire un nouveau sceau, puis une autorisation humaine distincte doit
lier exactement ce nouveau hash dans le champ et dans la phrase.

**Recommandation : READY FOR NARROW RE-AUDIT.**
