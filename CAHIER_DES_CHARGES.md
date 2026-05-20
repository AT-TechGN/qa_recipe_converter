# 📋 Cahier des Charges — QA Recipe Converter v2.0

**Projet :** QA Recipe Converter  
**Version :** 2.0  
**Date :** Mai 2026  
**Auteur :** Alseny Traoré — AT-TechGN  
**Statut :** ✅ Implémenté

---

## 1. Contexte et objectifs

### 1.1 Contexte

Les équipes QA produisent des **recettes de tests** sous forme de documents Word (.docx) contenant des tableaux de cas de tests (Use Cases). Le transfert manuel de ces données vers des outils de test automatisé (Excel, Jira, frameworks BDD) est long, fastidieux et source d'erreurs.

### 1.2 Objectifs généraux

- Automatiser la conversion Word → Excel structuré
- Générer automatiquement des scripts d'automatisation (Gherkin/BDD)
- Réduire le temps de mise en place des suites de tests automatisés
- Offrir une expérience utilisateur professionnelle et intuitive

---

## 2. Périmètre fonctionnel

### 2.1 Fonctionnalités v1.0 (existantes)

| ID | Fonctionnalité | Priorité | Statut |
|----|---------------|----------|--------|
| F01 | Upload fichier Word (.docx/.doc) | 🔴 Critique | ✅ |
| F02 | Extraction automatique des tableaux UC | 🔴 Critique | ✅ |
| F03 | Détection intelligente des colonnes | 🔴 Critique | ✅ |
| F04 | Gestion des cellules fusionnées | 🟡 Important | ✅ |
| F05 | Prévisualisation éditable | 🔴 Critique | ✅ |
| F06 | Export Excel (2 feuilles) | 🔴 Critique | ✅ |
| F07 | Template Excel personnalisé | 🟢 Optionnel | ✅ |
| F08 | Recherche fichiers locale | 🟢 Optionnel | ✅ |
| F09 | API REST complète | 🟡 Important | ✅ |
| F10 | Suppression auto des fichiers (1h) | 🟡 Important | ✅ |

### 2.2 Nouvelles fonctionnalités v2.0 🆕

| ID | Fonctionnalité | Priorité | Statut |
|----|---------------|----------|--------|
| F11 | **Génération scripts Gherkin** | 🔴 Critique | ✅ |
| F12 | **Génération projet Cypress complet** | 🔴 Critique | ✅ |
| F13 | **Ouverture dans VS Code** | 🟡 Important | ✅ |
| F14 | **Refonte UI (design système)** | 🟡 Important | ✅ |
| F15 | **Mise à jour README et documentation** | 🟢 Optionnel | ✅ |

---

## 3. Spécifications fonctionnelles détaillées

### F11 — Génération de scripts Gherkin

**Description :**  
Pour chaque Use Case marqué comme « automatisable », l'application génère un fichier `.feature` au format Gherkin (BDD/Cucumber).

**Règles métier :**
- Seuls les UC avec `is_automated = True` génèrent un fichier `.feature`
- Chaque fichier suit la structure : `Feature` → `Background` (préconditions) → `Scenario` (steps)
- Les étapes sont automatiquement classifiées : `Given` (1er step) / `When` (étapes suivantes) / `Then` (dernier step + résultats attendus)
- Les fichiers sont livrés dans un ZIP : `gherkin_features_<source>.zip`
- Structure du ZIP :
  ```
  features/
  ├── uc001_connexion.feature
  ├── uc002_deconnexion.feature
  └── ...
  ```

**Format du fichier généré :**
```gherkin
# Fichier généré automatiquement par QA Recipe Converter
Feature: UC001 — Description du cas

  Background:
    Given Précondition 1
    And   Précondition 2

  Scenario: Description du cas
    When  Étape 1
    And   Étape 2
    Then  Étape finale
    And   Résultat attendu 1
    And   Résultat attendu 2
```

**Endpoint :** `GET /gherkin/<job_id>/?mode=gherkin`

---

### F12 — Génération projet Cypress complet

**Description :**  
L'application génère un projet Cypress complet avec configuration, step definitions pré-remplies et README d'installation.

**Contenu du ZIP généré :**
```
cypress_project/
├── cypress.config.js          # Config Cypress + Cucumber preprocessor
├── package.json               # Dépendances npm
├── .gitignore
├── README.md                  # Instructions d'installation
└── cypress/
    ├── e2e/
    │   ├── <uc_slug>.feature           # Fichiers Gherkin
    │   └── step_definitions/
    │       └── <uc_slug>.js            # Step defs à implémenter
    ├── fixtures/
    │   └── example.json
    └── support/
        ├── commands.js
        └── e2e.js
```

**Dépendances npm incluses :**
- `cypress@^13.6.0`
- `@badeball/cypress-cucumber-preprocessor@^20.0.0`
- `@bahmutov/cypress-esbuild-preprocessor@^2.2.0`

**Endpoint :** `GET /gherkin/<job_id>/?mode=cypress`

---

### F13 — Ouverture dans VS Code

**Description :**  
Génère le projet Cypress dans un répertoire temporaire et tente d'ouvrir VS Code via la CLI `code`.

**Comportement :**
- POST vers `/vscode/<job_id>/`
- Génère le ZIP Cypress
- Extrait dans `<tempdir>/cypress_qa_<job_id[:8]>/`
- Tente `subprocess.Popen(['code', project_dir])`
- Retourne un JSON avec : `vscode_opened`, `project_path`, `message`
- Si VS Code non trouvé : affiche le chemin du projet pour ouverture manuelle

**Réponse JSON :**
```json
{
  "success": true,
  "vscode_opened": true,
  "project_path": "/tmp/cypress_qa_abc12345/",
  "message": "VS Code ouvert avec succès !"
}
```

**Note :** Fonctionne en mode développement local. En production Docker/cloud, VS Code ne peut pas être ouvert automatiquement ; le ZIP Cypress reste disponible au téléchargement.

---

### F14 — Refonte UI

**Objectifs :**
- Design moderne et professionnel
- Cohérence visuelle sur toutes les pages
- Accessibilité améliorée

**Décisions design :**

| Élément | Choix |
|---------|-------|
| Font principale | Inter (Google Fonts) |
| Font monospace | JetBrains Mono |
| Couleur primaire | #2563eb (Blue 600) |
| Couleur accent | #06b6d4 (Cyan 500) |
| Couleur succès | #10b981 (Emerald 500) |
| Fond | #f8fafc (Slate 50) |
| Radius | 10px (card), 14px (large), 18px (xl) |
| Shadows | Multi-niveaux (xs/sm/md/lg/xl) |

**Pages redesignées :**
- `base.html` : Nouveau design system complet (variables CSS, composants)
- `index.html` : Hero section, pipeline visuel, drag & drop amélioré
- `preview.html` : Panel d'export unifié, toggles modernes, modal VS Code
- `result.html` : Actions groupées avec tous les exports

---

## 4. Architecture technique

### 4.1 Nouveaux fichiers

| Fichier | Description |
|---------|-------------|
| `apps/parser/gherkin_generator.py` | Module de génération Gherkin + Cypress |
| `CAHIER_DES_CHARGES.md` | Ce document |

### 4.2 Fichiers modifiés

| Fichier | Modifications |
|---------|--------------|
| `apps/core/views.py` | + `GenerateGherkinView`, `OpenVSCodeView` |
| `apps/core/urls.py` | + routes `/gherkin/<id>/`, `/vscode/<id>/` |
| `templates/base.html` | Refonte complète du design system |
| `templates/core/index.html` | Refonte UI + pipeline visuel |
| `templates/core/preview.html` | Refonte + panel export Gherkin/Cypress |
| `templates/core/result.html` | Refonte + nouveaux boutons d'export |
| `README.md` | Mise à jour complète v2.0 |

### 4.3 Routes

| URL | Vue | Méthode | Description |
|-----|-----|---------|-------------|
| `/` | `IndexView` | GET/POST | Page d'accueil + upload |
| `/preview/<id>/` | `PreviewView` | GET/POST | Prévisualisation éditable |
| `/generate/<id>/` | `GenerateExcelView` | GET | Télécharger Excel |
| `/gherkin/<id>/` | `GenerateGherkinView` | GET | Télécharger Gherkin/Cypress ZIP |
| `/vscode/<id>/` | `OpenVSCodeView` | POST | Ouvrir VS Code |
| `/result/<id>/` | `ResultView` | GET | Page résultat |

---

## 5. Contraintes et exigences non fonctionnelles

### 5.1 Performance
- Génération du ZIP Cypress < 2 secondes pour 50 UC
- Parsing d'un fichier Word de 200 UC < 5 secondes

### 5.2 Sécurité
- Fichiers uploadés supprimés après 1h (configurable)
- Validation stricte des extensions et taille (max 50 MB)
- Protection CSRF sur toutes les vues POST
- Pas de données utilisateur persistées au-delà du job

### 5.3 Compatibilité
- Python 3.12+
- Django 5.0+
- Navigateurs modernes (Chrome, Firefox, Edge, Safari)
- VS Code avec CLI `code` installée (pour F13)

### 5.4 Tests
- Couverture minimale : 80% sur les modules `parser/`
- Tests unitaires pour `gherkin_generator.py`

---

## 6. Évolutions futures (v3.0)

| ID | Fonctionnalité | Priorité |
|----|---------------|----------|
| F20 | Export vers Jira (XRay/Zephyr) | 🟡 |
| F21 | Intégration GitHub Actions pour CI | 🟡 |
| F22 | Génération Playwright en plus de Cypress | 🟢 |
| F23 | Support multi-fichiers Word en batch | 🟢 |
| F24 | Templates Gherkin personnalisables | 🟢 |
| F25 | Authentification utilisateurs | 🟡 |
| F26 | Historique des conversions persistant | 🟢 |

---

*Document maintenu par AT-TechGN — QA Recipe Converter v2.0 — Mai 2026*
