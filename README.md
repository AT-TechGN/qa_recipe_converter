# 📋 QA Recipe Converter

> **Convertissez automatiquement vos documents Word de recette en fichiers Excel structurés.**

Application web Django permettant aux testeurs QA d'automatiser la conversion des tableaux de cas de tests (Use Cases) depuis des fichiers Word (.docx) vers des fichiers Excel (.xlsx) professionnels.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| **Upload Word** | Glisser-déposer ou sélection classique `.docx` / `.doc` |
| **Détection intelligente** | Reconnaissance automatique des colonnes (insensible à la casse, accents, variantes) |
| **Fusion de cellules** | Gestion automatique des cellules fusionnées |
| **Prévisualisation** | Tableau interactif éditable avant export |
| **Export Excel** | 2 feuilles : *Use Cases* + *Cas automatisé*, mise en forme professionnelle |
| **Recherche fichiers** | Recherche de fichiers `.docx`/`.xlsx` sur la machine locale via API |
| **Sécurité** | Fichiers supprimés automatiquement après 1 heure |

---

## 🏗️ Architecture

```
qa_recipe_converter/
├── config/                  # Configuration Django
│   ├── settings/
│   │   ├── base.py          # Paramètres communs
│   │   ├── development.py   # Dev (DEBUG=True, SQLite)
│   │   └── production.py    # Prod (sécurité renforcée)
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── core/                # App principale (modèles, vues, forms)
│   │   ├── models.py        # ConversionJob, ExtractedUseCase
│   │   ├── views.py         # Upload, Preview, Generate, Result
│   │   ├── forms.py         # Validation upload
│   │   └── admin.py
│   ├── parser/              # Moteur de parsing
│   │   ├── docx_parser.py   # Extraction Word → dict
│   │   ├── excel_generator.py # Génération Excel professionnel
│   │   └── file_searcher.py # Recherche fichiers locale
│   └── api/                 # API REST (DRF)
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── templates/
│   ├── base.html
│   └── core/
│       ├── index.html       # Page upload
│       ├── preview.html     # Prévisualisation & édition
│       └── result.html      # Téléchargement
├── tests/                   # Suite de tests (52 tests, ~76% coverage)
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── pytest.ini
```

---

## 🚀 Démarrage rapide

### Option 1 — Docker (recommandé)

```bash
# 1. Cloner le projet
git clone <repo-url>
cd qa_recipe_converter

# 2. Copier et configurer l'environnement
cp .env.example .env

# 3. Lancer avec Docker Compose
docker-compose up --build

# 4. Appliquer les migrations (premier démarrage)
docker-compose exec web python manage.py migrate

# 5. (Optionnel) Créer un super-utilisateur admin
docker-compose exec web python manage.py createsuperuser
```

L'application est disponible sur **http://localhost:8000**

---

### Option 2 — Développement local (sans Docker)

#### Prérequis
- Python 3.12+
- pip

```bash
# 1. Cloner le projet
git clone <repo-url>
cd qa_recipe_converter

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\Scripts\activate         # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer l'environnement
cp .env.example .env

# 5. Créer le dossier base de données
mkdir -p db

# 6. Appliquer les migrations
python manage.py migrate --settings=config.settings.development

# 7. Créer un superutilisateur (optionnel)
python manage.py createsuperuser --settings=config.settings.development

# 8. Lancer le serveur de développement
python manage.py runserver --settings=config.settings.development
```

L'application est disponible sur **http://127.0.0.1:8000**

---

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/

# Avec rapport de couverture
python -m pytest tests/ --cov=apps --cov-report=term-missing

# Rapport HTML de couverture
python -m pytest tests/ --cov=apps --cov-report=html
# → Ouvrir htmlcov/index.html

# Un module spécifique
python -m pytest tests/test_docx_parser.py -v
python -m pytest tests/test_excel_generator.py -v
python -m pytest tests/test_models_views.py -v
python -m pytest tests/test_file_searcher.py -v
```

**Résultats actuels :** 52 tests ✅ | Couverture métier : 88–100%

---

## 🔧 Commandes Django utiles

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Shell Django interactif
python manage.py shell

# Vider les fichiers anciens (> 1h)
python manage.py shell -c "
from apps.core.models import ConversionJob
from django.utils import timezone
from datetime import timedelta
old = ConversionJob.objects.filter(created_at__lt=timezone.now()-timedelta(hours=1))
print(f'{old.count()} tâches à supprimer')
old.delete()
"

# Vérifier la configuration
python manage.py check

# Collecter les fichiers statiques (production)
python manage.py collectstatic --noinput --settings=config.settings.production
```

---

## 🌐 API REST

| Endpoint | Méthode | Description |
|---|---|---|
| `/api/upload/` | `POST` | Upload + parsing Word |
| `/api/jobs/` | `GET` | Liste des conversions |
| `/api/jobs/<uuid>/` | `GET` | Détail d'une conversion |
| `/api/jobs/<uuid>/generate/` | `GET` | Télécharger l'Excel |
| `/api/jobs/<uuid>/use-cases/<uuid>/` | `PATCH` | Modifier un Use Case |
| `/api/files/search/?q=<query>` | `GET` | Recherche fichiers locale |

### Exemple d'upload via curl

```bash
curl -X POST http://localhost:8000/api/upload/ \
  -F "word_file=@/chemin/vers/recette.docx"
```

---

## 📋 Modèles de données

### ConversionJob
| Champ | Type | Description |
|---|---|---|
| `id` | UUID | Identifiant unique |
| `status` | Enum | PENDING / PROCESSING / DONE / ERROR |
| `source_filename` | str | Nom du fichier Word source |
| `word_file` | FileField | Fichier Word uploadé |
| `result_file` | FileField | Fichier Excel généré |
| `use_cases_count` | int | Nombre de UC extraits |
| `error_message` | text | Message d'erreur éventuel |

### ExtractedUseCase
| Champ | Type | Description |
|---|---|---|
| `id` | UUID | Identifiant unique |
| `job` | FK | Lien vers la tâche de conversion |
| `order` | int | Ordre d'apparition |
| `use_case_id` | str | Identifiant UC (ex: UC001) |
| `description` | text | Description du cas |
| `preconditions` | text | Prérequis |
| `steps` | text | Étapes / Actions |
| `expected_results` | text | Résultats attendus |
| `observed_results` | text | Résultats observés |
| `is_automated` | bool | Marqué comme automatisé |
| `status` | Enum | À tester / En cours / Passé / Échoué / Bloqué |

---

## ⚙️ Configuration (.env)

```env
SECRET_KEY=votre-secret-key-unique
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.development
MAX_UPLOAD_SIZE_MB=50
FILE_RETENTION_HOURS=1
```

---

## 📦 Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Backend | Python / Django | 5.0.x |
| BDD | SQLite | — |
| Parsing Word | python-docx | 1.1.x |
| Génération Excel | openpyxl | 3.1.x |
| API REST | Django REST Framework | 3.15.x |
| Tests | pytest-django + coverage | — |
| Serveur prod | gunicorn + whitenoise | — |
| Conteneurisation | Docker + docker-compose | — |

---

## 🔒 Sécurité

- Les fichiers uploadés sont supprimés après **1 heure** (configurable via `FILE_RETENTION_HOURS`)
- Validation stricte des extensions et de la taille (max 50 MB)
- Protection CSRF sur tous les formulaires
- En production : HTTPS recommandé, `DEBUG=False`, `SECRET_KEY` sécurisée

---

## 👤 Auteur

**Alseny Traoré** — Mai 2026  
QA Recipe Converter v1.0
