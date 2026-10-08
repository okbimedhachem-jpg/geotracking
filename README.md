# GeoTracking

Suivi GPS en temps réel pour véhicules, conducteurs et personnes autorisées.

## Stack
- Mobile: Flutter
- Backend: FastAPI
- Frontend WebSIG: React + Leaflet
- Base de données: PostgreSQL + PostGIS
- Temps réel: WebSocket
- Conteneurisation: Docker Compose

## Architecture
Smartphone GPS -> FastAPI -> PostgreSQL/PostGIS -> WebSocket -> Carte WebSIG

## Démarrage rapide

### 1) Cloner le projet
```bash
git clone https://github.com/okbimedhachem-jpg/geotracking.git
cd geotracking
```

### 2) Créer le fichier d'environnement
```bash
cp .env.example .env
```

### 3) Démarrer l'infrastructure
```bash
docker compose up -d
```

### 4) Lancer le backend
```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5) Lancer le frontend web
```bash
cd apps/web
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### 6) Lancer le mobile
```bash
cd apps/mobile
flutter pub get
flutter run
```

## API

### Santé du service
```http
GET /api/v1/health
```

### Envoi de position
```http
POST /api/v1/location
Content-Type: application/json
```

Exemple :
```json
{
  "user_id": 25,
  "latitude": 36.8065,
  "longitude": 10.1815,
  "accuracy": 8,
  "speed": 32,
  "heading": 145,
  "timestamp": "2026-10-08T21:20:15"
}
```

### WebSocket
```text
ws://localhost:8000/ws
```

## Fonctionnalités prévues
- Suivi GPS en temps réel
- Carte interactive
- Historique des déplacements
- Distance parcourue
- Vitesse et direction
- Trajectoire
- Temps d'arrêt
- Alertes / geofencing
- Export GPX/KML/GeoJSON
- Données géospatiales avec PostGIS

## Structure du projet
```text
geotracking/
├── apps/
│   ├── mobile/
│   │   ├── android/
│   │   ├── ios/
│   │   ├── lib/
│   │   ├── analysis_options.yaml
│   │   ├── pubspec.yaml
│   │   └── README.md
│   ├── backend/
│   │   ├── app/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── README.md
│   └── web/
│       ├── public/
│       ├── src/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.js
│       └── README.md
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── LICENSE
```

## License
MIT
