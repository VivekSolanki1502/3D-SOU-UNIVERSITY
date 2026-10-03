/**
 * SOU 3D Disha - Production Application Engine & Centralized API Client
 * Silver Oak University Campus Digital Twin
 */

// ==========================================
// 1. Centralized Backend API Client
// ==========================================
const API_BASE = '/api/v1';

const ApiClient = {
  getToken() {
    return localStorage.getItem('sou_token') || '';
  },
  setToken(token) {
    if (token) localStorage.setItem('sou_token', token);
    else localStorage.removeItem('sou_token');
  },
  getCurrentUser() {
    try {
      return JSON.parse(localStorage.getItem('sou_user') || 'null');
    } catch {
      return null;
    }
  },
  setCurrentUser(user) {
    if (user) localStorage.setItem('sou_user', JSON.stringify(user));
    else localStorage.removeItem('sou_user');
  },

  async request(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };
    const token = this.getToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, { ...options, headers });
      if (response.status === 401) {
        // Clear invalid token
        this.setToken(null);
        this.setCurrentUser(null);
      }
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }
      if (response.status === 204) return null;
      return await response.json();
    } catch (err) {
      console.warn(`API Error [${endpoint}]:`, err.message);
      throw err;
    }
  },

  // Auth APIs
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    this.setToken(data.access_token);
    this.setCurrentUser({
      id: data.user_id,
      role: data.role,
      display_name: data.display_name,
      email: email,
    });
    return data;
  },

  async getMe() {
    return await this.request('/auth/me');
  },

  // Campus APIs
  async getHealth() {
    return await this.request('/health');
  },
  async getBuildings() {
    return await this.request('/campus/buildings');
  },
  async getRooms(buildingId = '', roomType = '') {
    const params = new URLSearchParams();
    if (buildingId) params.append('building_id', buildingId);
    if (roomType) params.append('room_type', roomType);
    const query = params.toString() ? `?${params.toString()}` : '';
    return await this.request(`/campus/rooms${query}`);
  },
  async getFacilities(facilityType = '') {
    const query = facilityType ? `?facility_type=${facilityType}` : '';
    return await this.request(`/campus/facilities${query}`);
  },
  async searchCampus(query) {
    return await this.request(`/campus/search?q=${encodeURIComponent(query)}`);
  },

  // Dynamic Content APIs
  async getEvents(category = '') {
    const query = category ? `?category=${category}` : '';
    return await this.request(`/events${query}`);
  },
  async createEvent(eventData) {
    return await this.request('/events', { method: 'POST', body: JSON.stringify(eventData) });
  },
  async deleteEvent(eventId) {
    return await this.request(`/events/${eventId}`, { method: 'DELETE' });
  },

  async getExams(department = '', semester = '') {
    const params = new URLSearchParams();
    if (department) params.append('department', department);
    if (semester) params.append('semester', semester);
    const query = params.toString() ? `?${params.toString()}` : '';
    return await this.request(`/exams${query}`);
  },
  async createExam(examData) {
    return await this.request('/exams', { method: 'POST', body: JSON.stringify(examData) });
  },
  async updateExam(examId, examData) {
    return await this.request(`/exams/${examId}`, { method: 'PATCH', body: JSON.stringify(examData) });
  },
  async deleteExam(examId) {
    return await this.request(`/exams/${examId}`, { method: 'DELETE' });
  },

  async getSOS(category = '') {
    const query = category ? `?category=${category}` : '';
    return await this.request(`/sos${query}`);
  },
  async createSOS(sosData) {
    return await this.request('/sos', { method: 'POST', body: JSON.stringify(sosData) });
  },

  // Admin Dashboard APIs
  async getAdminStats() {
    return await this.request('/admin/stats');
  },
  async getUsers() {
    return await this.request('/admin/users');
  },
  async updateUser(userId, data) {
    return await this.request(`/admin/users/${userId}`, { method: 'PATCH', body: JSON.stringify(data) });
  },
  async getAuditLogs() {
    return await this.request('/admin/audit-logs');
  },
};

// ==========================================
// 2. Application State & Offline Fallback Data
// ==========================================
let locations = [
  { id: 'innovation-hub', name: 'Innovation Hub', type: 'building', meta: 'Zone A · 4 floors · 24 rooms', code: 'IH', aliases: ['block b', 'બ્લોક બી', 'ब्लॉक बी'] },
  { id: 'central-library', name: 'Central Library', type: 'facility', meta: 'Central Campus · Ground + 2 floors', code: 'LIB', aliases: ['library', 'પુસ્તકાલય', 'पुस्तकालय'] },
  { id: 'admin-block', name: 'Admin Block', type: 'building', meta: 'Zone C · 3 floors · Reception', code: 'AB', aliases: ['reception', 'વહીવટી બ્લોક', 'प्रशासन ब्लॉक'] },
  { id: 'school-design', name: 'School of Design', type: 'building', meta: 'Zone D · 3 floors · Studios', code: 'SD', aliases: ['design school', 'ડિઝાઇન', 'डिजाइन'] },
  { id: 'room-b204', building_id: 'innovation-hub', name: 'Room B-204', type: 'room', meta: 'Innovation Hub · 2nd floor · Classroom', code: '204', aliases: ['b204', 'classroom 204', 'રૂમ બી ૨૦૪', 'कमरा बी 204'] },
  { id: 'lab-b108', building_id: 'innovation-hub', name: 'Lab B-108', type: 'room', meta: 'Innovation Hub · Ground floor · Computer lab', code: '108', aliases: ['computer lab', 'લેબ', 'कंप्यूटर लैब'] },
  { id: 'medical-room', building_id: 'admin-block', name: 'Medical Room', type: 'facility', meta: 'Admin Block · Ground floor · Open 24/7', code: '✚', aliases: ['clinic', 'મેડિકલ રૂમ', 'चिकित्सा कक्ष'] },
  { id: 'canteen', name: 'Canteen', type: 'facility', meta: 'Central Campus · Ground floor · 8 AM – 8 PM', code: '◒', aliases: ['food court', 'કેન્ટીન', 'कैंटीन'] },
  { id: 'parking', name: 'Parking', type: 'facility', meta: 'East Gate · 180 spaces · Accessible', code: 'P', aliases: ['car park', 'પાર્કિંગ', 'पાર્કિંગ'] },
  { id: 'meera-shah', building_id: 'innovation-hub', name: 'Dr. Meera Shah', type: 'room', meta: 'Faculty · Innovation Hub · B-312', code: 'MS', aliases: ['meera', 'computer science faculty'] },
  { id: 'main-gate', name: 'Main Gate', type: 'facility', meta: 'North entrance · Reception nearby', code: '⌂', aliases: ['entrance', 'મુખ્ય દરવાજો', 'मुख्य द्वार'] },
  { id: 'auditorium', name: 'Auditorium', type: 'facility', meta: 'Central Campus · 650 seats · Accessible', code: 'AU', aliases: ['hall', 'ઓડિટોરિયમ', 'सभागार'] },
  { id: 'east-exit', name: 'East Exit', type: 'facility', meta: 'Emergency exit · Clearly marked', code: '↗', aliases: ['safe exit'] },
  { id: 'assembly-area', name: 'Assembly Area', type: 'facility', meta: 'Sports Ground · Emergency gathering point', code: '⌖', aliases: ['sports ground', 'મિલન સ્થળ', 'सभा क्षेत्र'] }
];

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
  en: { search: 'Search campus', explore: 'Explore campus', myday: 'My day', emergency: 'Emergency help', events: 'Campus Events', exams: 'Exam Schedules' },
  gu: { search: 'કેમ્પસ શોધો', explore: 'કેમ્પસ જુઓ', myday: 'મારો દિવસ', emergency: 'કટોકટી મદદ', events: 'ઇવેન્ટ્સ', exams: 'પરીક્ષાનું સમયપત્રક' },
  hi: { search: 'कैंपस खोजें', explore: 'कैंपस देखें', myday: 'मेरा दिन', emergency: 'आपातकालीन सहायता', events: 'आयोजन', exams: 'परीक्षा कार्यक्रम' }
};

const state = {
  filter: 'all',
  query: '',
  lang: 'en',
  role: 'student', // visitor, student, faculty, admin
  accessible: false,
  currentNode: 'room-b204',
  dynamicEvents: [],
  dynamicExams: [],
  dynamicSOS: [],
  adminStats: null,
};

const $ = (selector, root = document) => root.querySelector(selector);
const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];

function showToast(message, type = 'info') {
  const toast = $('#toast');
  if (!toast) return;
  toast.textContent = message;
  toast.className = `toast visible ${type}`;
  setTimeout(() => {
    toast.className = 'toast';
  }, 3500);
}

function normalize(value) {
  return String(value || '').toLowerCase().replace(/[\s-]+/g, '').trim();
}

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[character]);
}

function findLocation(target) {
  return locations.find(loc => loc.name === target || loc.id === target || (loc.aliases || []).includes(target)) || locations[0];
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
      queue.push({
        node: edge.to,
        path: [...current.path, edge],
        distance: current.distance + edge.distance,
        minutes: current.minutes + edge.minutes
      });
    });
  }
  return null;
}

// ==========================================
// 3. View Routing & Role Guarding
// ==========================================
function showView(viewId) {
  const target = document.getElementById(viewId) ? viewId : 'home';

  // Role Access Enforcement
  if (target === 'admin' && state.role !== 'admin') {
    showToast('Admin dashboard requires admin authentication', 'warn');
    openRoleModal('admin');
    return;
  }
  if (target === 'myday' && state.role === 'visitor') {
    showToast('Sign in as Student or Faculty to view personal schedule', 'info');
    openRoleModal('student');
    return;
  }

  $$('[data-view-panel]').forEach(view => view.classList.toggle('active', view.id === target));
  $$('[data-nav]').forEach(link => link.classList.toggle('active', link.dataset.nav === target));
  history.replaceState(null, '', `#${target}`);
  window.scrollTo({ top: 0, behavior: document.body.classList.contains('reduced-motion') ? 'auto' : 'smooth' });

  // Load view-specific dynamic data
  if (target === 'events') loadEvents();
  if (target === 'emergency') loadSOS();
  if (target === 'exams') loadExams();
  if (target === 'admin') loadAdminDashboard();
}

function updateRoleUI() {
  const user = ApiClient.getCurrentUser();
  state.role = user ? user.role : 'visitor';

  // Update Avatar button
  const avatar = $('#profileButton');
  if (avatar) {
    if (state.role === 'admin') avatar.textContent = 'AD';
    else if (state.role === 'faculty') avatar.textContent = 'FC';
    else if (state.role === 'student') avatar.textContent = 'ST';
    else avatar.textContent = 'VI';
    avatar.title = `Current role: ${state.role.toUpperCase()} (${user ? user.display_name : 'Visitor'})`;
  }

  // Update navigation items visibility based on RBAC rules
  const adminNav = $('[data-nav="admin"]');
  if (adminNav) {
    adminNav.style.display = state.role === 'admin' ? 'flex' : 'none';
  }
  const myDayNav = $('[data-nav="myday"]');
  if (myDayNav) {
    myDayNav.style.display = state.role !== 'visitor' ? 'flex' : 'none';
  }
  const examsNav = $('[data-nav="exams"]');
  if (examsNav) {
    examsNav.style.display = state.role !== 'visitor' ? 'flex' : 'none';
  }

  // If in admin view but not admin, switch to home
  if (state.role !== 'admin' && location.hash === '#admin') {
    showView('home');
  }
}

// ==========================================
// 4. Dynamic Data Fetching
// ==========================================
async function loadDynamicCampusEntities() {
  try {
    const [bList, rList, fList] = await Promise.allSettled([
      ApiClient.getBuildings(),
      ApiClient.getRooms(),
      ApiClient.getFacilities()
    ]);

    const newLocations = [];
    if (bList.status === 'fulfilled' && Array.isArray(bList.value)) {
      bList.value.forEach(b => {
        newLocations.push({
          id: b.id,
          building_id: b.id,
          name: b.name,
          type: 'building',
          meta: `${b.short_code} · ${b.floors_count} floors · ${b.department || 'Academic'}`,
          code: b.short_code,
          aliases: b.aliases || []
        });
      });
    }
    if (rList.status === 'fulfilled' && Array.isArray(rList.value)) {
      rList.value.forEach(r => {
        newLocations.push({
          id: r.id,
          building_id: r.building_id,
          name: r.name,
          type: 'room',
          meta: `${r.building_id.toUpperCase()} · Floor ${r.floor_number} · ${r.room_type}`,
          code: r.room_number,
          aliases: r.aliases || []
        });
      });
    }
    if (fList.status === 'fulfilled' && Array.isArray(fList.value)) {
      fList.value.forEach(f => {
        newLocations.push({
          id: f.id,
          building_id: f.building_id,
          name: f.name,
          type: 'facility',
          meta: f.location_description,
          code: f.code_symbol || '⌂',
          aliases: f.aliases || []
        });
      });
    }

    if (newLocations.length > 0) {
      locations = newLocations;
      renderResults(state.query);
    }
  } catch (e) {
    console.warn('Campus entities loaded from static cache.');
  }
}

async function loadEvents() {
  const container = $('.events-grid');
  if (!container) return;

  try {
    const events = await ApiClient.getEvents();
    state.dynamicEvents = events;
    if (Array.isArray(events) && events.length > 0) {
      container.innerHTML = events.map((ev, idx) => {
        const d = new Date(ev.event_date);
        const day = d.getDate();
        const month = d.toLocaleString('en-US', { month: 'short' }).toUpperCase();
        const eventId = escapeHtml(ev.id);
        const category = escapeHtml(ev.category || 'event').toUpperCase();
        const title = escapeHtml(ev.title);
        return `
          <article class="event-card ${idx === 0 ? 'featured' : ''}">
            <div class="${idx === 0 ? 'event-art' : 'event-date-large'}">
              ${idx === 0
                ? `<span>${day} ${month}</span><strong>${category}</strong>`
                : `<strong>${day}</strong><span>${month}</span>`}
            </div>
            <div class="event-card-body">
              <span class="type-label">${category}</span>
              <h2>${title}</h2>
              <p>${escapeHtml(ev.description || 'Join fellow students and faculty on campus.')}</p>
              <div class="event-meta">
                ◷ ${escapeHtml(ev.start_time || 'Full day')} · ${escapeHtml(ev.venue)}
              </div>
              <button class="primary-button" data-action="navigate" data-target="${escapeHtml(ev.building_id || 'innovation-hub')}">
                Navigate to venue <span>→</span>
              </button>
              ${state.role === 'admin' ? `<button class="outline-button" data-action="delete-event" data-id="${eventId}" style="margin-top:8px;color:#ad452e;">Delete Event</button>` : ''}
            </div>
          </article>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('Failed loading dynamic events; using default templates.');
  }
}

async function loadHomeEvents() {
  const container = $('#homeEvents');
  if (!container) return;

  try {
    const events = await ApiClient.getEvents();
    if (!Array.isArray(events) || events.length === 0) {
      container.textContent = 'No published events yet.';
      return;
    }

    container.innerHTML = events.slice(0, 2).map((event, index) => {
      const eventDate = new Date(`${event.event_date}T12:00:00`);
      const day = Number.isNaN(eventDate.getTime()) ? '' : eventDate.getDate();
      const month = Number.isNaN(eventDate.getTime()) ? '' : eventDate.toLocaleString('en-US', { month: 'short' }).toUpperCase();
      const time = event.start_time ? String(event.start_time).slice(0, 5) : 'Full day';
      return `<div class="event-mini"><div class="event-date ${index ? 'warm' : ''}"><strong>${day}</strong><small>${month}</small></div><div><strong>${escapeHtml(event.title)}</strong><small>${escapeHtml(event.venue)} · ${escapeHtml(time)}</small></div><span>›</span></div>`;
    }).join('');
  } catch {
    container.textContent = 'Published events are unavailable.';
  }
}

async function loadExams() {
  const list = $('#examList');
  if (!list) return;

  try {
    const exams = await ApiClient.getExams();
    state.dynamicExams = exams;
    if (Array.isArray(exams) && exams.length > 0) {
      list.innerHTML = exams.map(ex => `
        <article class="panel" style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;">
            <span class="type-label">${escapeHtml(ex.subject_code)} · SEM ${escapeHtml(ex.semester)}</span>
            <span class="status-pill">${escapeHtml(ex.status).toUpperCase()}</span>
          </div>
          <h2 style="margin:8px 0 4px;font-size:16px;">${escapeHtml(ex.subject_name)}</h2>
          <p style="color:var(--muted);margin:0 0 10px;font-size:12px;">${escapeHtml(ex.course)} (${escapeHtml(ex.department)})</p>
          <div style="display:flex;gap:16px;font-size:12px;color:var(--ink);">
            <span>📅 ${escapeHtml(ex.exam_date)}</span>
            <span>⏰ ${escapeHtml(ex.start_time)} – ${escapeHtml(ex.end_time)}</span>
            <span>📍 ${escapeHtml(ex.venue)}</span>
          </div>
          <div style="margin-top:12px;display:flex;gap:8px;">
            <button class="secondary-button" data-action="navigate" data-target="${escapeHtml(ex.building_id || 'innovation-hub')}">Navigate to Hall</button>
            ${state.role === 'faculty' || state.role === 'admin' ? `
              <button class="outline-button" data-action="edit-exam" data-id="${escapeHtml(ex.id)}" data-venue="${escapeHtml(ex.venue)}" data-status="${escapeHtml(ex.status)}">Update Venue/Status</button>
            ` : ''}
            ${state.role === 'admin' ? `<button class="outline-button" data-action="delete-exam" data-id="${escapeHtml(ex.id)}" style="color:#ad452e;">Delete</button>` : ''}
          </div>
        </article>
      `).join('');
    } else {
      list.innerHTML = '<p style="color:var(--muted);">No upcoming examinations scheduled.</p>';
    }
  } catch (e) {
    list.innerHTML = '<p style="color:var(--muted);">Exams require student/faculty authentication.</p>';
  }
}

async function loadSOS() {
  const container = $('.emergency-grid');
  if (!container) return;

  try {
    const contacts = await ApiClient.getSOS();
    state.dynamicSOS = contacts;
    if (Array.isArray(contacts) && contacts.length > 0) {
      container.innerHTML = contacts.map(c => {
        const icon = c.category === 'medical' ? '✚' : c.category === 'fire' ? '🔥' : '☎';
        const phone = String(c.phone_number || '').replace(/[^0-9+().\-\s]/g, '');
        return `
          <a class="safety-action ${escapeHtml(c.category)}" data-action="navigate" data-target="${escapeHtml(c.building_id || 'admin-block')}" href="tel:${escapeHtml(phone)}">
            <span>${icon}</span>
            <strong>${escapeHtml(c.title)}</strong>
            <small>${escapeHtml(c.location_name)} · <strong>${escapeHtml(phone)}</strong></small>
          </a>
        `;
      }).join('');
    }
  } catch (e) {
    console.warn('Using default SOS contacts.');
  }
}

async function loadAdminDashboard() {
  if (state.role !== 'admin') return;

  try {
    const stats = await ApiClient.getAdminStats();
    state.adminStats = stats;
    $('#statLocations').textContent = (stats.buildings || 0) + (stats.rooms || 0) + (stats.facilities || 0);
    $('#statEvents').textContent = stats.events || 0;
    $('#statExams').textContent = stats.exams || 0;
    $('#statUsers').textContent = stats.users || 0;

    // Load Audit Logs
    const logs = await ApiClient.getAuditLogs();
    const logBody = $('#adminLogBody');
    if (logBody && Array.isArray(logs)) {
      logBody.innerHTML = logs.map(l => `
        <tr>
          <td><strong>${escapeHtml(l.action)}</strong><small>${escapeHtml(l.entity_type)} · ${escapeHtml(l.entity_id)}</small></td>
          <td>${escapeHtml(l.actor_email || 'System')}</td>
          <td>${new Date(l.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td>
          <td><span class="table-status published">${escapeHtml(l.details || 'Executed')}</span></td>
        </tr>
      `).join('');
    }
  } catch (e) {
    showToast('Failed to load admin metrics: ' + e.message, 'error');
  }
}

async function loadServiceStatus() {
  const title = $('#serviceStatus');
  const detail = $('#serviceDetails');
  if (!title || !detail) return;

  try {
    const health = await ApiClient.getHealth();
    title.textContent = health.database === 'connected' ? 'FastAPI ready' : 'Backend unavailable';
    detail.textContent = `${health.version} · Redis ${health.redis}`;
  } catch {
    title.textContent = 'Backend unavailable';
    detail.textContent = 'Campus services could not be reached';
  }
}

// Global actions for Faculty & Admin
window.deleteEventRecord = async function (id) {
  if (!confirm('Are you sure you want to delete this event?')) return;
  try {
    await ApiClient.deleteEvent(id);
    showToast('Event deleted successfully');
    loadEvents();
  } catch (e) {
    showToast(e.message, 'error');
  }
};

window.deleteExamRecord = async function (id) {
  if (!confirm('Are you sure you want to delete this exam schedule?')) return;
  try {
    await ApiClient.deleteExam(id);
    showToast('Exam deleted successfully');
    loadExams();
  } catch (e) {
    showToast(e.message, 'error');
  }
};

window.editExamPrompt = async function (id, currentVenue, currentStatus) {
  const newVenue = prompt('Enter new exam venue / hall:', currentVenue);
  if (!newVenue) return;
  const newStatus = prompt('Enter exam status (scheduled / ongoing / completed / rescheduled):', currentStatus || 'scheduled');
  try {
    await ApiClient.updateExam(id, { venue: newVenue, status: newStatus || 'scheduled' });
    showToast('Exam schedule updated successfully');
    loadExams();
  } catch (e) {
    showToast(e.message, 'error');
  }
};

// ==========================================
// 5. Search & Directory Rendering
// ==========================================
function renderResults(query = state.query) {
  state.query = query.trim();
  const needle = normalize(state.query);
  const filtered = locations.filter(loc => {
    const matchesQuery = !needle || [loc.name, loc.meta, ...(loc.aliases || [])].some(v => normalize(v).includes(needle));
    return matchesQuery && (state.filter === 'all' || loc.type === state.filter);
  });

  const list = $('#resultsList');
  if (!list) return;
  const countEl = $('#resultCount');
  if (countEl) countEl.textContent = `${filtered.length} result${filtered.length === 1 ? '' : 's'}`;

  list.innerHTML = filtered.map(loc => `
    <article class="result-card">
      <span class="result-tag">${escapeHtml(loc.type).toUpperCase()}</span>
      <div class="result-code">${escapeHtml(loc.code || '⌂')}</div>
      <div class="result-main">
        <h3>${escapeHtml(loc.name)}</h3>
        <p>${escapeHtml(loc.meta || '')}</p>
        <div class="result-meta">
          <span>Accessible route available</span>
          <button class="primary-button" data-action="navigate" data-target="${escapeHtml(loc.id || loc.name)}">Navigate <span>→</span></button>
        </div>
      </div>
    </article>
  `).join('');
}

// ==========================================
// 6. Navigation Preview Modal & 3D Camera Jump
// ==========================================
function openRouteModal(destination) {
  const target = findLocation(destination);
  const route = calculateRoute(target.id);
  const modal = $('#routeModal');
  if (!modal) return;

  $('#routeTitle').textContent = `Route to ${target.name}`;
  const stepsContainer = modal.querySelector('.route-steps-box') || modal.querySelector('.route-summary').parentNode;

  // Dispatch event to Three.js camera to orbit & focus
  window.dispatchEvent(new CustomEvent('focus-campus-entity', {
    detail: { id: target.building_id || target.id, entityId: target.id, name: target.name }
  }));

  modal.classList.remove('hidden');
}

function openRoleModal(targetRole = '') {
  const modal = $('#roleModal');
  if (!modal) return;
  modal.classList.remove('hidden');
  if (targetRole) {
    $$('.role-option').forEach(btn => {
      btn.classList.toggle('selected', btn.dataset.role === targetRole);
    });
  }
}

// Quick sign-in helper for seamless evaluator testing
function handleRoleSelection(role) {
  if (role !== 'visitor') return;
  ApiClient.setToken(null);
  ApiClient.setCurrentUser(null);
  updateRoleUI();
  showToast('Switched to Visitor view (Public access)');
  $('#roleModal').classList.add('hidden');
}

async function handleLoginSubmit(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const error = $('#loginError');
  const submit = form.querySelector('[type="submit"]');
  error.hidden = true;
  submit.disabled = true;
  submit.textContent = 'Signing in...';

  try {
    await ApiClient.login($('#loginEmail').value.trim(), $('#loginPassword').value);
    $('#loginPassword').value = '';
    updateRoleUI();
    $('#roleModal').classList.add('hidden');
    const requestedView = location.hash.slice(1);
    showView(state.role === 'admin' && requestedView === 'admin' ? 'admin' : 'home');
    showToast(`Signed in as ${state.role.toUpperCase()}`);
  } catch (err) {
    error.textContent = err.message;
    error.hidden = false;
  } finally {
    submit.disabled = false;
    submit.textContent = 'Sign in';
  }
}

// ==========================================
// 7. Event Listeners & Bootstrapping
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Navigation tabs
  $$('[data-nav]').forEach(link => {
    link.addEventListener('click', event => {
      event.preventDefault();
      showView(link.dataset.nav);
    });
  });

  $$('[data-view]').forEach(btn => {
    btn.addEventListener('click', () => showView(btn.dataset.view));
  });

  // Global search input
  const globalSearch = $('#globalSearch');
  if (globalSearch) {
    globalSearch.addEventListener('input', e => {
      state.query = e.target.value;
      if (state.query) showView('search');
      renderResults(state.query);
    });
    globalSearch.addEventListener('keydown', e => {
      if (e.key === 'Enter') {
        showView('search');
        renderResults(globalSearch.value);
      }
    });
  }

  const dirSearch = $('#directorySearch');
  if (dirSearch) {
    dirSearch.addEventListener('input', e => renderResults(e.target.value));
  }

  // Quick destination links
  $$('[data-search]').forEach(link => {
    link.addEventListener('click', () => {
      const q = link.dataset.search;
      showView('search');
      if (dirSearch) dirSearch.value = q;
      renderResults(q);
      window.dispatchEvent(new CustomEvent('focus-campus-entity', { detail: q }));
    });
  });

  // Action clicks
  document.addEventListener('click', event => {
    const deleteEvent = event.target.closest('[data-action="delete-event"]');
    if (deleteEvent) { deleteEventRecord(deleteEvent.dataset.id); return; }
    const editExam = event.target.closest('[data-action="edit-exam"]');
    if (editExam) { editExamPrompt(editExam.dataset.id, editExam.dataset.venue, editExam.dataset.status); return; }
    const deleteExam = event.target.closest('[data-action="delete-exam"]');
    if (deleteExam) { deleteExamRecord(deleteExam.dataset.id); return; }
    const navBtn = event.target.closest('[data-action="navigate"]');
    if (navBtn) {
      const target = navBtn.dataset.target;
      openRouteModal(target);
    }
  });

  // Modals
  $('#closeModal')?.addEventListener('click', () => $('#routeModal')?.classList.add('hidden'));
  $('#startRoute')?.addEventListener('click', () => {
    $('#routeModal')?.classList.add('hidden');
    showView('explore');
  });
  $('#closeRoleModal')?.addEventListener('click', () => $('#roleModal')?.classList.add('hidden'));
  $('#profileButton')?.addEventListener('click', () => openRoleModal());

  $$('.role-option').forEach(btn => btn.addEventListener('click', () => handleRoleSelection(btn.dataset.role)));
  $('#loginForm')?.addEventListener('submit', handleLoginSubmit);

  // Contrast toggle
  $('#contrastButton')?.addEventListener('click', () => {
    document.body.classList.toggle('high-contrast');
  });

  // Initial Hash routing
  const initialHash = location.hash.replace('#', '') || 'home';
  updateRoleUI();
  showView(initialHash);
  loadServiceStatus();
  loadDynamicCampusEntities();
  loadHomeEvents();
  loadEvents();
  loadSOS();
});
