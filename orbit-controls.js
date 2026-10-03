export class OrbitControls {
  constructor(camera, domElement) {
    this.camera = camera;
    this.domElement = domElement;
    this.target = camera.position.clone().set(0, 1.5, 0);
    this.enableDamping = true;
    this.dampingFactor = 0.08;
    this.minDistance = 7;
    this.maxDistance = 35;
    this.maxPolarAngle = Math.PI / 2.08;
    this.minPolarAngle = 0.1;
    this.autoRotate = false;
    this.autoRotateSpeed = 1.0;
    
    this._state = 'none';
    this._pointer = { x: 0, y: 0 };
    this._pointers = new Map();
    this._lastPinch = 0;
    this._spherical = { theta: 0.7, phi: 0.78, radius: 25 };
    this._desired = { ...this._spherical };
    
    this._syncFromCamera();
    domElement.style.touchAction = 'none';
    domElement.addEventListener('pointerdown', event => this._onPointerDown(event));
    window.addEventListener('pointermove', event => this._onPointerMove(event));
    window.addEventListener('pointerup', event => this._onPointerUp(event));
    window.addEventListener('pointercancel', event => this._onPointerUp(event));
    domElement.addEventListener('wheel', event => {
      event.preventDefault();
      this._desired.radius = this._clamp(this._desired.radius * (1 + event.deltaY * 0.001), this.minDistance, this.maxDistance);
    }, { passive: false });
  }

  _clamp(value, min, max) {
    return Math.max(min, Math.min(max, value));
  }

  _syncFromCamera() {
    const offset = this.camera.position.clone().sub(this.target);
    const radius = offset.length();
    if (radius > 0.001) {
      this._spherical.radius = this._desired.radius = this._clamp(radius, this.minDistance, this.maxDistance);
      this._spherical.phi = this._desired.phi = Math.acos(this._clamp(offset.y / radius, -1, 1));
      this._spherical.theta = this._desired.theta = Math.atan2(offset.x, offset.z);
    }
  }

  _onPointerDown(event) {
    this._pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (this._pointers.size === 1) {
      this._state = 'rotate';
      this._pointer = { x: event.clientX, y: event.clientY };
    } else if (this._pointers.size === 2) {
      this._state = 'pinch';
      const pts = Array.from(this._pointers.values());
      this._lastPinch = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
    }
  }

  _onPointerMove(event) {
    if (!this._pointers.has(event.pointerId)) return;
    this._pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (this._state === 'rotate' && this._pointers.size === 1) {
      const dx = event.clientX - this._pointer.x;
      const dy = event.clientY - this._pointer.y;
      this._pointer = { x: event.clientX, y: event.clientY };
      this._desired.theta -= dx * 0.005;
      this._desired.phi = this._clamp(this._desired.phi - dy * 0.005, this.minPolarAngle, this.maxPolarAngle);
    } else if (this._state === 'pinch' && this._pointers.size === 2) {
      const pts = Array.from(this._pointers.values());
      const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
      if (this._lastPinch > 0) {
        const factor = this._lastPinch / (dist || 1);
        this._desired.radius = this._clamp(this._desired.radius * factor, this.minDistance, this.maxDistance);
      }
      this._lastPinch = dist;
    }
  }

  _onPointerUp(event) {
    this._pointers.delete(event.pointerId);
    if (this._pointers.size === 0) {
      this._state = 'none';
    } else if (this._pointers.size === 1) {
      this._state = 'rotate';
      const remaining = Array.from(this._pointers.values())[0];
      this._pointer = { x: remaining.x, y: remaining.y };
    }
  }

  update() {
    if (this.autoRotate) {
      this._desired.theta += 0.003 * this.autoRotateSpeed;
    }
    const factor = this.enableDamping ? this.dampingFactor : 1.0;
    this._spherical.theta += (this._desired.theta - this._spherical.theta) * factor;
    this._spherical.phi += (this._desired.phi - this._spherical.phi) * factor;
    this._spherical.radius += (this._desired.radius - this._spherical.radius) * factor;

    const sinPhi = Math.sin(this._spherical.phi);
    const x = this.target.x + this._spherical.radius * sinPhi * Math.sin(this._spherical.theta);
    const y = this.target.y + this._spherical.radius * Math.cos(this._spherical.phi);
    const z = this.target.z + this._spherical.radius * sinPhi * Math.cos(this._spherical.theta);

    this.camera.position.set(x, y, z);
    this.camera.lookAt(this.target);
  }
}
