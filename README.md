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
http://localhost:8787/#explore
```

The home route is available at:

```text
http://localhost:8787/#home
```

## Run locally

### Requirements

- Node.js 18+
- npm

### Start the app

PowerShell users can run the Windows npm launcher directly:

```powershell
npm.cmd install
npm.cmd run dev
```

Then visit `http://localhost:8787`.

### Validate the JavaScript

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
| `app.js` | Campus data, routing, search, accessibility settings, roles, and demo workflows |
| `three-scene.js` | Three.js scene, building factory, raycasting, camera focus, and rendering loop |
| `orbit-controls.js` | Lightweight local orbit, zoom, pan, damping, and touch controls |
| `server/server.js` | Static file server and demo API endpoints |
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
