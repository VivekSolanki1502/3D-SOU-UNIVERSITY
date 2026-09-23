export class OrbitControls {
  constructor(camera, domElement) {
    this.camera = camera;
    this.domElement = domElement;
    this.target = camera.position.clone().set(0, 1.5, 0);
    this.enableDamping = true;
    this.dampingFactor = 0.08;
    this.minDistance = 7;
    this.maxDistance = 32;
    this.maxPolarAngle = Math.PI / 2.08;
    this._state = 'none';
    this._pointer = { x: 0, y: 0 };
    this._pointers = new Map();
    this._lastPinch = 0;
    this._spherical = { theta: 0.7, phi: 0.78, radius: 25 };
    this._desired = { ...this._spherical };
    this._syncFromCamera();
    domElement.style.touchAction = 'none';
    domElement.addEventListener('pointerdown', event => this._onPointerDown(event));
    domElement.addEventListener('pointermove', event => this._onPointerMove(event));
    domElement.addEventListener('pointerup', event => this._onPointerUp(event));
    domElement.addEventListener('pointercancel', event => this._onPointerUp(event));
    domElement.addEventListener('wheel', event => { event.preventDefault(); this._desired.radius = this._clamp(this._desired.radius * (1 + event.deltaY * 0.001), this.minDistance, this.maxDistance); }, { passive: false });
  }
  _clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
  _syncFromCamera() {
    const offset = this.camera.position.clone().sub(this.target);
    this._spherical.radius = offset.length();
    this._spherical.theta = Math.atan2(offset.x, offset.z);
    this._spherical.phi = Math.acos(this._clamp(offset.y / this._spherical.radius, -1, 1));
    this._desired = { ...this._spherical };
  }
  _onPointerDown(event) {
    this.domElement.setPointerCapture(event.pointerId);
    this._pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    this._pointer = { x: event.clientX, y: event.clientY };
    this._state = event.pointerType === 'touch' ? 'touch' : (event.button === 2 ? 'pan' : 'rotate');
  }
  _onPointerMove(event) {
    if (this._state === 'none') return;
    if (this._pointers.has(event.pointerId)) this._pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (this._state === 'touch' && this._pointers.size > 1) {
      const points = [...this._pointers.values()];
      const distance = Math.hypot(points[0].x - points[1].x, points[0].y - points[1].y);
      if (this._lastPinch) this._desired.radius = this._clamp(this._desired.radius * this._lastPinch / Math.max(distance, 1), this.minDistance, this.maxDistance);
      this._lastPinch = distance;
      this._pointer = { x: event.clientX, y: event.clientY };
      return;
    }
    const dx = event.clientX - this._pointer.x;
    const dy = event.clientY - this._pointer.y;
    this._pointer = { x: event.clientX, y: event.clientY };
    if (this._state === 'rotate' || this._state === 'touch') {
      this._desired.theta -= dx * 0.008;
      this._desired.phi = this._clamp(this._desired.phi + dy * 0.008, 0.12, this.maxPolarAngle);
    } else if (this._state === 'pan') {
      const distance = this._desired.radius * 0.0015;
      this.target.x -= dx * distance;
      this.target.z += dy * distance;
    }
  }
  _onPointerUp(event) {
    this._pointers.delete(event.pointerId);
    if (this._pointers.size < 2) this._lastPinch = 0;
    if (this.domElement.hasPointerCapture(event.pointerId)) this.domElement.releasePointerCapture(event.pointerId);
    this._state = 'none';
  }
  update() {
    const easing = this.enableDamping ? this.dampingFactor : 1;
    this._spherical.theta += (this._desired.theta - this._spherical.theta) * easing;
    this._spherical.phi += (this._desired.phi - this._spherical.phi) * easing;
    this._spherical.radius += (this._desired.radius - this._spherical.radius) * easing;
    const sinPhi = Math.sin(this._spherical.phi);
    this.camera.position.set(
      this.target.x + this._spherical.radius * sinPhi * Math.sin(this._spherical.theta),
      this.target.y + this._spherical.radius * Math.cos(this._spherical.phi),
      this.target.z + this._spherical.radius * sinPhi * Math.cos(this._spherical.theta)
    );
    this.camera.lookAt(this.target);
  }
  dispose() { this.domElement.replaceWith(this.domElement.cloneNode(true)); }
}
