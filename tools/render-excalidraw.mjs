// Renderiza un .excalidraw a SVG, PNG y PDF con la librería oficial de Excalidraw (exportToSvg) en Chrome headless (CDP).
// Uso: node tools/render-excalidraw.mjs Diagramas/harness.excalidraw [salida-sin-extension]
// Requiere Google Chrome y acceso a esm.sh (carga @excalidraw/excalidraw 0.18 y sus fuentes, que quedan embebidas en el SVG).
import fs from 'node:fs'; import path from 'node:path'; import os from 'node:os'; import {spawn} from 'node:child_process'; import {pathToFileURL} from 'node:url';
const src = process.argv[2]; if (!src) throw new Error('Pasa el .excalidraw');
const stem = process.argv[3] || src.replace(/\.excalidraw$/, '');
const scene = JSON.parse(fs.readFileSync(src, 'utf8'));
const els = scene.elements.filter(e => !e.isDeleted);
const PAD = 32;
const minX = Math.min(...els.map(e => e.x)), minY = Math.min(...els.map(e => e.y));
const maxX = Math.max(...els.map(e => e.x + e.width)), maxY = Math.max(...els.map(e => e.y + e.height));
const W = Math.ceil(maxX - minX + 2 * PAD), H = Math.ceil(maxY - minY + 2 * PAD);
const html = `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;background:#fff}svg{display:block}@page{size:${W}px ${H}px;margin:0}</style></head><body><div id="err"></div>
<script id="scene" type="application/json">${JSON.stringify(scene).replace(/<\//g, '<\\/')}</script>
<script type="module">
try {
  const { exportToSvg, restoreElements } = await import("https://esm.sh/@excalidraw/excalidraw@0.18.0?deps=react@18.3.1,react-dom@18.3.1");
  const scene = JSON.parse(document.getElementById('scene').textContent);
  const elements = restoreElements(scene.elements, null);
  const svg = await exportToSvg({ elements, files: scene.files || {}, exportPadding: ${PAD},
    appState: { ...(scene.appState||{}), exportBackground: true, viewBackgroundColor: '#ffffff', exportWithDarkMode: false, exportEmbedScene: false } });
  svg.setAttribute('width', '${W}'); svg.setAttribute('height', '${H}');
  document.getElementById('scene').remove(); document.body.replaceChildren(svg);
  await document.fonts.ready; window.__done = true;
} catch (e) { document.getElementById('err').textContent = 'ERR ' + e.message; window.__done = 'error'; }
</script></body></html>`;
const tmp = path.join(os.tmpdir(), `excalidraw-render-${process.pid}.html`); fs.writeFileSync(tmp, html);
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const proc = spawn(chrome, ['--headless=new', '--disable-gpu', '--hide-scrollbars', '--no-first-run', '--allow-file-access-from-files', '--remote-debugging-port=0', `--user-data-dir=${fs.mkdtempSync(path.join(os.tmpdir(), 'chrome-prof-'))}`, 'about:blank'], {stdio: ['ignore', 'ignore', 'pipe']});
const wsUrl = await new Promise((res, rej) => { let buf = ''; proc.stderr.on('data', d => { buf += d; const m = buf.match(/DevTools listening on (ws:\/\/\S+)/); if (m) res(m[1]); }); setTimeout(() => rej(new Error('Chrome no expuso DevTools')), 20000); });
const port = new URL(wsUrl).port;
const target = await (await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, {method: 'PUT'})).json();
const ws = new WebSocket(target.webSocketDebuggerUrl); await new Promise(r => ws.onopen = r);
let id = 0; const pending = new Map();
ws.onmessage = ev => { const m = JSON.parse(ev.data); if (m.id && pending.has(m.id)) { const {res, rej} = pending.get(m.id); pending.delete(m.id); m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result); } };
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, {res, rej}); ws.send(JSON.stringify({id: i, method, params})); });
const evalJs = async expr => (await send('Runtime.evaluate', {expression: expr, returnByValue: true, awaitPromise: true})).result.value;
try {
  await send('Page.enable'); await send('Runtime.enable');
  await send('Emulation.setDeviceMetricsOverride', {width: W, height: H, deviceScaleFactor: 1.5, mobile: false});
  await send('Page.navigate', {url: pathToFileURL(tmp).href});
  const t0 = Date.now(); let state;
  while (!(state = await evalJs('window.__done || null'))) { if (Date.now() - t0 > 180000) throw new Error('timeout esperando exportToSvg'); await new Promise(r => setTimeout(r, 500)); }
  if (state === 'error') throw new Error(await evalJs('document.getElementById("err").textContent'));
  let svgText = await evalJs('document.querySelector("svg").outerHTML');
  if (!/xmlns=/.test(svgText.slice(0, 200))) svgText = svgText.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
  fs.writeFileSync(stem + '.svg', svgText);
  const shot = await send('Page.captureScreenshot', {format: 'png', captureBeyondViewport: true, clip: {x: 0, y: 0, width: W, height: H, scale: 1}});
  fs.writeFileSync(stem + '.png', Buffer.from(shot.data, 'base64'));
  const pdf = await send('Page.printToPDF', {printBackground: true, preferCSSPageSize: true, paperWidth: W / 96, paperHeight: H / 96, marginTop: 0, marginBottom: 0, marginLeft: 0, marginRight: 0, scale: 1});
  fs.writeFileSync(stem + '.pdf', Buffer.from(pdf.data, 'base64'));
  const sz = f => (fs.statSync(f).size / 1024).toFixed(0) + 'KB';
  console.log(JSON.stringify({svg: sz(stem + '.svg'), png: sz(stem + '.png'), pdf: sz(stem + '.pdf'), W, H, ms: Date.now() - t0}));
} finally { ws.close(); proc.kill(); fs.unlinkSync(tmp); }
