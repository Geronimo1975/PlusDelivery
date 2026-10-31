/* PlusDelivery — Hero 3D Hamburg (MapLibre GL)
 * Harta reala a Hamburgului cu rute active si colete in miscare live.
 * Degradare eleganta: pe mobil / fara WebGL / prefers-reduced-motion
 * ramane fundalul-gradient din CSS (nu initializam harta grea).
 */
(function () {
  "use strict";

  var el = document.getElementById("hbMap");
  if (!el || typeof maplibregl === "undefined") return;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var bigEnough = window.innerWidth >= 768;
  var hasWebGL = (function () {
    try {
      var c = document.createElement("canvas");
      return !!(c.getContext("webgl") || c.getContext("experimental-webgl"));
    } catch (e) { return false; }
  })();

  // Pe ecrane mici sau fara WebGL pastram fundalul gradient (CSS) — economie baterie/date.
  if (!bigEnough || !hasWebGL) return;

  // Satelit real Hamburg (port, Elba, cheiuri) — key-free.
  var ESRI = "https://server.arcgisonline.com/ArcGIS/rest/services/" +
             "World_Imagery/MapServer/tile/{z}/{y}/{x}";

  var map = new maplibregl.Map({
    container: el,
    style: {
      version: 8,
      sources: { esri: { type: "raster", tiles: [ESRI], tileSize: 256, attribution: "© Esri, Maxar, Earthstar Geographics" } },
      layers: [
        { id: "bg", type: "background", paint: { "background-color": "#060912" } },
        // opacitate sub 1 lasa fundalul inchis sa transpara -> satelit mai
        // intunecat/premium, pe care rutele si coletele neon ies puternic.
        { id: "esri", type: "raster", source: "esri",
          paint: { "raster-opacity": 0.82, "raster-brightness-max": 0.9, "raster-contrast": 0.05 } }
      ]
    },
    center: [9.9937, 53.5511], zoom: 11.2,
    pitch: reduceMotion ? 35 : 58, bearing: -18,
    interactive: false, attributionControl: false
  });

  // Huburi reale din Hamburg (lng, lat)
  var HUBS = {
    mitte: [9.9937, 53.5511], hafencity: [10.000, 53.541], stpauli: [9.962, 53.550],
    altona: [9.935, 53.5505], speicher: [9.988, 53.543], wandsbek: [10.085, 53.582],
    barmbek: [10.040, 53.586], eimsbuettel: [9.953, 53.574], harburg: [9.983, 53.460],
    bergedorf: [10.206, 53.489], airport: [10.006, 53.630], elbbr: [10.026, 53.534]
  };
  var CATS = ["#ff8a3d", "#39d5ff", "#9aa7bd", "#ff4d5e", "#2ad88f"];
  var PAIRS = [
    ["airport", "hafencity"], ["harburg", "mitte"], ["altona", "wandsbek"],
    ["stpauli", "bergedorf"], ["eimsbuettel", "harburg"], ["speicher", "barmbek"],
    ["mitte", "airport"], ["hafencity", "altona"], ["wandsbek", "harburg"], ["barmbek", "elbbr"]
  ];

  function arc(a, b, bend, n) {
    bend = bend || 0.18; n = n || 64;
    var ax = a[0], ay = a[1], bx = b[0], by = b[1];
    var mx = (ax + bx) / 2, my = (ay + by) / 2;
    var dx = bx - ax, dy = by - ay;
    var cx = mx - dy * bend, cy = my + dx * bend;
    var pts = [];
    for (var i = 0; i <= n; i++) {
      var t = i / n, u = 1 - t;
      pts.push([u * u * ax + 2 * u * t * cx + t * t * bx,
                u * u * ay + 2 * u * t * cy + t * t * by]);
    }
    return pts;
  }

  var routes = PAIRS.map(function (p, i) {
    return { line: arc(HUBS[p[0]], HUBS[p[1]]), color: CATS[i % CATS.length],
             t: Math.random(), sp: 0.0016 + Math.random() * 0.003 };
  });

  function fc(features) { return { type: "FeatureCollection", features: features }; }

  map.on("load", function () {
    var hubFeats = Object.keys(HUBS).map(function (k) {
      return { type: "Feature", geometry: { type: "Point", coordinates: HUBS[k] }, properties: {} };
    });
    map.addSource("hubs", { type: "geojson", data: fc(hubFeats) });
    map.addLayer({ id: "hubs-glow", type: "circle", source: "hubs",
      paint: { "circle-radius": 11, "circle-color": "#4f8cff", "circle-opacity": 0.18, "circle-blur": 1 } });
    map.addLayer({ id: "hubs", type: "circle", source: "hubs",
      paint: { "circle-radius": 3.5, "circle-color": "#cfe0ff",
               "circle-stroke-color": "#4f8cff", "circle-stroke-width": 1.5 } });

    map.addSource("routes", { type: "geojson", data: fc(routes.map(function (r) {
      return { type: "Feature", geometry: { type: "LineString", coordinates: r.line },
               properties: { color: r.color } };
    })) });
    map.addLayer({ id: "routes", type: "line", source: "routes",
      layout: { "line-cap": "round", "line-join": "round" },
      paint: { "line-color": ["get", "color"], "line-width": 2, "line-opacity": 0.55, "line-blur": 0.4 } });

    map.addSource("packets", { type: "geojson", data: fc([]) });
    map.addLayer({ id: "packets-glow", type: "circle", source: "packets",
      paint: { "circle-radius": 8, "circle-color": ["get", "color"], "circle-opacity": 0.35, "circle-blur": 0.8 } });
    map.addLayer({ id: "packets", type: "circle", source: "packets",
      paint: { "circle-radius": 4.5, "circle-color": ["get", "color"],
               "circle-stroke-color": "#ffffff", "circle-stroke-width": 1 } });

    var packetSrc = map.getSource("packets");

    // Pozitie statica a coletelor cand miscarea e redusa (fara bucla rAF).
    function staticPackets() {
      packetSrc.setData(fc(routes.map(function (r) {
        var idx = Math.floor(0.5 * r.line.length);
        return { type: "Feature", geometry: { type: "Point", coordinates: r.line[idx] },
                 properties: { color: r.color } };
      })));
    }

    if (reduceMotion) { staticPackets(); return; }

    // Animatie: colete pe trasee.
    var running = true;
    function frame() {
      if (!running) return;
      var feats = routes.map(function (r) {
        r.t = (r.t + r.sp) % 1;
        var idx = Math.min(r.line.length - 1, Math.floor(r.t * r.line.length));
        return { type: "Feature", geometry: { type: "Point", coordinates: r.line[idx] },
                 properties: { color: r.color } };
      });
      packetSrc.setData(fc(feats));
      requestAnimationFrame(frame);
    }
    frame();

    // Pauza cand sectiunea nu e vizibila (economie CPU/baterie).
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        var vis = entries[0].isIntersecting;
        if (vis && !running) { running = true; frame(); }
        else if (!vis) { running = false; }
      }, { threshold: 0.05 }).observe(el);
    }

    // „Viu": leganare lenta a bearing-ului + parallax usor la mouse.
    var targetBearing = -18, targetPitch = 58, sway = 0;
    document.addEventListener("mousemove", function (e) {
      targetBearing = -18 + (e.clientX / window.innerWidth - 0.5) * 30;
      targetPitch = 58 - (e.clientY / window.innerHeight - 0.5) * 12;
    });
    (function drift() {
      sway += 0.00045;
      map.setBearing(targetBearing + Math.sin(sway) * 5);
      map.setPitch(map.getPitch() + (targetPitch - map.getPitch()) * 0.05);
      requestAnimationFrame(drift);
    })();
  });
})();
