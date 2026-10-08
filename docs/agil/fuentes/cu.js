// Diagrama de casos de uso PowerFit (SVG -> PNG)
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const W = 1720, H = 1250, RX = 118, RY = 33;
const CU = {
  '01': ['Iniciar sesión', 560, 140], '04': ['Cerrar sesión', 560, 248],
  '02': ['Recuperar contraseña', 1000, 92], '03': ['Bloquear acceso por|intentos fallidos', 1000, 192],
  '06': ['Validar RUT', 1000, 335], '05': ['Registrar socio', 560, 360], '07': ['Consultar socios', 560, 452],
  '08': ['Registrar inscripción|mensual', 560, 546], '09': ['Verificar cupo|disponible', 1000, 546],
  '10': ['Cobrar mensualidad', 560, 642], '11': ['Renovar membresía', 1000, 642],
  '12': ['Controlar ingreso|de socio', 560, 748], '13': ['Verificar vigencia|de membresía', 1000, 808],
  '14': ['Vender suplemento', 560, 852], '15': ['Registrar suplemento', 560, 948], '16': ['Consultar valor|del dólar', 1000, 902],
  '17': ['Crear clase', 560, 1048], '19': ['Registrar asistencia', 560, 1145], '18': ['Consultar nómina|de clase', 1000, 1145],
};
const ACT = { T: ['Trabajador', 70, 200, '«abstracto»'], R: ['Recepcionista', 178, 655], I: ['Instructor', 178, 1070], S: ['Socio', 1625, 748], D: ['API Dólar\n(mindicador.cl)', 1625, 902, 'sys'], M: ['Servidor de\ncorreo', 1625, 92, 'sys'] };
const ASOC = [['T', '01'], ['T', '04'], ['R', '05'], ['R', '07'], ['R', '08'], ['R', '10'], ['R', '12'], ['R', '14'], ['R', '15'], ['I', '17'], ['I', '19'], ['S', '12'], ['D', '16'], ['M', '02']];
const INC = [['01', '06'], ['05', '06'], ['08', '09'], ['10', '11'], ['12', '13'], ['14', '16'], ['15', '16'], ['19', '18']];
const EXT = [['02', '01'], ['03', '01'], ['10', '12']];

function borde(id, hacia) { const [, x, y] = CU[id]; const [tx, ty] = hacia; const dx = tx - x, dy = ty - y; const t = 1 / Math.sqrt((dx / RX) ** 2 + (dy / RY) ** 2); return [x + dx * t, y + dy * t]; }
const ctr = (id) => [CU[id][1], CU[id][2]];
let s = `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" font-family="Inter, sans-serif">
<defs><marker id="open" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse"><path d="M1 1 L11 6 L1 11" fill="none" stroke="#374151" stroke-width="1.6"/></marker>
<marker id="tri" viewBox="0 0 20 20" refX="19" refY="10" markerWidth="20" markerHeight="20" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1 L19 10 L1 19 Z" fill="#fff" stroke="#111827" stroke-width="1.6"/></marker></defs>
<rect width="${W}" height="${H}" fill="#fff"/>
<rect x="300" y="36" width="1190" height="1185" rx="10" fill="#FFFBF7" stroke="#C2410C" stroke-width="2"/>
<text x="320" y="66" font-size="19" font-weight="700" fill="#9A3412">Sistema PowerFit</text>
<text x="320" y="88" font-size="13" fill="#9A3412">«sistema» gestión del gimnasio</text>`;
// zonas
const zona = (y, h, t) => s += `<rect x="318" y="${y}" width="1154" height="${h}" rx="8" fill="none" stroke="#F3D9C8" stroke-dasharray="4 4"/><text x="1462" y="${y + 18}" text-anchor="end" font-size="12" fill="#C2410C" font-weight="600">${t}</text>`;
zona(102, 186, 'Acceso al sistema'); zona(302, 690, 'Recepción'); zona(1002, 205, 'Instrucción');
// asociaciones
for (const [a, c] of ASOC) { const [, ax, ay, k] = ACT[a]; const fromX = ax < 800 ? ax + 24 : ax - (k ? 62 : 24); const p = [CU[c][1] + (ax < 800 ? -RX : RX), CU[c][2]]; s += `<line x1="${fromX}" y1="${ay - (k ? 0 : 6)}" x2="${p[0]}" y2="${p[1]}" stroke="#111827" stroke-width="1.6"/>`; }
// include / extend
function rel(a, b, tipo) { const p1 = borde(a, ctr(b)), p2 = borde(b, ctr(a)); const mx = (p1[0] + p2[0]) / 2, my = (p1[1] + p2[1]) / 2; const col = tipo === 'include' ? '#1D4ED8' : '#7C3AED';
  s += `<line x1="${p1[0]}" y1="${p1[1]}" x2="${p2[0]}" y2="${p2[1]}" stroke="${col}" stroke-width="1.6" stroke-dasharray="7 5" marker-end="url(#open)" style="color:${col}"/>`;
  const tw = tipo === 'include' ? 66 : 62; s += `<rect x="${mx - tw / 2}" y="${my - 11}" width="${tw}" height="20" rx="4" fill="#fff" stroke="${col}" stroke-width=".8"/><text x="${mx}" y="${my + 4}" text-anchor="middle" font-size="12.5" font-weight="600" fill="${col}">«${tipo}»</text>`; }
INC.forEach(([a, b]) => rel(a, b, 'include')); EXT.forEach(([a, b]) => rel(a, b, 'extend'));
// generalización
const gen = (from, to) => { const [, fx, fy] = ACT[from]; const [, tx, ty] = ACT[to]; const a = [fx, fy - 58], b = [tx + 4, ty + 92]; s += `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" stroke="#111827" stroke-width="1.6" marker-end="url(#tri)"/>`; };
gen('R', 'T'); gen('I', 'T');
// casos de uso
for (const [id, [t, x, y]] of Object.entries(CU)) {
  const lin = t.split('|'); const incl = INC.some(r => r[1] === id), ext = EXT.some(r => r[0] === id && id !== '10');
  s += `<ellipse cx="${x}" cy="${y}" rx="${RX}" ry="${RY}" fill="${incl ? '#EFF6FF' : ext ? '#F5F3FF' : '#FFF7ED'}" stroke="${incl ? '#1D4ED8' : ext ? '#7C3AED' : '#C2410C'}" stroke-width="1.8"/>`;
  s += `<text x="${x}" y="${y - (lin.length - 1) * 8 - 9}" text-anchor="middle" font-size="11" font-weight="700" fill="#6B7280">CU-${id}</text>`;
  lin.forEach((l, i) => s += `<text x="${x}" y="${y + 6 + i * 16 - (lin.length - 1) * 8}" text-anchor="middle" font-size="14.5" font-weight="600" fill="#111827">${l}</text>`);
}
// actores
for (const [k, [n, x, y, extra]] of Object.entries(ACT)) {
  if (extra === 'sys') { const ls = n.split('\n'); s += `<rect x="${x - 62}" y="${y - 40}" width="124" height="80" rx="6" fill="#F9FAFB" stroke="#111827" stroke-width="1.6"/><text x="${x}" y="${y - 18}" text-anchor="middle" font-size="12" fill="#6B7280">«actor sistema»</text>`; ls.forEach((l, i) => s += `<text x="${x}" y="${y + 4 + i * 17}" text-anchor="middle" font-size="14" font-weight="700">${l}</text>`); continue; }
  s += `<g stroke="#111827" stroke-width="2" fill="none"><circle cx="${x}" cy="${y - 40}" r="14" fill="#fff"/><line x1="${x}" y1="${y - 26}" x2="${x}" y2="${y + 12}"/><line x1="${x - 22}" y1="${y - 12}" x2="${x + 22}" y2="${y - 12}"/><line x1="${x}" y1="${y + 12}" x2="${x - 18}" y2="${y + 42}"/><line x1="${x}" y1="${y + 12}" x2="${x + 18}" y2="${y + 42}"/></g>`;
  s += `<text x="${x}" y="${y + 64}" text-anchor="middle" font-size="15" font-weight="700" ${extra ? 'font-style="italic"' : ''}>${n}</text>`;
  if (extra && extra !== 'sys') s += `<text x="${x}" y="${y + 81}" text-anchor="middle" font-size="12" fill="#6B7280">${extra}</text>`;
}
// leyenda
s += `<g font-size="12.5"><rect x="1500" y="1130" width="212" height="88" rx="6" fill="#fff" stroke="#E5E7EB"/>
<line x1="1510" y1="1150" x2="1546" y2="1150" stroke="#1D4ED8" stroke-dasharray="7 5" stroke-width="1.6"/><text x="1552" y="1154">«include»: obligatorio</text>
<line x1="1510" y1="1173" x2="1546" y2="1173" stroke="#7C3AED" stroke-dasharray="7 5" stroke-width="1.6"/><text x="1552" y="1177">«extend»: condicional</text>
<line x1="1510" y1="1198" x2="1544" y2="1198" stroke="#111" stroke-width="1.6" marker-end="url(#tri)"/><text x="1552" y="1202">Generalización</text></g>`;
s += '</svg>';
fs.writeFileSync(__dirname + '/casos_de_uso.svg', s);
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: W, height: H }, deviceScaleFactor: 1.6 }); await p.setContent(`<body style="margin:0">${s}</body>`); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: __dirname + '/casos_de_uso.png' }); await b.close(); console.log('ok'); })();
