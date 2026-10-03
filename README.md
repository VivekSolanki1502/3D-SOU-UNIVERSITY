# SOU Campus Digital Twin

> A polished, accessible campus companion for Silver Oak University, Ahmedabad.
> Search the campus, discover places, plan routes, explore a live 3D blueprint, and find the right help quickly.

<p align="center">
	<strong>Interactive campus navigation · 3D blueprint explorer · accessibility-first UX</strong>
</p>

## Overview

SOU Campus Digital Twin is a responsive university navigation experience designed around the moments that matter on campus: finding a classroom before the next lecture, locating a faculty member, discovering events, choosing an accessible route, and getting emergency guidance without friction.

The experience combines a calm, editorial dashboard with a neon cyan 3D campus blueprint. Buildings have real height and depth, floor slices, glowing edges, hover states, camera focus animation, live search, and touch-friendly controls.

## Highlights

- **Interactive 3D campus** with perspective, depth, fog, isometric grid lines, building edges, floor slices, and distinct building heights.
- **Direct manipulation** with orbit rotation, wheel zoom, right-drag pan, touch rotation, pinch zoom, reset view, and optional auto-rotate.
- **Campus search** across buildings, rooms, facilities, aliases, faculty, and departments.
- **Building discovery** with hover labels, click-to-focus camera movement, filtered results, and connected detail cards.
- **Navigation workflows** with route previews, accessible-path preferences, closures, emergency exits, assembly areas, and deep links.
- **Responsive layout** with a desktop workspace sidebar and a mobile bottom navigation experience.
- **Inclusive controls** including high contrast, reduced motion, language preview, low-bandwidth fallback, and accessible route mode.
- **Demo role views** for Student, Faculty, Visitor, Department Admin, and Super Admin contexts.
- **Local API** for health checks, demo authentication, entities, QR links, admin writes, and audit data.

## Preview

Start the project locally and open the Explore view:

```text
http://localhost:8000/#explore
```

The home route is available at:

```text
http://localhost:8000/#home
```

## Run locally

### Requirements

- Python 3.12+
- Node.js 18+ and npm for JavaScript validation

### Start the integrated app

FastAPI serves the browser app and its `/api/v1` endpoints together. In PowerShell:

```powershell
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
$env:SECRET_KEY = (& python -c "import secrets; print(secrets.token_hex(32))")
$env:DATABASE_URL = "sqlite+aiosqlite:///./sou_disha.db"
$env:REDIS_ENABLED = "false"
python -m uvicorn app.main:app --reload --port 8000
```

Before starting, edit `backend/.env` and replace every `replace-with-...` placeholder with a unique value. Keep `BACKEND_CORS_ORIGINS` empty for same-origin local use; configure only explicit origins when hosting the UI separately.

Open `http://localhost:8000/#explore`. The API health check and interactive docs are available at `http://localhost:8000/api/v1/health` and `http://localhost:8000/api/v1/docs`.

Run the backend tests from `backend/` with the same environment variables set using `python -m pytest tests -q`.

The Node server in `server/server.js` is retained as a visitor-only legacy demo server. The integrated UI uses FastAPI. Seed credentials and the JWT signing key must be supplied through environment configuration; the checked-in example contains placeholders only.

### Validate the JavaScript

From the project root:

```powershell
npm.cmd run validate
```

## How to explore

1. Open **Explore campus** from the sidebar or visit `#explore`.
2. Drag the 3D scene to orbit around the campus.
3. Scroll or pinch to zoom, and right-drag to pan.
4. Hover a building to reveal its label.
5. Click a building to focus the camera and open its details.
6. Search by building, department, faculty member, or short code.
7. Use **Reset view** or enable **Auto-rotate** from the blueprint panel.

## Technical structure

| File | Responsibility |
| --- | --- |
| `index.html` | Application shell, routes, view panels, and semantic UI markup |
| `styles.css` | Responsive design system, dashboard UI, and blueprint panel styling |
| `app.js` | API client, campus search/routing, accessibility settings, roles, events, exams, and admin workflows |
| `three-scene.js` | API-backed Three.js campus scene, building selection, camera focus, and rendering loop |
| `orbit-controls.js` | Lightweight local orbit, zoom, pan, damping, and touch controls |
| `server/server.js` | Legacy static file server and demo API endpoints |
| `backend/app/main.py` | FastAPI app serving the browser UI and versioned API |
| `prisma/schema.prisma` | Future production data model foundation |
| `sw.js` | Service-worker caching for local app assets |

The project uses vanilla HTML, CSS, and JavaScript with Three.js loaded as an ES module. There is no frontend framework or bundler, keeping the prototype easy to inspect and run.

## Demo data and production notes

This repository is an intentionally self-contained prototype. Campus locations, timetable entries, faculty availability, events, notices, routes, emergency contacts, and admin metrics are demo data.

Before production deployment, SOU will need to connect:

- Verified campus geometry, floors, rooms, paths, entrances, and accessibility metadata.
- ERP, LMS, timetable, directory, and identity-provider integrations.
- Approved emergency operations, closure data, contact channels, and audit requirements.
- Authenticated role-based API enforcement and privacy/security review.
- Final GIS, CAD, GLB, or other campus assets with a tested performance budget.

See [`integrations.md`](integrations.md) for the integration contracts and privacy boundaries.

## Roadmap

- Replace demo location data with typed PostgreSQL/Prisma APIs.
- Validate route graphs with campus operations and accessibility stakeholders.
- Add authenticated CRUD workflows with audit logs and permissions.
- Connect timetable, events, directory, and emergency operations services.
- Introduce production campus geometry with lazy-loaded GLB/GIS assets.
- Complete keyboard, screen-reader, contrast, mobile performance, and route usability audits.

## License

This project is currently maintained as a private university prototype. Add an approved license before public redistribution.
