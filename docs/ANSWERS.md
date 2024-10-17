# Réponses du test

## _Utilisation de la solution (étape 1 à 3)_

Pour lancer le pipeline de collecte de données:
- créer un environnement virtuel et l'activer 
- installer les packages nécessaires via la commande `pip install -r requirements.txt`
- dans un terminal où l'environnement virtuel est activé, se déplacer dans le dossier `src/moovitamix_fastapi` et lancer le serveur pour l'API via la commande `python -m uvicorn main:app`
- dans un autre terminal où l'environnement virtuel est activé, se déplacer dans le dossier `src` et lancer le script pour la collecte des données de l'API via la commande `python -m data_pipeline` 

Une fois le script exécuté, la base de données sqlite devrait apparaitre dans le dossier src: `music_database.db`. Vous pouvez explorer les valeurs collectées avec la méthode de votre choix.  

## Questions (étapes 4 à 7)

### Étape 4

#### Schéma de Base de Données

##### Table: USERS
| Colonne         | Type     | Contraintes       |
|-----------------|----------|-------------------|
| id              | Integer  | Primary Key       |
| first_name      | String   |                   |
| last_name       | String   |                   |
| email           | String   | Unique            |
| gender          | String   |                   |
| favorite_genres | String   |                   |
| created_at      | DateTime | Default: utcnow   |
| updated_at      | DateTime | Default: utcnow   |

##### Table: TRACKS
| Colonne     | Type     | Contraintes       |
|-------------|----------|-------------------|
| id          | Integer  | Primary Key       |
| name        | String   |                   |
| artist      | String   |                   |
| songwriters | String   |                   |
| duration    | String   |                   |
| genres      | String   |                   |
| album       | String   |                   |
| created_at  | DateTime | Default: utcnow   |
| updated_at  | DateTime | Default: utcnow   |

##### Table: LISTEN_HISTORY
| Colonne     | Type     | Contraintes                 |
|-------------|----------|-----------------------------|
| id          | Integer  | Primary Key                 |
| user_id     | Integer  | Foreign Key (USERS.id)      |
| created_at  | DateTime | Default: utcnow             |
| updated_at  | DateTime | Default: utcnow             |

##### Table: LISTEN_HISTORY_TRACKS (Table de jointure)
| Colonne           | Type    | Contraintes                        |
|-------------------|---------|-------------------------------------|
| listen_history_id | Integer | Foreign Key (LISTEN_HISTORY.id)     |
| track_id          | Integer | Foreign Key (TRACKS.id)             |

##### Relations
- USERS (1) ---> (0..n) LISTEN_HISTORY
- TRACKS (0..n) <---> (0..n) LISTEN_HISTORY (via LISTEN_HISTORY_TRACKS)


##### Systeme de données recommandé: PGSQL
- Système de gestion de base de données relationnelle structurée performant et scalable
- Permet de gérer les relations many-to-many et one-to-many 
- Open source & utilisation classique 


### Étape 5

Pour suivre la santé du pipeline de données dans son execution, nous pourrions logger et collecter des métriques telles que:
- occurence d'erreurs lors d'une étape du pipeline 
- temps d'exécution des étapes du pipeline 
- volume de données traité 

Nous aurions des informations sur l'execution du pipeline dans les logs.

Nous pourrions aussi utiliser ces différentes métriques pour créer un dashboard de suivi, créer des alertes quand un problème est détecté dans le pipeline.

### Étape 6

Pour automatiser le calcul des recommandations, il faudrait utiliser un orchestrateur (comme Airflow par exemple) qui pourrait automatiser le déclanchement de plusieurs scripts. Soit en se basant sur la réalisation avec succès d'une précédente étape, soit en se basant sur la date (scheduled job). Ces tâches pourraient être les suivantes: 
- Calcul régulier des features selon les données d'écoute puis stockage de ces features dans un feature store ou dans une base de donnée. 
- Génération de recommandation: chargement du modèle (depuis une plateforme ML ou un simple blob storage) et des dernières features calculées pour calculer les recommandations à l'aide de modèle. 
- Stockage des recommandations dans une base de données afin de pouvoir les exposer à l'aide d'une API.

Note: la collecte de log et de métrique aiderait à veiller à la bonne santée du pipeline. 

### Étape 7

Pour automatiser le réentrainement du modèle de recommandation, nous aurions aussi besoin d'un orchestrateur ou d'une plateforme ML pour déclancher les différentes tâches nécessaires pour le réentrainement: 
1. Préparation des données & génération des features qui seront stockées. Cette étape pourrait être déclanchée juste avant le réentrainement.
2. Entrainement du modèle avec les dernières features calculées puis stockage versionné de celui-ci. Cet entrainement pourrait être déclanché automatiquement, soit périodiquement, soit à la dégration des performances du modèle en production.
3. Pour choisir si le modèle doit être utilisé en production, des tests automatisés serviraient à le comparer à l'ancien modèle et le déployer de manière automatique si il est jugé meilleur par les différentes métriques. 
4. Il sera nécessaire de monitorer les performances du modèle en production et veiller à sa non-dégradation (par exemple via des métriques comme le nombre de click de l'utilisateur sur les titres recommandés) -> sinon déclanchement d'un nouveau pipeline d'entrainement / test / deploiement. 
