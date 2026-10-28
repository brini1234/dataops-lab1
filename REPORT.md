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


---

# TP 2 - Versionner le code avec Git, les données avec DVC

## TP2

## Étape 1 - Une règle sur une branche

**Q1.** Non, pendant que je travaillais sur la branche `feature/country-rule`, `main` ne contenait pas la règle 6. Elle est apparue sur `main` avec la commande `git merge --no-ff feature/country-rule` (commit de fusion `3237502`). C'est utile si le rapport tourne chaque nuit depuis `main` : du code à moitié fini ne peut pas casser le rapport, seul du code testé arrive sur `main`.

**Q2.** Une pull request permet à un collègue de relire et commenter le changement avant la fusion, de lancer automatiquement les tests (CI), et de garder une trace de la discussion et de l'approbation. Un `git merge` local ne fait rien de tout cela.

## Étape 2 - Mettre les données sous DVC

**Q3.** La ligne est `md5: 2b3c1607110c06fe4619ef560c7a6356.dir`. Elle identifie le contenu exact du dossier `data/raw`. Si je changeais un seul caractère dans un des CSV, l'empreinte changerait.

**Q4.** C'est le fichier `data/.gitignore`, qui contient `/raw`.

## Étape 3 - Un remote DVC

**Q5.** Les fichiers de `dvc-storage` sont nommés par leur empreinte md5 (par exemple dans les dossiers `1d`, `2b`, `3f`, `9f`) et non par `orders_day1.csv`. Deux versions différentes d'un même fichier ont des empreintes différentes, donc elles ne s'écrasent pas et on peut garder toutes les versions.

## Étape 4 - Une nouvelle version des données

**Q6.** Le fichier `.dvc` ne contient que l'empreinte et la taille des données : quand les données changent, seules ces deux lignes changent (md5 `2b3c1607...` devenu `94103799...`, taille 2115 devenue 2344). Cela suffit à Git. Il faut quand même commiter ce pointeur, parce que c'est ce commit qui lie une version du code à une version précise des données.

**Q7.** Non, le code n'a pas changé entre `data-v1` et `data-v2`, seules les données ont changé. Le total est passé de 7655.90 (`data-v1`) à 8835.40 (`data-v2`).

## Étape 5 - Revenir aux anciennes données

**Q8.** `git checkout data-v1 -- data/raw.dvc` a remis l'ancien pointeur (l'ancienne empreinte), mais pas les CSV. `dvc checkout` a ensuite remplacé les CSV pour qu'ils correspondent à ce pointeur.

**Q9.** Si j'oublie `dvc checkout`, les CSV restent dans la version précédente alors que le pointeur indique l'autre version. Je l'ai vu : avec le pointeur `data-v1` mais sans `dvc checkout`, le pipeline affichait encore 35 lignes et `TOTAL: 8835.40`. C'est dangereux pour un rapport, car aucune erreur n'apparaît et on croit avoir reconstruit l'ancien rapport alors qu'on a produit le nouveau.

## Étape 6 - Un collègue récupère tout

**Q10.** `git clone` a donné au collègue le code, les tests, les pointeurs `.dvc` et la configuration du remote, mais pas les CSV. `dvc pull` lui a donné les vrais CSV, téléchargés depuis `dvc-storage` (4 files fetched, 3 files added).

**Q11.** Sans `dvc push` à l'étape 4, les fichiers de `data-v2` ne seraient pas dans le remote. Le collègue ne pourrait pas récupérer les bonnes données avec `dvc pull`, donc il n'obtiendrait pas le total 8835.40.

**Q12.** Le TP a réduit trois des quatre douleurs :
- « Ça marche sur ma machine » : `git clone` + `dvc pull` redonnent le même code, les mêmes données et le même total 8835.40 (étape 6).
- Erreurs silencieuses : on peut expliquer pourquoi le chiffre est passé de 7655.90 à 8835.40 et revoir l'ancien rapport (étapes 4 et 5).
- Étapes manuelles : `dvc push` et `dvc pull` remplacent l'échange de fichiers à la main (étapes 3 et 6).

## Historique Git

```
* 1bff7d9 (HEAD -> main, tag: data-v2) Data v2: late orders for 2026-10-05
* ac69513 Add the DVC remote
* 47dd09b (tag: data-v1) Track raw data with DVC
*   3237502 Merge the country rule
|\
| * b54abda (feature/country-rule) Reject orders from countries the shop does not sell to
|/
* 12d0552 Finish TP1, add DVC to requirements
* c400ec8 (origin/main) Add CI workflow
* 6a34da0 Add REPORT.md
* 7bd446e Add day 2 and day 3 files
* 122e846 Add pipeline, data checks and unit tests
* a0716d3 Empty project with requirements
```