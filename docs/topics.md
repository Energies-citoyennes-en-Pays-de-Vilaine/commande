# Sujets des composants

## Écran M5Stack avec OpenHASP

Sujet racine : `hasp/g<id>/`

### Pages & boutons

| N° page | Titre | Donnée | Sujet bouton |
| --- | --- | --- | --- |
| 1 | Météo | | |
| 2 | Heures confort semaine | heure de début période 1 | `state/p2b5` |
| | | minute de début période 1 | `state/p2b6` |
| | | heure de fin période 1 | `state/p2b8` |
| | | minute de fin période 1 | `state/p2b9` |
| | | heure de début période 2 | `state/p2b25` |
| | | minute de début période 2 | `state/p2b26` |
| | | heure de fin période 2 | `state/p2b28` |
| | | minute de fin période 2 | `state/p2b29` |
| | | Valider | `state/p2b3` |
| 3 | Heures confort WE | heure de début période 1 | `state/p3b5` |
| | | minute de début période 1 | `state/p3b6` |
| | | heure de fin période 1 | `state/p3b8` |
| | | minute de fin période 1 | `state/p3b9` |
| | | heure de début période 2 | `state/p3b25` |
| | | minute de début période 2 | `state/p3b26` |
| | | heure de fin période 2 | `state/p3b28` |
| | | minute de fin période 2 | `state/p3b29` |
| | | Valider | `state/p3b3` |
| 4 | H. creuses semaine | heure de début période 1 | `state/p4b5` |
| | | minute de début période 1 | `state/p4b6` |
| | | heure de fin période 1 | `state/p4b8` |
| | | minute de fin période 1 | `state/p4b9` |
| | | heure de début période 2 | `state/p4b25` |
| | | minute de début période 2 | `state/p4b26` |
| | | heure de fin période 2 | `state/p4b28` |
| | | minute de fin période 2 | `state/p4b29` |
| | | Valider | `state/p4b3` |
| 5 | H. creuses WE | heure de début période 1 | `state/p5b5` |
| | | minute de début période 1 | `state/p5b6` |
| | | heure de fin période 1 | `state/p5b8` |
| | | minute de fin période 1 | `state/p5b9` |
| | | heure de début période 2 | `state/p5b25` |
| | | minute de début période 2 | `state/p5b26` |
| | | heure de fin période 2 | `state/p5b28` |
| | | minute de fin période 2 | `state/p5b29` |
| | | Valider | `state/p5b3` |
| 6 | Voiture | heure de fin | `state/p6b5` |
| | | minute de fin | `state/p6b6` |
| | | charge restante | `state/p6b8` |
| | | Prêt | `state/p6b3` |

### Commande

Sujet : `command/jsonl`


## Nous A1T Tasmota

|  | Sujet |
| --- | --- |
| Last Will and Testament | `tele/A<id>/LWT` |
|  | `tele/A<id>/STATE` |
|  | `tele/A<id>/SENSOR` |

## Cofybox

Les sujets qui concernent la Cofybox ont le préfixe `cofybox/cb<id>`.

Par exemple, une prise Nous A1T Tasmota sera sous `cofybox/cb<id>/tele/A<id>/#`
