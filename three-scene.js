import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import { OrbitControls } from './orbit-controls.js';

const host = document.querySelector('#campusScene');
if (host) {
  const canvas = document.createElement('canvas');
  canvas.id = 'threeCanvas';
  canvas.setAttribute('aria-label', 'Interactive 3D campus model');
  host.querySelectorAll('.ground-grid,.road,.water,.building,.tree,.map-pin').forEach(node => node.remove());
  host.prepend(canvas);

  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#081a33');
  scene.fog = new THREE.Fog('#081a33', 18, 42);

  const camera = new THREE.PerspectiveCamera(42, 1, 0.1, 100);
  camera.position.set(14, 13, 16);

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'high-performance' });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;

  const controls = new OrbitControls(camera, canvas);
  controls.enableDamping = true;
  controls.dampingFactor = 0.07;
  controls.minDistance = 7;
  controls.maxDistance = 35;
  controls.maxPolarAngle = Math.PI / 2.08;
  controls.target.set(0, 1.5, 0);

  const blueprint = new THREE.Color('#00e5ff');
  let buildings = [
    { id: 'innovation-hub', name: 'Innovation Hub', short: 'IH', x: -4.4, z: 1.2, w: 4.2, d: 3.1, h: 5.2, floors: 4, department: 'Computer Science & Engineering', faculty: 'Dr. Meera Shah' },
    { id: 'central-library', name: 'Central Library', short: 'LIB', x: 4.1, z: -2.3, w: 3.8, d: 3.2, h: 3.4, floors: 3, department: 'Learning Commons', faculty: 'Library Services' },
    { id: 'admin-block', name: 'Admin Block', short: 'AB', x: -5.1, z: -4.2, w: 3.2, d: 2.8, h: 2.8, floors: 2, department: 'Administration', faculty: 'Registrar Office' },
    { id: 'school-design', name: 'School of Design', short: 'SD', x: 3.6, z: 3.4, w: 4.4, d: 2.7, h: 4.1, floors: 3, department: 'Design', faculty: 'Prof. Rohan Patel' }
  ];

  const buildingGroups = [];
  const searchable = value => String(value || '').toLowerCase().replace(/[\s-]+/g, '');
  const escapeHtml = value => String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  })[character]);
  let hovered = null;
  let selected = null;
  let autoRotate = false;
  let focusAnimation = null;

  const panel = document.createElement('div');
  panel.className = 'blueprint-panel';
  panel.innerHTML = '<div class="blueprint-kicker">SOU / 3D DISHA DIGITAL TWIN</div><strong>CAMPUS NAVIGATOR</strong><input class="blueprint-search" type="search" placeholder="Search 3D buildings, labs..." aria-label="Search 3D campus" autocomplete="off"><div class="blueprint-hint">Drag to orbit · Scroll to zoom<br>Click a block for live details</div><div class="blueprint-results" aria-live="polite"></div><div class="blueprint-info" hidden></div><button class="blueprint-reset" type="button">Reset camera</button><label class="blueprint-toggle"><input type="checkbox"> Auto-rotate</label>';
  host.append(panel);

  const searchInput = panel.querySelector('.blueprint-search');
  const results = panel.querySelector('.blueprint-results');
  const info = panel.querySelector('.blueprint-info');

  const label = document.createElement('div');
  label.className = 'blueprint-hover-label';
  host.append(label);

  function addBuilding(data) {
    const group = new THREE.Group();
    const px = data.x ?? data.pos_x ?? 0;
    const pz = data.z ?? data.pos_z ?? 0;
    const bw = data.w ?? data.dim_w ?? 4.0;
    const bd = data.d ?? data.dim_d ?? 3.0;
    const bh = data.h ?? data.dim_h ?? 4.0;
    const floorsCount = data.floors ?? data.floors_count ?? 3;

    group.position.set(px, 0, pz);
    group.userData = {
      ...data,
      x: px,
      z: pz,
      w: bw,
      d: bd,
      h: bh,
      floors: floorsCount,
      short: data.short || data.short_code || data.name.slice(0, 3).toUpperCase(),
      faculty: data.faculty || data.faculty_lead || 'Faculty Office'
    };

    const geometry = new THREE.BoxGeometry(bw, bh, bd);
    const faces = new THREE.MeshBasicMaterial({ color: blueprint, transparent: true, opacity: 0.12, depthWrite: false, side: THREE.DoubleSide });
    const mesh = new THREE.Mesh(geometry, faces);
    mesh.position.y = bh / 2;
    mesh.userData = { building: group.userData };

    const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geometry), new THREE.LineBasicMaterial({ color: blueprint, transparent: true, opacity: 0.9 }));
    edges.position.y = bh / 2;
    edges.userData = { building: group.userData, edge: true };
    group.add(mesh, edges);

    for (let floor = 1; floor < floorsCount; floor += 1) {
      const y = (bh / floorsCount) * floor;
      const floorLine = new THREE.LineSegments(
        new THREE.EdgesGeometry(new THREE.BoxGeometry(bw * 0.99, 0.015, bd * 0.99)),
        new THREE.LineBasicMaterial({ color: '#4cf3ff', transparent: true, opacity: 0.42 })
      );
      floorLine.position.y = y;
      floorLine.userData = { building: group.userData, floorLine: true };
      group.add(floorLine);
    }

    scene.add(group);
    buildingGroups.push(group);
  }

  // Load campus buildings dynamically from FastAPI backend if available
  async function loadDynamicCampus() {
    try {
      const response = await fetch('/api/v1/campus/buildings');
      if (response.ok) {
        const dynamicList = await response.json();
        if (Array.isArray(dynamicList) && dynamicList.length > 0) {
          // Clear current buildings
          buildingGroups.forEach(g => scene.remove(g));
          buildingGroups.length = 0;
          buildings = dynamicList.map(b => ({
            id: b.id,
            name: b.name,
            short: b.short_code,
            x: b.pos_x,
            z: b.pos_z,
            w: b.dim_w,
            d: b.dim_d,
            h: b.dim_h,
            floors: b.floors_count,
            department: b.department || 'Academic Department',
            faculty: b.faculty_lead || 'Dean Office'
          }));
        }
      }
    } catch (e) {
      console.warn('Using local 3D building definitions (backend offline or standalone mode)');
    }
    buildings.forEach(addBuilding);
    updateVisibility('');
  }

  // Environment Setup
  const grid = new THREE.GridHelper(30, 30, '#11627b', '#0b354f');
  scene.add(grid);

  const axisMaterial = new THREE.LineBasicMaterial({ color: '#00e5ff', transparent: true, opacity: 0.8 });
  const axisGeometry = new THREE.BufferGeometry().setFromPoints([
    new THREE.Vector3(-15, 0.012, 0),
    new THREE.Vector3(15, 0.012, 0),
    new THREE.Vector3(0, 0.014, -15),
    new THREE.Vector3(0, 0.014, 15)
  ]);
  scene.add(new THREE.LineSegments(axisGeometry, axisMaterial));

  const ground = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.MeshBasicMaterial({ color: '#081a33', transparent: true, opacity: 0.7, depthWrite: false }));
  ground.rotation.x = -Math.PI / 2;
  scene.add(ground);

  function buildingFromObject(object) {
    let current = object;
    while (current && !current.userData.building) current = current.parent;
    return current?.userData.building || null;
  }

  function setHighlight(data, active) {
    const group = buildingGroups.find(item => item.userData.id === data?.id);
    if (!group) return;
    group.children.forEach(child => {
      const material = child.material;
      if (material.color) {
        material.color.set(active ? '#8cffff' : (child.userData.floorLine ? '#4cf3ff' : blueprint));
        material.opacity = active ? (child.userData.floorLine ? 0.9 : 1) : (child.userData.floorLine ? 0.42 : child.userData.edge ? 0.9 : 0.12);
      }
    });
  }

  function updateVisibility(query) {
    const needle = searchable(query.trim());
    buildingGroups.forEach(group => {
      const data = group.userData;
      const match = !needle || [data.name, data.department, data.faculty, data.short].some(value => searchable(value).includes(needle));
      group.children.forEach(child => {
        child.material.opacity = match ? (child.userData.floorLine ? 0.42 : child.userData.edge ? 0.9 : 0.12) : 0.025;
      });
    });
    const matches = buildings.filter(data => !needle || [data.name, data.department, data.faculty, data.short].some(value => searchable(value).includes(needle)));
    results.innerHTML = needle && matches.length ? matches.map(data => `<button type="button" data-building-id="${escapeHtml(data.id)}">${escapeHtml(data.short)} · ${escapeHtml(data.name)}</button>`).join('') : '';
  }

  function showInfo(data) {
    selected = data;
    info.hidden = false;
    info.innerHTML = `<strong>${escapeHtml(data.name)}</strong><span>${escapeHtml(data.department)}</span><small>${escapeHtml(data.floors)} floors · ${escapeHtml(data.faculty)}</small>`;
    window.dispatchEvent(new CustomEvent('campus-building-selected', { detail: { name: data.name, id: data.id } }));
  }

  function focusBuilding(data) {
    if (!data) return;
    const target = new THREE.Vector3(data.x, data.h * 0.38, data.z);
    const offset = new THREE.Vector3(8, 6, 9).normalize().multiplyScalar(Math.max(data.w, data.d) * 2.7 + 5);
    focusAnimation = {
      fromPosition: camera.position.clone(),
      fromTarget: controls.target.clone(),
      toPosition: target.clone().add(offset),
      toTarget: target,
      start: performance.now(),
      duration: 650
    };
    showInfo(data);
    buildingGroups.forEach(group => setHighlight(group.userData, group.userData.id === data.id));
  }

  function resetView() {
    focusAnimation = {
      fromPosition: camera.position.clone(),
      fromTarget: controls.target.clone(),
      toPosition: new THREE.Vector3(14, 13, 16),
      toTarget: new THREE.Vector3(0, 1.5, 0),
      start: performance.now(),
      duration: 650
    };
    selected = null;
    info.hidden = true;
    buildingGroups.forEach(group => setHighlight(group.userData, false));
  }

  function pick(event) {
    const rect = canvas.getBoundingClientRect();
    const pointer = new THREE.Vector2(((event.clientX - rect.left) / rect.width) * 2 - 1, -((event.clientY - rect.top) / rect.height) * 2 + 1);
    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(pointer, camera);
    return buildingFromObject(raycaster.intersectObjects(buildingGroups, true)[0]?.object);
  }

  canvas.addEventListener('pointermove', event => {
    const data = pick(event);
    if (data?.id !== hovered?.id) {
      if (hovered && hovered.id !== selected?.id) setHighlight(hovered, false);
      hovered = data;
      if (hovered && hovered.id !== selected?.id) setHighlight(hovered, true);
    }
    label.textContent = data ? `${data.name} · ${data.floors} floors` : '';
    label.classList.toggle('visible', Boolean(data));
  });

  canvas.addEventListener('pointerleave', () => {
    label.classList.remove('visible');
    if (hovered && hovered.id !== selected?.id) setHighlight(hovered, false);
    hovered = null;
  });

  canvas.addEventListener('click', event => {
    const data = pick(event);
    if (data) focusBuilding(data);
  });

  searchInput.addEventListener('input', event => updateVisibility(event.target.value));
  results.addEventListener('click', event => {
    const data = buildings.find(item => item.id === event.target.dataset.buildingId);
    if (data) focusBuilding(data);
  });

  panel.querySelector('.blueprint-reset').addEventListener('click', resetView);
  panel.querySelector('.blueprint-toggle input').addEventListener('change', event => {
    autoRotate = event.target.checked;
  });

  // Global event listener for search & route focus triggers
  window.addEventListener('focus-campus-entity', event => {
    const entityId = event.detail?.id || event.detail?.building_id || event.detail;
    const found = buildings.find(b => b.id === entityId || b.name.toLowerCase() === String(entityId).toLowerCase());
    if (found) {
      focusBuilding(found);
    }
  });

  host.querySelector('.scene-toolbar button[aria-label="Zoom out"]')?.addEventListener('click', () => { camera.position.multiplyScalar(1.12); });
  host.querySelector('.scene-toolbar button[aria-label="Zoom in"]')?.addEventListener('click', () => { camera.position.multiplyScalar(0.88); });
  host.querySelector('.scene-toolbar button[aria-label="Reset view"]')?.addEventListener('click', resetView);

  const resize = () => {
    const width = host.clientWidth || 1;
    const height = host.clientHeight || 1;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height, false);
  };
  window.addEventListener('resize', resize);
  if ('ResizeObserver' in window) new ResizeObserver(resize).observe(host);
  resize();

  loadDynamicCampus();

  const animate = time => {
    if (focusAnimation) {
      const progress = Math.min((time - focusAnimation.start) / focusAnimation.duration, 1);
      const eased = 1 - (1 - progress) ** 3;
      camera.position.lerpVectors(focusAnimation.fromPosition, focusAnimation.toPosition, eased);
      controls.target.lerpVectors(focusAnimation.fromTarget, focusAnimation.toTarget, eased);
      if (progress === 1) focusAnimation = null;
    }
    if (autoRotate && !focusAnimation) scene.rotation.y += 0.0018;
    controls.update();
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
  };
  requestAnimationFrame(animate);
}
