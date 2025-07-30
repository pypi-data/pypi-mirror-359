# Seuils (de l'usure)
[![](https://img.shields.io/pypi/v/seuils)](https://pypi.org/project/seuils/)
[![](https://img.shields.io/pypi/dm/seuils)](https://pypi.org/project/seuils/)
[![](https://gitlab.com/outils-jcp/seuils-usure/badges/main/pipeline.svg)](https://gitlab.com/outils-jcp/seuils-usure/-/pipelines)


Répertoire des seuils de l'usure applicables aux crédits à la consommation en France depuis 2005.

Le taux d'usure correspond au taux d'intérêt maximum légal que les établissements de crédit sont autorisés à pratiquer lorsqu'ils accordent un prêt. Le taux d'usure vise à protéger les emprunteurs. La Banque de France est en charge du calcul trimestriel du taux d'usure dont les modalités de calcul sont définies dans les différents textes juridiques de la législation française.

Installation
---

```bash
python3 -m pip install seuils
```

Utilisation
---

```python
>>> from seuils import usure

>>> usure.get_lien(jour="2024-01-01")
'https://www.legifrance.gouv.fr/download/file/TngutXAISa4GeWXvS4DQMQ8m5kM-HkKzkIVCl8TVyds=/JOE_TEXTE'
# Retourne le lien legifrance de l'avis ministériel détaillant les seuils de l'usure en vigueur pour le 1er trimestre 2024

>>> usure.get_taux(jour="2024-01-01", montant=3000)
Decimal('22.00')
# Retourne le seuil de l'usure applicable au 1er trimestre 2024 pour un crédit à la consommation d'un montant de 3000 euros
```

Mise à jour
---

1. Ajouter les nouvelles données dans les fichiers suivants :
```
public/avis.json
public/seuils.json
src/seuils/data/avis.json
src/seuils/data/seuils/json
```

2. Ajouter le pdf du journal officiel dans le dossier `public/assets/pdf` et dans le dossier `src/seuils/pdf`

3. Lancer les tests
```bash
pytest
```

4. Mettre à jour le numéro de version dans le fichier `pyproject.toml` (format : annee.trimestre.version)