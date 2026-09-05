# TBRT02 — reconstruction de trois archives perdues. DÉCLARÉ AVANT DE LANCER.

## Ce qui s'est passé

Le vingt-troisième retour arrière du conteneur (29 août 2026) a effacé les archives brutes des
triplets **793, 827 et 866**. Elles n'avaient jamais traversé le pont vers l'ordinateur, coupé de
03:57 UTC jusqu'à la fin de la mission. Les trente-huit autres triplets étaient sur le disque et
sont récupérés.

## Ce que je vais faire, et ce que ce n'est PAS

Je relance `tbrt02_fork.one_seed(index, seed)` sur ces trois indices, avec les graines du
registre. **Ce n'est pas une nouvelle mesure.** Ce sont trois mondes déjà exécutés, déjà comptés
au registre scellé, dont l'admissibilité est déjà décidée et dont le coût est déjà imputé aux
609,5 instances-bras. Rien de ce qui suit ne peut changer un résultat :

- **aucune graine nouvelle** — 2464723753, 2833493710, 573170435, toutes trois déjà au manifeste
  et déjà consommées ;
- **aucune ligne ajoutée ou modifiée au registre scellé** — le script ne l'ouvre qu'en lecture ;
- **aucun compteur touché** — ni les 885 graines, ni les 41 triplets, ni les 609,5 instances ;
- **aucun procès-verbal rouvert** — C3, C4, C4-bis et C5 sont écrits, hachés et clos.

C'est la reconstruction d'un artefact perdu, pas une expérience.

## Le critère de réussite, fixé maintenant

Le moteur est déterministe et le `METHODS_HASH` se reproduit à l'identique après restauration
(21571fb4cb1df9ac2e9089924e9d6ee5d4d63c920a007e188bdc24e0d94d1f99). Les mêmes graines sous les
mêmes méthodes doivent donc redonner **les mêmes octets**. Le registre a scellé les sha256 au
moment où les archives ont été écrites ; ce sont eux, et rien d'autre, qui jugent :

| index | graine | bras | sha256 scellé |
|-------|--------|------|----------------|
| 793 | 2464723753 | SHAM | 3934b8737c29a677686d3ef02d592934a241dd1a2e442d1aa33affd758f199ac |
| 793 | 2464723753 | SELECTIVE | 4b5edee39aaf16cec4a5fde3ae5167b93e1db0980a0bb181c4e8f260d0cd7f60 |
| 793 | 2464723753 | DISPLACED | 90718677fa873a987a321dbaad7d74edee45a8c5c392657fc6c70711320a73b8 |
| 827 | 2833493710 | SHAM | b8d31354f0d90318803de17c18a55536abaf37b31260ff86b9ef7adf4e84be6c |
| 827 | 2833493710 | SELECTIVE | 00a58aabbd2b5d493b6149e57a5428719702c7b56f768730c6ddcbf3c796edd6 |
| 827 | 2833493710 | DISPLACED | 3c71d35a796cc42d3a825499f3d3b36aaa7906dad3c9a0b7008b95aae02cad62 |
| 866 | 573170435 | SHAM | 312f2d4b85e6ade6abeb8e61cc8da96a9374943df318c80124918f4dd1ac9b26 |
| 866 | 573170435 | SELECTIVE | ebd2d61d49331cd4207eafe9c143be38bbd05ab172e80193c37ce1171f5fb50a |
| 866 | 573170435 | DISPLACED | 0b3bc95b4eb478384674438e40879ecba1a0bbc4e9f50abb201564ffc632b6b0 |

Les t_m attendus sont 1568, 919 et 1006.

**RÉUSSITE** = les neuf sha256 coïncident, et les t_m aussi. L'archive est alors l'archive
d'origine, au bit près, et le brut redevient complet à 41 sur 41.

**ÉCHEC** = un seul écart. Dans ce cas les fichiers reconstruits sont écartés, **ils ne sont pas
mis dans TBRT02_raw**, et l'écart devient le résultat : il signifierait que le pipeline n'est pas
déterministe sous restauration, ce qui serait un fait plus important que trois archives. Il serait
écrit tel quel, et le brut resterait déclaré à 38 sur 41.

**Aucune troisième issue.** Je ne garde pas une archive « presque bonne », je ne compare pas des
résumés à la place des octets, et je n'ajuste pas le critère après avoir vu le résultat.

## Ce que la réussite prouverait en plus

Elle vaudrait comme test de reproductibilité de bout en bout : mêmes graines, méthodes restaurées
depuis deux canaux de sauvegarde distincts, mêmes octets. C'est une vérification que la mission
n'avait pas prévue et que le rollback offre gratuitement. Elle ne serait revendiquée que si elle
passe.

## Statuts inchangés

H3_STATUS = NOT_TESTED ; REPRODUCTION_STATUS = NOT_TESTED ; HEREDITY_STATUS = NOT_TESTED ;
AUTONOMOUS_COHESION_STATUS = NOT_ESTABLISHED ; X_LAWSPEC_BASELINE = UNCHANGED ;
ARCHITECTURE_CHANGE_NECESSITY = NOT_ESTABLISHED ;
COMPANION_PAPER_V1_1_STATUS = UNPUBLISHED__NOT_SUBMITTED__PUBLICATION_DEFERRED ;
OMLDCT02_STATUS = INSUFFICIENT_ADMISSIBLE_PAIRED_BLOCKS__UNCHANGED ;
CLEA01_STATUS = CLOSED__LINEAGE_ROUTE_PAUSED__NOT_REOPENED ;
TBRT02_STATUS = CLOSED__RAW_COMPLETE__PRIMARY_ADJUDICATION_INCONCLUSIVE_BY_CONSTRUCTION.

Le mot « reproduction » n'apparaît ici qu'au sens informatique de la reproductibilité d'un calcul.
Il ne dit rien d'un objet du monde.
