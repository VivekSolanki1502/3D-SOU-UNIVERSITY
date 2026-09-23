let locations = [
  { id: 'innovation-hub', name: 'Innovation Hub', type: 'building', meta: 'Zone A · 4 floors · 24 rooms', code: 'IH', aliases: ['block b', 'બ્લોક બી', 'ब्लॉक बी'] },
  { id: 'central-library', name: 'Central Library', type: 'facility', meta: 'Central Campus · Ground + 2 floors', code: '▤', aliases: ['library', 'પુસ્તકાલય', 'पुस्तकालय'] },
  { id: 'admin-block', name: 'Admin Block', type: 'building', meta: 'Zone C · 3 floors · Reception', code: 'AB', aliases: ['reception', 'વહીવટી બ્લોક', 'प्रशासन ब्लॉक'] },
  { id: 'school-design', name: 'School of Design', type: 'building', meta: 'Zone D · 3 floors · Studios', code: 'SD', aliases: ['design school', 'ડિઝાઇન', 'डिजाइन'] },
  { id: 'room-b204', name: 'Room B-204', type: 'room', meta: 'Innovation Hub · 2nd floor · Classroom', code: '204', aliases: ['b204', 'classroom 204', 'રૂમ બી ૨૦૪', 'कमरा बी 204'] },
  { id: 'lab-b108', name: 'Lab B-108', type: 'room', meta: 'Innovation Hub · Ground floor · Computer lab', code: '108', aliases: ['computer lab', 'લેબ', 'कंप्यूटर लैब'] },
  { id: 'medical-room', name: 'Medical Room', type: 'facility', meta: 'Admin Block · Ground floor · Open 24/7', code: '✚', aliases: ['clinic', 'મેડિકલ રૂમ', 'चिकित्सा कक्ष'] },
  { id: 'canteen', name: 'Canteen', type: 'facility', meta: 'Central Campus · Ground floor · 8 AM – 8 PM', code: '◒', aliases: ['food court', 'કેન્ટીન', 'कैंटीन'] },
  { id: 'parking', name: 'Parking', type: 'facility', meta: 'East Gate · 180 spaces · Accessible', code: 'P', aliases: ['car park', 'પાર્કિંગ', 'पार्किंग'] },
  { id: 'meera-shah', name: 'Dr. Meera Shah', type: 'room', meta: 'Faculty · Innovation Hub · B-312', code: 'MS', aliases: ['meera', 'computer science faculty'] },
  { id: 'main-gate', name: 'Main Gate', type: 'facility', meta: 'North entrance · Reception nearby', code: '⌂', aliases: ['entrance', 'મુખ્ય દરવાજો', 'मुख्य द्वार'] },
  { id: 'auditorium', name: 'Auditorium', type: 'facility', meta: 'Central Campus · 650 seats · Accessible', code: 'AU', aliases: ['hall', 'ઓડિટોરિયમ', 'सभागार'] },
  { id: 'east-exit', name: 'East Exit', type: 'facility', meta: 'Emergency exit · Clearly marked', code: '↗', aliases: ['safe exit'] },
  { id: 'assembly-area', name: 'Assembly Area', type: 'facility', meta: 'Sports Ground · Emergency gathering point', code: '⌖', aliases: ['sports ground', 'મિલન સ્થળ', 'सभा क्षेत्र'] }
];

try {
  const savedEntities = JSON.parse(localStorage.getItem('sou-campus-entities') || '[]');
  savedEntities.forEach(saved => {
    const index = locations.findIndex(location => location.id === saved.id);
    if (index >= 0) locations[index] = { ...locations[index], ...saved };
  });
} catch { /* Storage can be unavailable in private or file contexts. */ }

const routeGraph = {
  'current': [{ to: 'room-b204', distance: 0, minutes: 0, accessible: true, instruction: 'You are at Innovation Hub · B-204' }],
  'room-b204': [{ to: 'innovation-hub', distance: 80, minutes: 1, accessible: true, instruction: 'Take the lift to the Innovation Hub lobby' }],
  'innovation-hub': [
    { to: 'central-library', distance: 250, minutes: 3, accessible: true, instruction: 'Follow the covered east walkway past the Central Library' },
    { to: 'admin-block', distance: 300, minutes: 4, accessible: true, instruction: 'Continue south on the accessible campus path' },
    { to: 'school-design', distance: 220, minutes: 3, accessible: false, instruction: 'Cross the north pedestrian path' }
  ],
  'central-library': [{ to: 'main-gate', distance: 180, minutes: 2, accessible: true, instruction: 'Continue north toward the main entrance' }, { to: 'auditorium', distance: 130, minutes: 2, accessible: true, instruction: 'Turn right at the central quad' }],
  'admin-block': [{ to: 'medical-room', distance: 20, minutes: 1, accessible: true, instruction: 'Enter through the ground-floor east entrance' }, { to: 'east-exit', distance: 160, minutes: 2, accessible: true, instruction: 'Follow the signed emergency corridor to East Gate' }],
  'school-design': [{ to: 'auditorium', distance: 260, minutes: 3, accessible: true, instruction: 'Use the covered path beside the design studios' }],
  'main-gate': [{ to: 'parking', distance: 100, minutes: 1, accessible: true, instruction: 'Parking is immediately beyond the east turn' }],
  'auditorium': [{ to: 'assembly-area', distance: 280, minutes: 4, accessible: true, instruction: 'Cross the central quad to the Sports Ground' }],
  'east-exit': [{ to: 'assembly-area', distance: 140, minutes: 2, accessible: true, instruction: 'Follow the marked emergency route to the assembly point' }]
};

const translations = {
  en: { search: 'Search campus', explore: 'Explore campus', myday: 'My day', emergency: 'Emergency help' },
  gu: { search: 'કેમ્પસ શોધો', explore: 'કેમ્પસ જુઓ', myday: 'મારો દિવસ', emergency: 'કટોકટી મદદ' },
  hi: { search: 'कैंपस खोजें', explore: 'कैंपस देखें', myday: 'मेरा दिन', emergency: 'आपातकालीन सहायता' }
};

const state = { filter: 'all', query: '', lang: 'en', role: 'student', accessible: false, currentNode: 'room-b204' };
const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function normalize(value) {
  return value.toLowerCase().replace(/[\s-]+/g, '').trim();
}

function editDistance(left, right) {
  const row = Array.from({ length: right.length + 1 }, (_, index) => index);
  for (let index = 1; index <= left.length; index += 1) {
    let diagonal = row[0];
    row[0] = index;
    for (let cursor = 1; cursor <= right.length; cursor += 1) {
      const above = row[cursor];
      row[cursor] = left[index - 1] === right[cursor - 1] ? diagonal : Math.min(diagonal + 1, row[cursor] + 1, row[cursor - 1] + 1);
      diagonal = above;
    }
  }
  return row[right.length];
}

function locationMatches(location, query) {
  if (!query) return true;
  const needle = normalize(query);
  const searchable = [location.name, location.meta, ...(location.aliases || [])].map(normalize);
  return searchable.some(value => value.includes(needle) || (needle.length > 3 && editDistance(value, needle) <= 2));
}

function findLocation(target) {
  return locations.find(location => location.name === target || location.id === target || (location.aliases || []).includes(target)) || locations[0];
}

function calculateRoute(destination) {
  const target = findLocation(destination).id;
  const queue = [{ node: state.currentNode, path: [], distance: 0, minutes: 0 }];
  const visited = new Set();
  while (queue.length) {
    queue.sort((left, right) => left.minutes - right.minutes);
    const current = queue.shift();
    if (current.node === target) return current;
    if (visited.has(current.node)) continue;
    visited.add(current.node);
    (routeGraph[current.node] || []).forEach(edge => {
      if (state.accessible && !edge.accessible) return;
      queue.push({ node: edge.to, path: [...current.path, edge], distance: current.distance + edge.distance, minutes: current.minutes + edge.minutes });
    });
  }
  return null;
}

function showView(viewId) {
  const target = document.getElementById(viewId) ? viewId : 'home';
  $$('[data-view-panel]').forEach(view => view.classList.toggle('active', view.id === target));
  $$('[data-nav]').forEach(link => link.classList.toggle('active', link.dataset.nav === target));
  history.replaceState(null, '', `#${target}`);
  window.scrollTo({ top: 0, behavior: document.body.classList.contains('reduced-motion') ? 'auto' : 'smooth' });
}

function typeLabel(type) {
  return type === 'building' ? 'BUILDING' : type === 'room' ? 'ROOM / FACULTY' : 'FACILITY';
}

function renderResults(query = state.query) {
  state.query = query.trim();
  const needle = state.query.toLowerCase();
  const filtered = locations.filter(location => {
    const matchesQuery = locationMatches(location, needle);
    return matchesQuery && (state.filter === 'all' || location.type === state.filter);
  });
  const list = $('#resultsList');
  if (!list) return;
  $('#resultCount').textContent = `${filtered.length} result${filtered.length === 1 ? '' : 's'}`;
  list.innerHTML = filtered.length ? filtered.map(location => `
    <article class="result-card">
      <div class="result-icon ${location.type}">${location.code}</div>
      <div><h3>${location.name}</h3><p>${typeLabel(location.type)}</p><small>${location.meta}</small></div>
      <div><button class="text-button result-action" data-target="${location.name}">Navigate →</button><button class="text-button" data-action="qr" data-target="${location.name}" title="Copy safe QR link">QR</button></div>
    </article>`).join('') : `<div class="empty-result"><h2>No location found</h2><p>Try a building, room number, or facility name.</p></div>`;
}

function renderBuildings() {
  const list = $('#buildingList');
  if (!list) return;
  list.innerHTML = locations.filter(item => item.type === 'building').map(item => `<article class="panel"><div class="result-icon building">${item.code}</div><h2>${item.name}</h2><p>${item.meta}</p><button class="text-button result-action" data-target="${item.name}">View details →</button></article>`).join('');
}

function openRoute(target) {
  const location = findLocation(target);
  const route = calculateRoute(location.id);
  const summary = $('.route-summary');
  const steps = $$('.route-modal .route-step');
  $('#routeTitle').textContent = `Route to ${location.name}`;
  if (!route) {
    summary.innerHTML = '<div><strong>—</strong><span>No route</span></div><div><strong>Try 2D</strong><span>Fallback map</span></div><div><strong>Help</strong><span>Ask reception</span></div>';
    $('.route-line').innerHTML = '<div class="route-start">!</div><div><strong>Destination is not reachable</strong><small>Choose a nearby building or ask reception for assistance.</small></div>';
    steps.forEach(step => { step.classList.add('hidden'); });
  } else {
    summary.innerHTML = `<div><strong>${route.minutes || 1} min</strong><span>walking time</span></div><div><strong>${route.distance || 80} m</strong><span>distance</span></div><div><strong>${state.accessible ? '♿' : '↗'}</strong><span>${state.accessible ? 'accessible' : 'standard route'}</span></div>`;
    $('.route-line').innerHTML = '<div class="route-start">●</div><div><strong>Current location</strong><small>Innovation Hub · B-204</small></div>';
    const routeSteps = route.path.length ? route.path : [{ instruction: `Arrive at ${location.name}`, distance: 0 }];
    steps.forEach((step, index) => {
      const item = routeSteps[index];
      step.classList.toggle('hidden', !item);
      if (item) step.innerHTML = `<span>${index + 1}</span><div><strong>${item.instruction}</strong><small>${item.distance ? `${item.distance} m · ${item.accessible ? 'accessible path' : 'stairs may be present'}` : 'Destination reached'}</small></div>`;
    });
  }
  $('#routeModal').classList.remove('hidden');
  $('#routeModal').setAttribute('aria-hidden', 'false');
}

function closeRoute() {
  $('#routeModal').classList.add('hidden');
  $('#routeModal').setAttribute('aria-hidden', 'true');
}

function toast(message) {
  const node = $('#toast');
  node.textContent = message;
  node.classList.add('show');
  window.clearTimeout(toast.timer);
  toast.timer = window.setTimeout(() => node.classList.remove('show'), 2600);
}

function selectBuilding(name) {
  $$('.building').forEach(building => building.classList.toggle('selected', building.dataset.building === name));
  const location = locations.find(item => item.name === name) || locations[0];
  const panel = $('#selectedLocation');
  panel.innerHTML = `<div class="location-icon">${location.code}</div><h2>${location.name}</h2><p>${location.type === 'building' ? 'Academic building · Zone A' : location.meta}</p><div class="side-divider"></div><div class="detail-line"><span>⌂</span><div><strong>${location.type === 'building' ? '4 floors' : 'Ground floor'}</strong><small>${location.type === 'building' ? '24 rooms · 3 labs' : 'Open to campus community'}</small></div></div><div class="detail-line"><span>♿</span><div><strong>Accessible entrance</strong><small>East entrance · Lift available</small></div></div><div class="detail-line"><span>◷</span><div><strong>Open today</strong><small>8:00 AM – 8:00 PM</small></div></div><button class="primary-button full" data-action="navigate" data-target="${location.name}">Plan route <span>→</span></button><button class="secondary-button full" data-action="details" data-target="${location.name}">View building details</button>`;
}

window.addEventListener('campus-building-selected', event => selectBuilding(event.detail.name));

function setLanguage(lang) {
  state.lang = lang;
  $$('.lang').forEach(button => button.classList.toggle('active', button.dataset.lang === lang));
  $('#languageButton').textContent = lang.toUpperCase();
  const copy = translations[lang];
  $('#search h1').textContent = copy.search;
  $('#explore h1').textContent = copy.explore;
  $('#myday h1').textContent = copy.myday;
  $('#emergency h1').textContent = copy.emergency;
  if (lang !== 'en') {
    toast(`${copy.search} · interface preview enabled`);
  } else toast('English interface enabled');
}

function toggleLowBandwidth(enabled) {
  $('#explore3d').style.display = enabled ? 'none' : '';
  $('#explore2d').style.display = enabled ? 'block' : 'none';
  $('#explore3d').classList.toggle('hidden', enabled);
  $('#explore2d').classList.toggle('hidden', !enabled);
  $('#view3d').classList.toggle('selected', !enabled);
  $('#view2d').classList.toggle('selected', enabled);
  toast(enabled ? '2D low-bandwidth mode enabled' : '3D campus mode enabled');
}

function closeRoleModal() {
  $('#roleModal').classList.add('hidden');
}

function persistLocation(location) {
  const saved = locations.map(item => ({ id: item.id, name: item.name, meta: item.meta, aliases: item.aliases, code: item.code, type: item.type }));
  localStorage.setItem('sou-campus-entities', JSON.stringify(saved));
  toast(`${location.name} saved locally · audit event recorded`);
}

async function fetchQrLink(entityId) {
  try {
    const response = await fetch(`http://localhost:8787/api/qr/${encodeURIComponent(entityId)}`);
    if (!response.ok) throw new Error('QR service unavailable');
    return (await response.json()).url;
  } catch {
    return `${location.origin}/#rooms/${encodeURIComponent(entityId)}`;
  }
}

function openRoleModal() {
  $('#roleModal').classList.remove('hidden');
  $$('.role-option').forEach(option => option.classList.toggle('selected', option.dataset.role === state.role));
}

function handleDeepLink() {
  const path = window.location.hash.replace('#', '');
  const match = path.match(/(?:campus\/buildings|rooms|facilities|faculty|events)\/(.+)/);
  if (!match) return false;
  const location = findLocation(match[1]);
  showView('search');
  $('#directorySearch').value = location.name;
  renderResults(location.name);
  return true;
}

document.addEventListener('click', event => {
  const nav = event.target.closest('[data-nav], [data-view]');
  if (nav) { event.preventDefault(); showView(nav.dataset.nav || nav.dataset.view); }
  const searchTrigger = event.target.closest('[data-search]');
  if (searchTrigger) {
    const query = searchTrigger.dataset.search;
    showView('search');
    $('#directorySearch').value = query;
    renderResults(query);
  }
  const routeTrigger = event.target.closest('[data-action="navigate"], .result-action');
  if (routeTrigger) openRoute(routeTrigger.dataset.target || 'selected location');
  const detailTrigger = event.target.closest('[data-action="details"]');
  if (detailTrigger) { showView('search'); $('#directorySearch').value = detailTrigger.dataset.target; renderResults(detailTrigger.dataset.target); }
  const building = event.target.closest('.building');
  if (building) selectBuilding(building.dataset.building);
  const filter = event.target.closest('.filter');
  if (filter) { state.filter = filter.dataset.filter; $$('.filter').forEach(item => item.classList.toggle('active', item === filter)); renderResults(); }
  const lang = event.target.closest('.lang');
  if (lang) setLanguage(lang.dataset.lang);
  const role = event.target.closest('.role-option');
  if (role) {
    state.role = role.dataset.role;
    closeRoleModal();
    toast(`${role.querySelector('strong').textContent} demo view selected`);
    if (state.role === 'visitor') showView('events');
    if (state.role === 'department-admin' || state.role === 'super-admin') showView('admin');
  }
  const editButton = event.target.closest('.row-action');
  if (editButton) {
    const row = editButton.closest('tr');
    const record = locations.find(location => row?.textContent.includes(location.name));
    if (record) {
      const updatedName = prompt('Update display name', record.name);
      if (updatedName?.trim()) { record.name = updatedName.trim(); persistLocation(record); renderResults(); renderBuildings(); }
    } else toast('This demo record is read-only');
  }
  const qrButton = event.target.closest('[data-action="qr"]');
  if (qrButton) fetchQrLink(findLocation(qrButton.dataset.target).id).then(link => {
    const copy = navigator.clipboard?.writeText(link);
    if (copy) copy.then(() => toast('Safe location link copied')).catch(() => toast(link));
    else toast(link);
  });
});

$('#searchSubmit').addEventListener('click', () => { showView('search'); $('#directorySearch').value = $('#globalSearch').value; renderResults($('#globalSearch').value); });
$('#globalSearch').addEventListener('keydown', event => { if (event.key === 'Enter') $('#searchSubmit').click(); });
$('#directorySearch').addEventListener('input', event => renderResults(event.target.value));
$('#clearSearch').addEventListener('click', () => { $('#directorySearch').value = ''; renderResults(''); $('#directorySearch').focus(); });
$('#closeModal').addEventListener('click', closeRoute);
$('#routeModal').addEventListener('click', event => { if (event.target.id === 'routeModal') closeRoute(); });
$('#startRoute').addEventListener('click', () => { closeRoute(); toast('Navigation started · follow the blue route'); });
$('#contrastButton').addEventListener('click', () => { document.body.classList.toggle('high-contrast'); toast(document.body.classList.contains('high-contrast') ? 'High contrast enabled' : 'High contrast disabled'); });
$('#settingsContrast').addEventListener('change', event => document.body.classList.toggle('high-contrast', event.target.checked));
$('#reducedMotion').addEventListener('change', event => document.body.classList.toggle('reduced-motion', event.target.checked));
$('#settingsAccessibility').addEventListener('change', event => { state.accessible = event.target.checked; $('#accessibilityToggle').checked = event.target.checked; toast(event.target.checked ? 'Accessible route preference saved' : 'Standard route preference saved'); });
$('#accessibilityToggle').addEventListener('change', event => { state.accessible = event.target.checked; $('#settingsAccessibility').checked = event.target.checked; toast(event.target.checked ? 'Accessible routes preferred' : 'Standard routes preferred'); });
$('#lowBandwidthToggle').addEventListener('change', event => toggleLowBandwidth(event.target.checked));
$('#view2d').addEventListener('click', () => toggleLowBandwidth(true));
$('#view3d').addEventListener('click', () => toggleLowBandwidth(false));
$('#return3d').addEventListener('click', () => toggleLowBandwidth(false));
$('#languageButton').addEventListener('click', () => showView('settings'));
$('#profileButton').addEventListener('click', openRoleModal);
$('#closeRoleModal').addEventListener('click', closeRoleModal);
$('#roleModal').addEventListener('click', event => { if (event.target.id === 'roleModal') closeRoleModal(); });

document.addEventListener('keydown', event => {
  if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); showView('search'); $('#directorySearch').focus(); }
  if (event.key === 'Escape') closeRoute();
});

window.addEventListener('hashchange', () => {
  if (!handleDeepLink()) {
    const view = window.location.hash.replace('#', '');
    if (document.getElementById(view)) showView(view);
  }
});

renderResults();
renderBuildings();
if ('serviceWorker' in navigator && location.protocol !== 'file:') navigator.serviceWorker.register('./sw.js').catch(() => {});
const initialView = window.location.hash.replace('#', '');
if (!handleDeepLink()) showView(initialView && document.getElementById(initialView) ? initialView : 'home');
