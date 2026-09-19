# KihanNama Backend (FastAPI + PostgreSQL + MongoDB)

Production-ready asynchronous backend for **KihanNama (کیهان‌نما)** with TLE orbit propagation, dynamic CZML generation for CesiumJS, and operational space station catalogs.

---

## Features

- **FastAPI Framework**: High performance async API with automatic OpenAPI interactive documentation (`/docs` and `/redoc`).
- **Dual Database Support**:
  - **PostgreSQL (Neon)**: Configured with `SQLAlchemy` + `asyncpg` for relational satellite ephemeris, orbital classes, and station metrics.
  - **MongoDB**: Built-in async driver (`motor`) with automatic fallback.
- **Active Satellite Ingestion**: Parses over 16,000 active satellites from `active-satellite.txt` into classified orbital categories (LEO, MEO, GEO, HEO).
- **CZML Generator Engine**: Generates Cesium Language (CZML) orbital paths with Lagrange 5th-degree interpolation, polylines, billboards, and labels for Cesium 3D globe visualization.
- **Space Station Catalog**: Parses operational space stations and docked craft (`station-ops.csv`), including ISS (Zarya, Poisk, Nauka), Tiangong (Tianhe, Wentian, Mengtian), Crew Dragon 12, Soyuz-MS 29, Shenzhou-23, Cygnus NG-24, and Progress-MS.

---

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health status, database connectivity (Postgres + Mongo), and entity counts |
| `/api/satellites` | GET | Filterable satellite list (`search`, `orbit_class`, `category`, pagination) |
| `/api/satellites/{norad_id}` | GET | Satellite detail by NORAD ID with Keplerian elements |
| `/api/satellites/czml` | GET | Dynamic CZML dataset generation with limits and filters |
| `/api/satellites/{norad_id}/czml` | GET | CZML trajectory packet for a single satellite |
| `/api/stations/space` | GET | Space station modules and visiting vehicles catalog |
| `/api/stations/space/{identifier}` | GET | Space station details and telemetry |
| `/api/stations/space/{identifier}/czml` | GET | CZML orbit packet for a space station |
| `/api/czml/active` | GET | Streamable CZML packet array for active satellites |
| `/api/czml/space-stations` | GET | CZML packet array for all space stations |
| `/api/czml/from-tle` | POST | Convert custom 2-line/3-line TLE to CZML |

---

## Setup & Running Locally

### 1. Install Dependencies
```bash
cd backend
python -m pip install -r requirements.txt
```

### 2. Configure Environment
Check `.env` file (already preconfigured with your Neon PostgreSQL credentials).

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

Interactive API documentation will be available at:
`http://localhost:8000/docs`
# kihannama-backend
