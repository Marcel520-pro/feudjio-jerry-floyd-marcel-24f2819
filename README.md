# 🎮 TP232

**Enquête interactive sur le game development au Cameroun**

> *"Est-il possible de faire du game development au Cameroun malgré les contraintes techniques, financières et culturelles ?"*

---

## 🚀 Lancement rapide

```bash
# 1. Cloner / décompresser le projet
cd CamGamePulse

# 2. Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer l'application
python run.py
```

Ouvrir **http://localhost:5000** dans le navigateur.

---

## 📁 Structure

```
CamGamePulse/
├── app/
│   ├── templates/       # HTML (index, minigame, dashboard, merci)
│   ├── static/          # CSS + JS
│   ├── models/
│   │   └── database.py  # Modèles SQLite (Reponse, Minigame)
│   └── routes.py        # Toutes les routes Flask
├── instance/
│   └── data.db          # Base SQLite (créée automatiquement)
├── requirements.txt
├── run.py               # Point d'entrée
└── README.md
```

---

## 🔗 Routes

| Route | Description |
|---|---|
| `GET /` | Formulaire d'enquête |
| `POST /` | Soumission → redirige vers mini-jeu |
| `GET /minigame/<id>` | Mini-jeu "Dev or Not" |
| `POST /minigame/<id>/submit` | Enregistre le score de résilience |
| `GET /merci/<id>` | Page de confirmation + diagnostic |
| `GET /dashboard` | Dashboard Chart.js |
| `GET /export` | Téléchargement CSV (UTF-8 BOM) |

---

## 🎮 Mini-jeu "Dev or Not"

3 scénarios inspirés du quotidien du développeur camerounais :
1. **La coupure de courant** – Que fais-tu face à la perte de données ?
2. **Le refus familial** – Comment réagis-tu aux pressions culturelles ?
3. **Le manque de ressources** – Comment avances-tu sans moyens ?

**Score de résilience** : 0 à 3 points selon les choix.

| Score | Titre |
|---|---|
| 0 | Débutant Résistant |
| 1 | Hackeur Débrouillard |
| 2 | Pionnier du Code |
| 3 | Légende du Game Dev Cam |

---

## 🛠 Stack technique

- **Backend** : Flask 3 + Flask-SQLAlchemy
- **Base de données** : SQLite (fichier `instance/data.db`)
- **Frontend** : HTML5 + CSS custom + JS vanilla
- **Charts** : Chart.js 4 (CDN)
- **Polices** : Syne + Space Mono (Google Fonts)

---

## 📊 Export des données

`GET /export` télécharge un CSV avec toutes les réponses, encodé en UTF-8 BOM (compatible Excel et Google Sheets).
