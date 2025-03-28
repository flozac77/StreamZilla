# VisiBrain - Explorateur de Vidéos Twitch 🎮

VisiBrain est une application web qui vous permet de rechercher et regarder des vidéos Twitch par jeu. C'est comme un YouTube, mais spécialisé pour les vidéos de jeux vidéo sur Twitch !

## 🚀 Comment commencer ?

### 1. Installation des outils nécessaires

#### Pour le Backend (serveur) :
1. Téléchargez et installez Python 3.8 ou plus récent depuis [python.org](https://www.python.org/downloads/)
   - **Important** : Cochez la case "Add Python to PATH" lors de l'installation
2. Ouvrez un terminal (PowerShell sur Windows)
3. Vérifiez que Python est bien installé :
   ```bash
   python --version
   ```

#### Pour le Frontend (interface) :
1. Téléchargez et installez Node.js 16 ou plus récent depuis [nodejs.org](https://nodejs.org/)
2. Vérifiez que Node.js est bien installé :
   ```bash
   node --version
   ```

### 2. Configuration de ngrok (pour tester l'API en local)

1. Téléchargez ngrok depuis [ngrok.com](https://ngrok.com/download)
2. Créez un compte gratuit sur ngrok.com
3. Connectez votre compte ngrok :
   ```bash
   ngrok config add-authtoken votre_token_ngrok
   ```
4. Lancez ngrok pour exposer votre serveur local :
   ```bash
   ngrok http 8000
   ```
5. Copiez l'URL HTTPS générée (ex: `https://abc123.ngrok.io`)

### 3. Configuration de l'API Twitch

1. Allez sur [Twitch Developer Console](https://console.twitch.tv/)
2. Connectez-vous avec votre compte Twitch
3. Cliquez sur "Applications" puis "Register Your Application"
4. Remplissez le formulaire :
   - Name : "VisiBrain" (ou ce que vous voulez)
   - OAuth Redirect URLs : `https://abc123.ngrok.io/callback` (remplacez par votre URL ngrok)
   - Category : "Website Integration"
5. Cliquez sur "Create"
6. Notez votre "Client ID" et "Client Secret"

### 4. Installation du projet

#### Backend (serveur) :
```bash
# 1. Allez dans le dossier backend
cd backend

# 2. Créez un environnement virtuel
python -m venv venv

# 3. Activez l'environnement virtuel
# Sur Windows :
venv\Scripts\activate
# Sur Mac/Linux :
source venv/bin/activate

# 4. Installez les dépendances
pip install -r requirements.txt

# 5. Créez un fichier .env
# Copiez ce contenu dans un nouveau fichier .env :
TWITCH_CLIENT_ID=votre_client_id
TWITCH_CLIENT_SECRET=votre_client_secret
TWITCH_REDIRECT_URI=https://abc123.ngrok.io/callback  # Remplacez par votre URL ngrok
DATABASE_URL=sqlite:///./app.db
CACHE_TTL=120
CACHE_MAX_SIZE=100
```

#### Frontend (interface) :
```bash
# 1. Allez dans le dossier frontend
cd frontend

# 2. Installez les dépendances
npm install

# 3. Créez un fichier .env
# Copiez ce contenu dans un nouveau fichier .env :
VITE_API_URL=https://abc123.ngrok.io  # Remplacez par votre URL ngrok
```

### 5. Lancement de l'application

1. Démarrez le backend :
```bash
# Dans le dossier backend
uvicorn backend.app.main:app --reload
```

2. Démarrez le frontend :
```bash
# Dans le dossier frontend
npm run dev
```

3. Ouvrez votre navigateur et allez à `http://localhost:5173`

## 🎯 Fonctionnalités

- 🔍 Recherche de vidéos par jeu
- 📊 Filtrage par :
  - Date (aujourd'hui, cette semaine, ce mois)
  - Durée (court, moyen, long)
  - Nombre de vues
  - Langue
- 🌙 Mode sombre
- 📱 Interface responsive (mobile, tablette, ordinateur)
- ⚡ Actualisation automatique toutes les 2 minutes

## 🛠️ Structure du projet

```
.
├── backend/           # Serveur (Python)
│   ├── app/          # Code de l'application
│   └── tests/        # Tests du serveur
└── frontend/         # Interface (Vue.js)
    ├── src/          # Code de l'interface
    └── tests/        # Tests de l'interface
```

## 🧪 Tests

### Backend :
```bash
cd backend
pytest
```

### Frontend :
```bash
cd frontend
npm run test:unit
```

## 🔒 Sécurité

- Les identifiants Twitch sont stockés de manière sécurisée
- Les requêtes sont limitées pour éviter la surcharge
- Les données sensibles sont protégées

## 📚 Documentation API

La documentation de l'API est disponible à `http://localhost:8000/docs`

## ❓ Questions fréquentes

1. **L'application ne démarre pas ?**
   - Vérifiez que Python et Node.js sont bien installés
   - Assurez-vous que tous les fichiers .env sont correctement configurés
   - Vérifiez que les ports 8000 et 5173 sont disponibles
   - Assurez-vous que ngrok est bien configuré et que l'URL est correcte

2. **Les vidéos ne s'affichent pas ?**
   - Vérifiez vos identifiants Twitch dans le fichier .env
   - Assurez-vous que l'URL ngrok est correctement configurée dans :
     - Twitch Developer Console
     - Fichier .env du backend
     - Fichier .env du frontend
   - Vérifiez que ngrok est bien en cours d'exécution

3. **Les tests échouent ?**
   - Vérifiez que toutes les dépendances sont installées
   - Assurez-vous d'être dans le bon dossier lors de l'exécution des tests

## 🤝 Contribution

1. Fork le projet
2. Créez une branche (`git checkout -b feature/MaNouvelleFonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Push sur la branche (`git push origin feature/MaNouvelleFonctionnalite`)
5. Ouvrez une Pull Request 