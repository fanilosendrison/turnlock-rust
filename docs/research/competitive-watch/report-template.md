---
okf_version: "1.0"
kind: "KnowledgeAsset"
asset_type: "report-projection-template"
domain: "turnlock-competitive-watch"
severity: "strict"
name: "Competitive Guarantee Watch Report Template"
---

# Veille Turnlock / Turnlock Cloud — Rapport du {{date_locale}}

- **report_id :** `{{report_id}}`
- **type :** `{{report_kind}}`
- **fenêtre observée :** `{{period_start}}` → `{{period_end}}`
- **généré à :** `{{generated_at}}`
- **référence TURNLOCK :** `{{basis.turnlock_repository}}@{{basis.turnlock_commit}}`
- **version du schéma :** `{{schema_version}}`
- **version de la méthode :** `{{methodology_version}}`
- **statut de Turnlock Cloud :** `{{basis.turnlock_cloud_status}}`
- **caractère partiel éventuel :** `{{partiality_statement}}`

Ce modèle est une projection de `report.json`. Il ne contient aucune
observation concurrentielle. Le rendu ne doit ajouter aucun jugement, niveau,
fait, source ou conclusion absent du JSON.

## 1. Fenêtre d’observation et base de comparaison

{{observation_window_and_basis}}

Présenter les sources de référence et leurs révisions immuables, y compris la
méthode, le schéma et le modèle lorsqu'ils sont utilisés. Distinguer la période
couverte de la date de génération et expliciter toute histoire indisponible.

## 2. Synthèse

{{summary}}

Préserver les limites, inconnues et couvertures partielles. Une absence de
preuve publique ne devient pas une preuve d'absence de capacité.

## 3. Tableau des niveaux de menace

<!-- markdownlint-disable MD013 -->

| Acteur / composant | Garanties TURNLOCK Core | Exécution managée | Signal / reproductibilité | Évaluation / optimisation downstream | Confiance | Disponibilité | Dernière observation | Réévalué pendant ce passage ? |
| ------------------ | ----------------------- | ----------------- | ------------------------- | ------------------------------------ | --------- | ------------- | -------------------- | ------------------------------ |
| {{display_name}} / `{{component_id}}` | {{turnlock_core_guarantees_color}} {{turnlock_core_guarantees_label}} | {{managed_execution_color}} {{managed_execution_label}} | {{run_signal_reproducibility_color}} {{run_signal_reproducibility_label}} | {{evaluation_optimization_downstream_color}} {{evaluation_optimization_downstream_label}} | {{dimension_confidences}} | {{availability}} | {{last_observed_at}} | {{revalidated_this_run}} |

<!-- markdownlint-enable MD013 -->

Afficher la couleur **et** le libellé depuis chaque `level` :

- `U` — ⚪ INDETERMINATE ;
- `L0` — 🟢 ADJACENT_OR_COMPLEMENTARY ;
- `L1` — 🟡 ISOLATED_PRIMITIVE ;
- `L2` — 🟠 SUBSTANTIAL_PARTIAL_SUBSTITUTE ;
- `L3` — 🔴 NEAR_EQUIVALENCE ;
- `L4` — 🟣 DEMONSTRATED_SCOPED_EQUIVALENCE.

Représenter tous les acteurs conservés dans le radar, y compris ceux dont les
notes sont reconduites, ceux qui sont dormants ou arrêtés par instruction, et
ceux dont l'évaluation reste indéterminée. Ne calculer aucune moyenne globale.

### Détails par acteur et composant

#### {{display_name}} — `{{actor_id}}` / `{{component_id}}`

- **rôles :** {{roles}}
- **résumé :** {{actor.summary}}
- **périmètre, justification et preuves des quatre notes :** {{rating_details}}
- **dépendances externes :** {{external_dependencies}}
- **axes T1–T10 and C1–C8 :** {{axis_assessments}}
- **dernière inspection de code :** {{monitoring.last_code_inspection_at}}
- **prochaine échéance :** {{monitoring.next_review_due_at}}
- **couverture :** {{monitoring.coverage_status}}
- **cycle de vie :** {{monitoring.actor_lifecycle}}
- **questions et investigations en attente :** {{monitoring.pending_investigations}}

## 4. Évolutions techniques et constats

{{findings}}

Chaque constat indique son identifiant stable, son acteur et composant, son
cycle de vie, ses axes, ses causes de changement et ses `evidence_ids`. Une
fermeture de constat ne retire pas l'acteur. Une correction indique clairement
ce qui était faux dans le rapport antérieur et référence le constat corrigé sous
la forme `<report_id>#<finding_id>`.

## 5. Reproductibilité, comparabilité et régressions

{{reproducibility_comparability_and_regressions}}

Présenter les profils réellement étayés, les déterminants requis pour chaque
propriété, l'éligibilité de comparaison, les inconnues, les dérives observées et
la portée de toute attribution. Ne pas confondre relecture du contrôle, nouvelle
exécution sémantique, différence de score et régression de méthode.

## 6. Évaluation, optimisation et exécution managée

{{evaluation_optimization_and_managed_execution}}

Présenter les responsabilités réellement disponibles pour l'évaluation, le
contrôle de variance, la génération ou promotion de variantes, l'isolation, la
matérialisation d'environnement, les effets et l'élasticité. Identifier les
dépendances externes et les limites du signal consommé.

## 7. Recherche de nouveaux entrants et compositions

- **statut de découverte :** {{discovery.status}}
- **recherches réellement effectuées :** {{discovery.searches}}
- **acteurs admis :** {{discovery.admitted_actor_ids}}
- **candidats en attente :** {{discovery.pending_candidates}}
- **doublons, forks, renommages et lignées :** {{discovery.duplicates_and_lineage}}
- **limites :** {{discovery.limitations}}

{{new_entrants_and_available_compositions}}

Ne présenter une composition comme disponible que lorsque ses composants et
ses frontières sont réellement accessibles et adéquats.

## 8. Trajectoires

{{trajectories}}

Dans le rapport hebdomadaire du premier lundi du mois, cette section porte la
synthèse mensuelle. Distinguer `implementation_change`, `new_evidence`,
`assessment_correction`, `turnlock_baseline_change` et `methodology_change`.
Seul `implementation_change` établit une progression technique concurrente.

## 9. Implications pour le positionnement

{{positioning_implications}}

Ces implications restent des observations de recherche. Elles ne modifient ni
le Product Intent, ni les ADRs, ni les rationales, ni le positionnement, ni les
considérations futures, ni le statut possible de Turnlock Cloud.

## 10. Couverture, retards et investigations ouvertes

{{coverage}}

- **acteurs en retard :** {{radar_continuity.overdue_actor_ids}}
- **questions ouvertes :** {{open_questions}}
- **continuité du radar :** {{radar_continuity.status}}
- **notes de réconciliation :** {{radar_continuity.reconciliation_notes}}

Un passage non réalisé reste `not_checked` ou `overdue`; ses dates et curseurs
ne sont pas avancés. Exposer les dates reconduites et définir
`revalidated_this_run` à `false` lorsqu'aucune nouvelle observation n'a eu lieu.

## 11. Sources et éléments de preuve

{{evidence}}

Pour chaque élément, afficher son identifiant, sa catégorie, son URL, les dates
d'événement/publication/observation disponibles, la révision et le chemin
éventuels, la proposition étayée, les limites et, pour `reproduced`, les détails
d'exécution. Ne pas confondre code lu, tests lus, tests exécutés et preuve
vérifiée.

## 12. Références historiques et corrections

- **rapports précédents :** {{previous_report_ids}}
- **rapports corrigés :** {{corrects}}
- **acteurs précédents :** {{radar_continuity.previous_actor_ids}}
- **nouvelles admissions :** {{radar_continuity.newly_admitted_actor_ids}}
- **radar courant :** {{radar_continuity.current_actor_ids}}
- **arrêts demandés par l'utilisateur :** {{radar_continuity.user_stopped_actor_ids}}
- **références des instructions utilisateur :** {{radar_continuity.user_instruction_refs}}

{{historical_references_and_corrections}}

La mise en forme ne remplace jamais les limites et incertitudes. Le tableau et
les détails sont rendus depuis le JSON ; ils ne sont pas édités indépendamment
pour changer une couleur ou une conclusion.
