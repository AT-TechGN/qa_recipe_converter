# 🧪 QA Recipe Converter v2.0

> **Convertissez automatiquement vos documents Word de recette en fichiers Excel structurés, scripts Gherkin et projets Cypress.**

Application web Django permettant aux testeurs QA d'automatiser la conversion des cas de tests depuis des fichiers Word (.docx) vers des fichiers Excel professionnels, et de générer des scripts d'automatisation Cypress/Gherkin en un clic.

---

## ✨ Fonctionnalités

| Fonctionnalité | Description | Version |
|---|---|---|
| **Upload Word** | Glisser-déposer ou sélection `.docx` / `.doc` | v1.0 |
| **Détection intelligente** | Reconnaissance automatique des colonnes | v1.0 |
| **Fusion de cellules** | Gestion automatique des cellules fusionnées | v1.0 |
| **Prévisualisation éditable** | Tableau interactif éditable avant export | v1.0 |
| **Export Excel** | 2 feuilles : *Use Cases* + *Cas automatisé* | v1.0 |
| **Recherche fichiers** | Recherche `.docx`/`.xlsx` sur la machine locale | v1.0 |
| **Scripts Gherkin** 🆕 | Génération `.feature` BDD/Cucumber par UC automatisable | v2.0 |
| **Projet Cypress** 🆕 | Projet Cypress complet avec step definitions | v2.0 |
| **Ouvrir VS Code** 🆕 | Ouvre le projet Cypress dans VS Code | v2.0 |
| **UI redesignée** 🆕 | Interface professionnelle Inter + JetBrains Mono | v2.0 |
| **Sécurité** | Fichiers supprimés automatiquement après 1 heure | v1.0 |

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
│   │   ├── views.py         # Upload, Preview, Generate, Gherkin, VSCode, Result
│   │   ├── forms.py         # Validation upload
│   │   └── urls.py          # Routes
│   ├── parser/              # Moteur de parsing & génération
│   │   ├── docx_parser.py        # Extraction Word → dict
│   │   ├── excel_generator.py    # Génération Excel professionnel
│   │   ├── gherkin_generator.py  # 🆕 Génération Gherkin + Cypress
│   │   └── file_searcher.py      # Recherche fichiers locale
│   └── api/                 # API REST (DRF)
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── templates/
│   ├── base.html            # 🆕 Design system complet (Inter, JetBrains Mono)
│   └── core/
│       ├── index.html       # 🆕 Page upload redesignée
│       ├── preview.html     # 🆕 Prévisualisation + panel export Gherkin/Cypress
│       └── result.html      # 🆕 Page résultat avec tous les exports
├── tests/                   # Suite de tests
├── manage.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🔄 Pipeline de conversion

```
Word (.docx)
    │
    ▼
┌─────────────────────┐
│   DocxParser        │  → Extraction des tableaux UC
│   (python-docx)     │
└─────────────────────┘
    │
    ▼
┌─────────────────────┐
│   Preview éditable  │  → Interface web éditable
│   (Django views)    │  → Marquage des cas automatisables
└─────────────────────┘
    │
    ├──────────────────────────────────────────┐
    ▼                                          ▼
┌─────────────────────┐          ┌─────────────────────────────┐
│   ExcelGenerator    │          │    GherkinGenerator (NEW)   │
│   (openpyxl)        │          │    - .feature files (BDD)   │
│   → .xlsx           │          │    - Projet Cypress (.zip)  │
└─────────────────────┘          │    - Step definitions .js   │
                                 └─────────────────────────────┘
                                              │
                                              ▼
                                 ┌─────────────────────────────┐
                                 │    VS Code (optionnel)      │
                                 │    - Ouverture automatique  │
                                 │    - `code /projet/path`    │
                                 └─────────────────────────────┘
```

---

## 🚀 Démarrage rapide

### Option 1 — Docker (recommandé)

```bash
git clone https://github.com/AT-TechGN/qa_recipe_converter.git
cd qa_recipe_converter
cp .env.example .env
docker-compose up --build
docker-compose exec web python manage.py migrate
```

L'application est disponible sur **http://localhost:8000**

### Option 2 — Développement local

```bash
git clone https://github.com/AT-TechGN/qa_recipe_converter.git
cd qa_recipe_converter
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# .venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env
mkdir -p db
python manage.py migrate --settings=config.settings.development
python manage.py runserver --settings=config.settings.development
```

---

## 🌲 Utilisation des nouvelles fonctionnalités

### 1. Génération Gherkin

Après l'upload et la prévisualisation :
1. Dans la colonne **Auto.**, activez le toggle pour chaque cas automatisable
2. Cliquez sur **💾 Sauvegarder**
3. Dans le panneau d'export, cliquez sur **📝 Scripts Gherkin** pour télécharger un ZIP de fichiers `.feature`

Exemple de fichier généré :

```gherkin
# Fichier généré automatiquement par QA Recipe Converter
# Use Case : UC001

Feature: UC001 — Connexion utilisateur

  Background:
    Given L'utilisateur est sur la page de connexion

  Scenario: Connexion utilisateur

    When L'utilisateur saisit son email et son mot de passe
    And L'utilisateur clique sur le bouton "Se connecter"
    Then L'utilisateur est redirigé vers le tableau de bord
    And Un message de bienvenue est affiché
```

### 2. Projet Cypress

Cliquez sur **🌲 Projet Cypress** pour télécharger un projet Cypress complet prêt à démarrer :

```bash
# Après extraction du ZIP :
cd cypress_project/
npm install
npm run cy:open   # Mode interactif
npm run cy:run    # Mode headless
```

Structure du projet généré :
```
cypress/
├── e2e/
│   ├── uc001_connexion.feature         # Scénario Gherkin
│   └── step_definitions/
│       └── uc001_connexion.js          # Steps à implémenter
├── fixtures/
└── support/
cypress.config.js
package.json
```

### 3. Ouvrir dans VS Code

Cliquez sur **🖥️ Ouvrir VS Code** : le projet Cypress est extrait dans un dossier temporaire et VS Code s'ouvre automatiquement (si installé avec la commande `code` dans le PATH).

---

## 🧪 Tests

```bash
# Lancer tous les tests
python -m pytest tests/

# Avec couverture
python -m pytest tests/ --cov=apps --cov-report=term-missing

# Module spécifique
python -m pytest tests/test_docx_parser.py -v
```

**Résultats :** 52 tests ✅ | Couverture métier : 88–100%

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

---

## 📦 Stack technique

| Composant | Technologie | Version |
|---|---|---|
| Backend | Python / Django | 5.0.x |
| BDD | SQLite | — |
| Parsing Word | python-docx | 1.1.x |
| Génération Excel | openpyxl | 3.1.x |
| Génération Gherkin | Built-in | v2.0 |
| Tests E2E | Cypress + Cucumber | 13.x |
| API REST | Django REST Framework | 3.15.x |
| Tests | pytest-django + coverage | — |
| Serveur prod | gunicorn + whitenoise | — |
| Conteneurisation | Docker + docker-compose | — |
| UI | Inter + JetBrains Mono | v2.0 |

---

## 👤 Auteur

**Alseny Traoré** — Mai 2026  
QA Recipe Converter v2.0 — AT-TechGN
