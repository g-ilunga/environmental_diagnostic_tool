# Outil de diagnostic des enjeux environnementaux
## <ins>Problématique</ins>
Dans le cadre d’un projet ou par curiosité personnelle, on peut être amené à se poser la question sur les enjeux environnementaux auquel un périmètre ou une emprise est soumise. Aujourd’hui grâce au travail de l’IGN Géoservices, on peut facilement avoir accès aux données environnementales. Cependant, cela demande généralement de parcourir les différents portails (selon les besoins) à savoir geoportail, geoportail de l’urbanisme, atlas des patrimoines, etc. Dans certains cas, tout ce qu’on veut est d’avoir un aperçu rapide ou réaliser un premier diagnostic.
Par ailleurs, bien qu’intuitive, certains de ces portails ne permettent pas de par exemple importer une couche shapefile pour déterminer les enjeux environnementaux auxquels est soumis l’air d’étude. 
## <ins>Ce que propose l’outil de diagnostic</ins>
L’objectif de cet outil est de proposer une première solution à la problématique élaborée ci-dessus.  L’IGN a développé des API pour permettre aux utilisateurs avertis de pouvoir se connecter à leur base des données et réaliser des manipulations avancées. Ainsi, le présent outil exploite les API développées par l’IGN. 

Dans un premier temps, c’est le flux WFS qui est exploité pour la construction de l’outil.

Grace au présent outil, il vous suffit d’importer l’emprise de votre aire d’étude et il vous donne la liste des enjeux environnementaux qui concernent votre aire d’étude. A ce jour l’outil permet de déterminer si vous êtes concerné par les périmètres suivants :
* ZNIEFF
* Sites Natura 2000
* Parcs Naturels Régionaux
* Parcs Naturels Marins
* Parcs Nationaux
* Servitudes (sites inscrits/classés, monuments historiques, etc.)
* L’outil vous permet aussi de déterminer les zones urbaines du PLU/PLUi que votre aire d’étude intercepte.
## <ins>Limites de l’outil</ins>
A ce jour, l’outil présente quelques limites :
* L’outil ne prend en compte que les fichiers au format shapefile.
* L’outil ne génère que du texte comme résultat. Il ne permet pas encore d’avoir une visualisation sous forme de carte.
* L’outil n’indique pas quels sont les emplacements réservés interceptés au titre du PLU/PLUi.
Progressivement ces limites seront resolus.
## <ins>Future développement</ins>
Aujourd’hui l’outil est encore un script. La future étape sera principalement le déploiement avec une interface graphique.

Une documentation plus détaillée sur les étapes du développement sera publiée ulterieurement.

## <ins>Développement technique de l'outil</ins>
- **Langage :** Python 3.10  
- **Structure modulaire :** plusieurs scripts, chacun avec une fonctionnalité spécifique.

| Fichiers                  | Description                                  |
|-----------------------------------|----------------------------------------------|
| **config_dataset.json**            | Liste des données environnementales et leurs paramètres |
| **config_urls.json**               | URLs utilisées par l’outil                    |
| **xml_builder.py**                 | Construction des requêtes de recherche        |
| **main.py**                        | Script principal (point d’entrée de l’outil). C'est ce script qui est utilisé pour lancer l'outil  |
| **requirements.txt**               | Liste des dépendances Python                   |
