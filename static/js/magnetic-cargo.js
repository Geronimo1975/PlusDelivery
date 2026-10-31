/* PlusDelivery — Cargo magnetic (Three.js, varianta B)
 * Colete 3D pe categorii (food / pharma / heavy / urgent / special) care
 * plutesc si sunt atrase de cursor. Component reutilizabil: se monteaza pe
 * orice element cu atributul [data-cargo].
 *
 * Optiuni via data-*:
 *   data-cargo-count   numarul de colete (implicit 24)
 *   data-cargo-opacity opacitatea umpluturii, 0-1 (implicit 0.14)
 *
 * Degradare eleganta: fara WebGL -> ramane fundalul CSS; reduced-motion ->
 * cadru static fara bucla; pauza cand elementul nu e vizibil.
 */
(function () {
  "use strict";
  if (typeof THREE === "undefined") return;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var hasWebGL = (function () {
    try {
      var c = document.createElement("canvas");
      return !!(c.getContext("webgl") || c.getContext("experimental-webgl"));
    } catch (e) { return false; }
  })();
  if (!hasWebGL) return; // pastram fundalul CSS

  var CATS = [0xff8a3d, 0x39d5ff, 0x9aa7bd, 0xff4d5e, 0x2ad88f]; // food,pharma,heavy,urgent,special

  function mount(host) {
    var count = parseInt(host.getAttribute("data-cargo-count"), 10) || 24;
    var fillOpacity = parseFloat(host.getAttribute("data-cargo-opacity"));
    if (isNaN(fillOpacity)) fillOpacity = 0.14;

    var canvas = document.createElement("canvas");
    canvas.className = "cargo-canvas";
    canvas.setAttribute("aria-hidden", "true");
    host.insertBefore(canvas, host.firstChild);

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    var scene = new THREE.Scene();
    var cam = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
    cam.position.set(0, 0, 10);

    function size() {
      var w = host.clientWidth, h = host.clientHeight;
      renderer.setSize(w, h, false);
      cam.aspect = w / Math.max(1, h); cam.updateProjectionMatrix();
    }
    size();

    var boxes = [];
    for (var i = 0; i < count; i++) {
      var c = CATS[i % CATS.length];
      var s = 0.5 + Math.random() * 0.6;
      var g = new THREE.Group();
      g.add(new THREE.Mesh(new THREE.BoxGeometry(s, s, s),
        new THREE.MeshBasicMaterial({ color: c, transparent: true, opacity: fillOpacity })));
      g.add(new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(s, s, s)),
        new THREE.LineBasicMaterial({ color: c })));
      g.position.set((Math.random() - 0.5) * 11, (Math.random() - 0.5) * 7, (Math.random() - 0.5) * 5);
      g.userData = { home: g.position.clone(), rx: (Math.random() - 0.5) * 0.02, ry: (Math.random() - 0.5) * 0.02 };
      scene.add(g); boxes.push(g);
    }

    // Pointer -> tinta magnetica (coordonate relative la element).
    var target = new THREE.Vector3(0, 0, 2);
    var pointerInside = false;
    host.addEventListener("pointermove", function (e) {
      var b = host.getBoundingClientRect();
      var nx = ((e.clientX - b.left) / b.width) * 2 - 1;
      var ny = -(((e.clientY - b.top) / b.height) * 2 - 1);
      target.set(nx * 6, ny * 4, 2); pointerInside = true;
    });
    host.addEventListener("pointerleave", function () { pointerInside = false; });
    window.addEventListener("resize", size);

    function step() {
      for (var j = 0; j < boxes.length; j++) {
        var b = boxes[j];
        b.rotation.x += b.userData.rx; b.rotation.y += b.userData.ry;
        if (pointerInside) {
          var d = target.clone().sub(b.position); var dist = d.length();
          if (dist < 5) { b.position.add(d.multiplyScalar(0.015 * (1 - dist / 5))); }
          else { b.position.lerp(b.userData.home, 0.01); }
        } else {
          b.position.lerp(b.userData.home, 0.012);
        }
      }
      renderer.render(scene, cam);
    }

    if (reduceMotion) { step(); return; } // cadru static

    var running = true;
    function loop() { if (!running) return; step(); requestAnimationFrame(loop); }
    loop();

    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        var vis = entries[0].isIntersecting;
        if (vis && !running) { running = true; loop(); }
        else if (!vis) { running = false; }
      }, { threshold: 0.02 }).observe(host);
    }
  }

  var hosts = document.querySelectorAll("[data-cargo]");
  for (var k = 0; k < hosts.length; k++) mount(hosts[k]);
})();
