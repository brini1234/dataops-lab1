# TP 1 - D'un script fragile à un pipeline testé

**Auteur :** Chaima Brini - ING5-DS-B

---

## Étape 0 - Créer le projet

**Q1. Pourquoi écrit-on les bibliothèques dans requirements.txt au lieu de taper simplement `pip install pandas` ?**

Le fichier `requirements.txt` garde une trace écrite de toutes les bibliothèques dont le projet a besoin, avec leurs versions minimales. Avec une seule commande (`pip install -r requirements.txt`), n'importe qui peut recréer le même environnement sur une autre machine, ou moi-même plus tard. C'est la reproductibilité. Si on tape `pip install pandas` à la main, rien n'est enregistré : on risque d'oublier une bibliothèque ou d'installer une autre version, et le projet peut alors se comporter différemment.

---

## Étape 1 - Les données et l'ancien script

**Q2. La boutique vend dans cinq pays. Combien de lignes le rapport affiche-t-il ? Pourquoi ?**

Le rapport de l'ancien script affiche **8 lignes** au lieu de 5. Un même pays apparaît sous plusieurs écritures : `Tunisia`, `tunisia` et ` Tunisia` (avec un espace devant) pour la Tunisie, `Morocco` et `MOROCCO` pour le Maroc. Le script compare les textes exactement, donc il les traite comme des pays différents et répartit le chiffre d'affaires entre eux.

**Q3. Au moins cinq sortes de problèmes différentes dans le fichier.**

| order_id | Problème | Dimension de qualité |
|---|---|---|
| 1008 | `customer_id` vide | Complétude |
| 1010 | la commande apparaît deux fois (lignes identiques) | Unicité |
| 1013 | date `2026-13-45` impossible (mois 13, jour 45) | Validité |
| 1004 | quantité négative (-2) | Validité |
| 1006, 1016, 1023 | pays écrits différemment : `tunisia`, `MOROCCO`, ` Tunisia` | Cohérence |
| 1019 | clavier à 4500 au lieu de 45, prix qui ne correspond pas à la réalité | Exactitude |

**Q4. Le total est-il trop haut ou trop bas ? Peut-on le savoir sans recalculer à la main ?**

Le total de 12771.10 est **trop haut**. Les erreurs qui ajoutent beaucoup de chiffre d'affaires en trop sont le prix de 4500 (commande 1019) et le doublon (commande 1010, 449). Une seule erreur le fait baisser, la quantité négative de la commande 1004 (-39.80), et elle est très petite. On peut donc le savoir sans tout recalculer : il suffit de regarder quelles erreurs augmentent le total et lesquelles le diminuent, et de voir que les premières sont bien plus grosses. Le calcul exact le confirme : le bon total est 7655.90.

---

## Étape 2 - Construire le pipeline

**Q5. Qu'a-t-on gagné en découpant le script en fonctions ? Deux avantages.**

1. Chaque fonction peut être testée séparément avec pytest, sur un petit tableau écrit à la main.
2. Quand il y a un problème, on sait dans quelle étape il se trouve (extraction, schéma, nettoyage, contrôle qualité, transformation). Il est aussi plus facile de modifier ou de réutiliser une étape sans toucher aux autres.

---

## Étape 3 - Ajouter les contrôles de données

**Q6. Quel est le bon total ? De combien l'ancien script se trompait-il ?**

Le bon total est **7655.90**. L'ancien script affichait 12771.10, soit 5115.20 de trop. L'erreur représente environ **67 %** du bon total (5115.20 / 7655.90 ≈ 0.67) : l'ancien script annonçait un chiffre d'affaires environ 1,67 fois trop grand.

**Q7. Quelle commande a causé l'essentiel de l'erreur ? Quelle règle l'a attrapée ?**

C'est la commande **1019** : un clavier vendu 4500 au lieu de 45, ce qui ajoute 4500 au total, soit environ 88 % de l'écart. Elle a été attrapée par la **règle 4** (prix présent, positif et au plus 1000), avec le motif `invalid_unit_price`. Le doublon de la commande 1010 (449), attrapé par la règle 5, explique une bonne partie du reste.

**Q8. Pourquoi enregistre-t-on les lignes rejetées dans un fichier au lieu de simplement les supprimer ?**

Le fichier de quarantaine (`data/rejected/rejected_orders.csv`) garde chaque ligne rejetée avec son motif. Cela permet de comprendre ce qui s'est mal passé, de corriger le problème à la source, de récupérer des commandes qui étaient peut-être réelles, et de garder une trace en cas de question du directeur commercial. Supprimer les lignes ferait perdre cette information, et personne ne saurait que des données ont été écartées.

---

## Étape 4 - Écrire des tests unitaires

**Q9. Que s'est-il passé quand vous avez cassé la règle 3 ? Quel test a échoué ?**

J'ai remplacé `> 0` par `> -5` dans la règle 3. La quantité -2 n'était alors plus considérée comme invalide. Le test **`test_negative_quantity_is_rejected`** a échoué : pytest affichait `1 failed, 4 passed` et `assert [1, 2] == [2]`. La commande 1 (quantité -2) restait dans les lignes propres alors qu'elle aurait dû être rejetée. Les quatre autres tests passaient toujours. Après avoir remis `> 0`, les 5 tests sont de nouveau passés. Cela montre que les tests détectent une erreur de logique dans le code.

**Q10. Que vérifie un test unitaire ? Que vérifie un contrôle de données ?**

Un test unitaire vérifie que mon code est juste, en l'exécutant sur un petit tableau écrit à la main dont je connais déjà la bonne réponse. Un contrôle de données vérifie que les vraies données du jour sont acceptables, à chaque exécution du pipeline.

---

## Étape 6 - Les jours 2 et 3 arrivent

**Q11. Tableau comparatif.**

|  | Ancien script | Votre pipeline |
|---|---|---|
| Jour 2 : message d'erreur ? | Non, aucune erreur ni avertissement | Oui : `PIPELINE STOPPED: Reject rate 100% is above the limit of 20% (6 rejected rows out of 6)`, code de sortie 1 |
| Jour 2 : total affiché | 270200 | Aucun total : `Nothing was published.` |
| Jour 3 : message d'erreur ? | Oui, mais brutal : `KeyError: 'unit_price'` (le programme plante) | Oui : `PIPELINE STOPPED: Missing columns: ['unit_price']`, code de sortie 1 |

Dans les deux cas, le fichier `data/output/revenue_by_country.csv` contient toujours le rapport du jour 1 (France 1188.5, Germany 407.5, Italy 2920.9, Morocco 2035.5, Tunisia 1103.5) : rien de faux n'a été publié.

**Q12. Qu'est-ce qui a changé dans le système source au jour 2 ? Au jour 3 ?**

- **Jour 2 :** les prix sont multipliés par 100 par rapport au jour 1 (par exemple 44900 au lieu de 449 pour une chaise de bureau, 3900 au lieu de 39 pour une webcam), comme si le système source avait commencé à envoyer les prix en centimes. Le schéma est le même, mais les valeurs ont changé.
- **Jour 3 :** la colonne `unit_price` a été renommée `price`. Le schéma du fichier a changé, alors que les valeurs sont normales.

**Q13. Sans pipeline, quel jour est le plus dangereux pour l'entreprise ?**

Le **jour 2** est le plus dangereux. L'ancien script ne plante pas, ne prévient personne et affiche un total de 270200, environ 100 fois trop grand. Le directeur commercial pourrait prendre ce chiffre pour vrai et prendre de mauvaises décisions. Au jour 3, l'ancien script plante avec une erreur visible : tout le monde voit qu'il y a un problème et personne n'utilise de chiffre faux. Le pire cas est l'erreur silencieuse.

**Q14. Le code de sortie vaut 1 quand le pipeline s'arrête. Qui ou quoi peut utiliser ce nombre ?**

Tout programme qui lance le pipeline peut lire ce code : un planificateur de tâches (par exemple cron ou un orchestrateur), qui peut ne pas lancer l'étape suivante ; un outil de monitoring ou d'alerte, qui peut envoyer un mail ou un message à l'équipe ; un outil d'intégration continue (CI), qui marque l'exécution comme échouée ; ou un autre script qui enchaîne plusieurs traitements. Un humain qui lit seulement l'écran peut manquer le message, alors qu'une machine lit toujours le code 0 (succès) ou 1 (arrêt).
