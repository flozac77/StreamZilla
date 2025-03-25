# VisioBrain - Explorateur de Vidéos Twitch

VisioBrain est une application web permettant de rechercher et visualiser des vidéos Twitch par jeu. Elle utilise l'API Twitch pour récupérer les vidéos et offre une interface moderne et réactive.

## 🚀 Démarrage Rapide

### Prérequis

- Python 3.8+ pour le backend
- Node.js 16+ pour le frontend
- Un compte développeur Twitch et les identifiants API (Client ID et Secret)

## 🔧 Backend (FastAPI)

### Installation

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

1. Créez un fichier `.env` dans le dossier `backend` :
```env
TWITCH_CLIENT_ID=votre_client_id
TWITCH_CLIENT_SECRET=votre_client_secret
TWITCH_REDIRECT_URI=http://localhost:5173/callback
DATABASE_URL=sqlite:///./app.db
CACHE_TTL=120  # Durée du cache en secondes
CACHE_MAX_SIZE=100  # Nombre maximum d'entrées en cache
```

### Lancement

```bash
uvicorn backend.app.main:app --reload
```

### Tests

```bash
pytest backend/tests/
```

### Points d'API Principaux

- `GET /api/search` : Recherche des vidéos par jeu
- `GET /api/auth/test` : Test de l'authentification

## 🎨 Frontend (Vue.js)

### Installation

```bash
cd frontend
npm install
```

### Configuration

1. Créez un fichier `.env` dans le dossier `frontend` :
```env
VITE_API_URL=http://localhost:5173
```

### Lancement

```bash
npm run dev
```

### Build Production

```bash
npm run build
```

### Tests

```bash
npm run test
```

## 🌟 Fonctionnalités

- Recherche de vidéos par jeu
- Mise en cache des résultats pour optimiser les performances
- Interface responsive et moderne
- Mode sombre
- Actualisation automatique des résultats toutes les 2 minutes
- Affichage des vues et de la durée des vidéos
- Liens directs vers les vidéos Twitch

## 🔍 Structure du Projet

```
.
├── backend/
│   ├── app/
│   │   ├── models/
│   │   ├── routes/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
└── frontend/
    ├── src/
    │   ├── components/
    │   ├── views/
    │   ├── stores/
    │   └── App.vue
    └── tests/
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push sur la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Notes

- L'application utilise SQLite par défaut, mais peut être configurée pour utiliser d'autres bases de données
- Le cache est configuré pour expirer après 2 minutes par défaut
- Les tests d'intégration nécessitent une connexion internet pour les appels à l'API Twitch

## 🔐 Sécurité

- Les tokens Twitch sont stockés de manière sécurisée
- Les requêtes API sont limitées en fréquence
- Les données sensibles sont protégées via les variables d'environnement

## 📚 Documentation API

La documentation Swagger de l'API est disponible à l'adresse : `http://localhost:5173/docs` 