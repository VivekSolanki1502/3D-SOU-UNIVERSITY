import http from 'node:http';
import crypto from 'node:crypto';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const rootDir = path.resolve(__dirname, '..');
const port = Number(process.env.PORT || 8787);
const entities = new Map([
  ['room-b204', { id: 'room-b204', kind: 'room', name: 'Room B-204', metadata: { building: 'innovation-hub', floor: '2' }, published: true }],
  ['central-library', { id: 'central-library', kind: 'facility', name: 'Central Library', metadata: { building: 'central-campus', floor: 'ground' }, published: true }]
]);
const roles = new Set(['VISITOR', 'STUDENT', 'FACULTY', 'DEPARTMENT_ADMIN', 'SUPER_ADMIN']);
const publicFiles = new Set(['index.html', 'styles.css', 'app.js', 'three-scene.js', 'orbit-controls.js', 'manifest.json', 'sw.js']);

function json(response, status, body) {
  response.writeHead(status, { 'content-type': 'application/json', 'cache-control': 'no-store', 'access-control-allow-origin': '*' });
  response.end(JSON.stringify(body));
}
function roleFrom() {
  return 'VISITOR';
}
function requireRole(request, response, allowed) {
  const role = roleFrom(request);
  if (!allowed.includes(role)) { json(response, 403, { error: 'forbidden', role }); return null; }
  return role;
}
function readBody(request) {
  return new Promise(resolve => { let data = ''; request.on('data', chunk => { data += chunk; }); request.on('end', () => { try { resolve(JSON.parse(data || '{}')); } catch { resolve(null); } }); });
}
function idForQr(entityId) {
  return `https://sou.example.edu/campus/${entityId.startsWith('room-') ? 'rooms' : 'facilities'}/${encodeURIComponent(entityId)}`;
}

const mimeTypes = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webmanifest': 'application/manifest+json'
};

async function serveStaticFile(request, response, pathname) {
  const requestedPath = pathname === '/' ? '/index.html' : pathname;
  const relativePath = requestedPath.replace(/^\/+/, '');
  const safePath = path.normalize(relativePath).replace(/\\/g, '/');
  if (!publicFiles.has(safePath)) return false;

  const filePath = path.resolve(rootDir, safePath);
  if (path.dirname(filePath) !== rootDir) {
    json(response, 403, { error: 'forbidden' });
    return true;
  }

  try {
    const file = await fs.readFile(filePath);
    const ext = path.extname(filePath).toLowerCase();
    response.writeHead(200, {
      'content-type': mimeTypes[ext] || 'application/octet-stream',
      'cache-control': 'no-store'
    });
    response.end(file);
    return true;
  } catch {
    return false;
  }
}

const server = http.createServer(async (request, response) => {
  if (request.method === 'OPTIONS') { response.writeHead(204, { 'access-control-allow-origin': '*', 'access-control-allow-methods': 'GET,POST,PUT,OPTIONS', 'access-control-allow-headers': 'content-type,authorization' }); return response.end(); }
  const url = new URL(request.url, `http://${request.headers.host}`);
  if (url.pathname.startsWith('/api/')) {
    if (url.pathname === '/api/health') return json(response, 200, { ok: true, service: 'sou-campus-api', mode: 'demo', database: process.env.DATABASE_URL ? 'configured' : 'not-configured' });
  if (url.pathname === '/api/auth/demo' && request.method === 'POST') {
    return json(response, 200, { token: 'demo:visitor', user: { id: 'demo-user', displayName: 'Demo User', role: 'VISITOR' } });
  }
    if (url.pathname === '/api/entities' && request.method === 'GET') return json(response, 200, { data: [...entities.values()].filter(entity => entity.published || roleFrom(request) !== 'VISITOR') });
    const entityMatch = url.pathname.match(/^\/api\/entities\/([^/]+)$/);
    if (entityMatch && request.method === 'GET') return json(response, entities.has(entityMatch[1]) ? 200 : 404, entities.get(entityMatch[1]) || { error: 'not_found' });
    if (entityMatch && ['PUT', 'POST'].includes(request.method)) {
      const role = requireRole(request, response, ['DEPARTMENT_ADMIN', 'SUPER_ADMIN']); if (!role) return;
      const body = await readBody(request); if (!body?.name) return json(response, 400, { error: 'name_required' });
      const previous = entities.get(entityMatch[1]) || {}; const entity = { ...previous, ...body, id: entityMatch[1], updatedBy: role }; entities.set(entityMatch[1], entity);
      return json(response, 200, { data: entity, audit: { action: previous.id ? 'UPDATE' : 'CREATE', entityId: entityMatch[1], actorRole: role } });
    }
    const qrMatch = url.pathname.match(/^\/api\/qr\/([^/]+)$/);
    if (qrMatch && request.method === 'GET') return json(response, entities.has(qrMatch[1]) ? 200 : 404, { entityId: qrMatch[1], url: idForQr(qrMatch[1]), safe: true });
    if (url.pathname === '/api/admin/audit' && request.method === 'GET') { if (!requireRole(request, response, ['SUPER_ADMIN'])) return; return json(response, 200, { data: [{ action: 'UPDATE', entityId: 'room-b204', actorRole: 'SUPER_ADMIN', createdAt: new Date().toISOString() }] }); }
    json(response, 404, { error: 'not_found' });
    return;
  }

  const served = await serveStaticFile(request, response, url.pathname);
  if (served) return;

  json(response, 404, { error: 'not_found' });
});

server.listen(port, () => console.log(`SOU Campus API listening on http://localhost:${port}`));
