// Generador de mockups PowerFit (imágenes PNG + mapa de hotspots para Marvel)
const fs = require('fs');
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const OUT = process.argv[2] || __dirname + '/png/';
fs.mkdirSync(OUT, { recursive: true });

// ---------- RUT ----------
function dv(cuerpo) { let s = 0, m = 2; for (const d of String(cuerpo).split('').reverse()) { s += +d * m; m = m === 7 ? 2 : m + 1; } const r = 11 - (s % 11); return r === 11 ? '0' : r === 10 ? 'K' : String(r); }
const rut = (c) => String(c).replace(/\B(?=(\d{3})+(?!\d))/g, '.') + '-' + dv(c);

// ---------- Íconos (trazos estilo Lucide) ----------
const IC = {
  home: '<path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
  users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
  clip: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="M12 11h4"/><path d="M12 16h4"/><path d="M8 11h.01"/><path d="M8 16h.01"/>',
  card: '<rect width="20" height="14" x="2" y="5" rx="2"/><line x1="2" x2="22" y1="10" y2="10"/>',
  door: '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" x2="3" y1="12" y2="12"/>',
  box: '<path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>',
  cal: '<rect width="18" height="18" x="3" y="4" rx="2"/><line x1="16" x2="16" y1="2" y2="6"/><line x1="8" x2="8" y1="2" y2="6"/><line x1="3" x2="21" y1="10" y2="10"/>',
  check: '<polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" x2="9" y1="12" y2="12"/>',
  menu: '<line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>',
  search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
  down: '<path d="m6 9 6 6 6-6"/>',
  dollar: '<line x1="12" x2="12" y1="2" y2="22"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
  alert: '<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>',
  ok: '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>',
  lock: '<rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
  mail: '<rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
  x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  plus: '<path d="M5 12h14"/><path d="M12 5v14"/>',
  print: '<polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect width="12" height="8" x="6" y="14"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
  back: '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
  ban: '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/>',
  idcard: '<rect width="20" height="16" x="2" y="4" rx="2"/><circle cx="8" cy="11" r="2.5"/><path d="M5 16.5c.8-1.5 1.9-2 3-2s2.2.5 3 2"/><line x1="14" x2="19" y1="9" y2="9"/><line x1="14" x2="18" y1="13" y2="13"/>',
  trash: '<path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
  dumb: '<path d="M6.5 6.5v11"/><path d="M17.5 6.5v11"/><path d="M3 9v6"/><path d="M21 9v6"/><path d="M6.5 12h11"/>',
  key: '<circle cx="7.5" cy="15.5" r="5.5"/><path d="m21 2-9.6 9.6"/><path d="m15.5 7.5 3 3L22 7l-3-3"/>',
  clock: '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
  info: '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
  sq: '<rect width="18" height="18" x="3" y="3" rx="3"/>',
  sqok: '<rect width="18" height="18" x="3" y="3" rx="3" fill="currentColor"/><polyline points="7 12 10.5 15.5 17 9" stroke="#fff"/>',
};
const I = (n, s = 18, extra = '') => `<svg width="${s}" height="${s}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ${extra}>${IC[n]}</svg>`;
const go = (g) => g ? ` data-go="${g}"` : '';

// ---------- Componentes ----------
function field({ label, value = '', ph = '', err, ok, g, focus, icon, help, type, ro, w }) {
  const cls = ['inp', err ? 'err' : '', focus ? 'focus' : '', ro ? 'ro' : '', ok ? 'okb' : ''].join(' ');
  let shown = value ? (type === 'pass' ? '•'.repeat(value.length) : value) : `<span class="ph">${ph}</span>`;
  return `<div class="fld"${w ? ` style="width:${w}px"` : ''}>${label ? `<label>${label}</label>` : ''}
    <div class="${cls}"${go(g)}>${icon ? `<span class="ic">${I(icon, 17)}</span>` : ''}<span class="val">${shown}</span>${focus ? '<span class="caret"></span>' : ''}${ok ? `<span class="okic">${I('ok', 17)}</span>` : ''}${err ? `<span class="erric">${I('alert', 17)}</span>` : ''}</div>
    ${err ? `<div class="msg e">${err}</div>` : help ? `<div class="msg">${help}</div>` : ''}</div>`;
}
function select({ label, value = '', ph = 'Seleccione…', g, open, w, err, ddw }) {
  const box = `<div class="inp sel ${open ? 'focus' : ''} ${err ? 'err' : ''}"${go(g)}><span class="val">${value || `<span class="ph">${ph}</span>`}</span><span class="chev">${I('down', 17)}</span></div>`;
  const dd = open ? `<div class="dd"${ddw ? ` style="right:auto;width:${ddw}px"` : ''}>${open}</div>` : '';
  return `<div class="fld"${w ? ` style="width:${w}px"` : ''}>${label ? `<label>${label}</label>` : ''}<div class="rel">${box}${dd}</div>${err ? `<div class="msg e">${err}</div>` : ''}</div>`;
}
const opt = (t, { g, sub, hov, dis, sel, tag } = {}) => `<div class="opt ${hov ? 'hov' : ''} ${dis ? 'dis' : ''} ${sel ? 'sel' : ''}"${go(g)}><div><div>${t}</div>${sub ? `<div class="sub">${sub}</div>` : ''}</div>${tag || ''}${sel ? `<span class="tick">${I('ok', 15)}</span>` : ''}</div>`;
function btn(t, { k = 'pri', g, icon, dis, sm, w } = {}) { return `<button class="btn ${k} ${dis ? 'dis' : ''} ${sm ? 'sm' : ''}"${go(g)}${w ? ` style="width:${w}px"` : ''}>${icon ? I(icon, sm ? 15 : 17) : ''}<span>${t}</span></button>`; }
const badge = (t, k) => `<span class="badge ${k}">${t}</span>`;
function alert(k, title, txt, { g, icon } = {}) {
  const ic = icon || { ok: 'ok', err: 'alert', warn: 'alert', info: 'info' }[k];
  return `<div class="alert ${k}"><span class="aic">${I(ic, 20)}</span><div class="atx"><b>${title}</b>${txt ? `<div>${txt}</div>` : ''}</div>${g ? `<span class="ax"${go(g)}>${I('x', 16)}</span>` : ''}</div>`;
}
const toast = (k, title, txt, g) => `<div class="toast ${k}"><span class="aic">${I(k === 'ok' ? 'ok' : 'alert', 20)}</span><div class="atx"><b>${title}</b>${txt ? `<div>${txt}</div>` : ''}</div><span class="ax"${go(g)}>${I('x', 15)}</span></div>`;
function table(h, rows, { cls = '' } = {}) {
  return `<table class="tb ${cls}"><thead><tr>${h.map(x => `<th>${x}</th>`).join('')}</tr></thead><tbody>${rows.map(r => `<tr${r.cls ? ` class="${r.cls}"` : ''}>${(r.c || r).map(x => `<td>${x}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
}
const card = (body, { title, right, pad = 20, style = '' } = {}) => `<div class="card" style="padding:${pad}px;${style}">${title ? `<div class="ch"><h3>${title}</h3>${right || ''}</div>` : ''}${body}</div>`;
const kpi = (ic, t, v, s, k) => `<div class="kpi"><div class="kic ${k}">${I(ic, 20)}</div><div><div class="kt">${t}</div><div class="kv">${v}</div><div class="ks">${s}</div></div></div>`;
const linkA = (t, g) => `<a class="lnk"${go(g)}>${t}</a>`;
const iconBtn = (ic, g, title = '') => `<span class="ibtn" title="Ícono ${title}"${go(g)}>${I(ic, 16)}</span>`;

// ---------- Layouts ----------
const NAV_R = [['home', 'Inicio', 'recep_dash'], ['users', 'Socios', 'socios'], ['clip', 'Inscripciones', 'insc'], ['card', 'Cobros', 'cobro'], ['door', 'Control de ingreso', 'ingreso'], ['box', 'Suplementos', 'supl']];
const NAV_I = [['home', 'Inicio', 'inst_dash'], ['cal', 'Mis clases', 'mis_clases'], ['plus', 'Crear clase', 'clase_nueva'], ['check', 'Asistencia', 'nomina']];
function app({ rol = 'R', act, title, crumb, body, over = '', collapsed, menu }) {
  const nav = rol === 'R' ? NAV_R : NAV_I;
  const user = rol === 'R' ? ['VS', 'Valentina Soto', 'Recepcionista'] : ['CR', 'Camila Rojas', 'Instructora'];
  const side = collapsed
    ? `<aside class="side mini"><div class="logo"><span class="lg">${I('dumb', 20)}</span></div>${nav.map(([ic, t, g]) => `<a class="${t === act ? 'on' : ''}"${go(g)}>${I(ic, 19)}</a>`).join('')}</aside>`
    : `<aside class="side"><div class="logo"><span class="lg">${I('dumb', 20)}</span><div><b>PowerFit</b><small>Gestión del gimnasio</small></div></div>
      <div class="sect">${rol === 'R' ? 'RECEPCIÓN' : 'INSTRUCTOR'}</div>
      <nav>${nav.map(([ic, t, g]) => `<a class="${t === act ? 'on' : ''}"${go(g)}>${I(ic, 18)}<span>${t}</span></a>`).join('')}</nav>
      <div class="sfoot"><div class="tip">${I('lock', 15)}<span>Sesión segura · ${rol === 'R' ? 'Rol: Recepcionista' : 'Rol: Instructor'}</span></div></div></aside>`;
  const menuDD = menu ? `<div class="dd umenu"><div class="uhead"><b>${user[1]}</b><span>${user[2]} · ${rol === 'R' ? '22.222.222-2' : '11.111.111-1'}</span></div><div class="sep"></div>${opt(`<span class="row">${I('logout', 16)} Cerrar sesión</span>`, { g: rol === 'R' ? 'logout_modal' : 'login_salida', hov: true })}</div>` : '';
  const top = `<header class="top">${rol === 'R' ? `<span class="ibtn ham"${go(collapsed ? 'recep_dash' : 'sidebar_contraido')}>${I('menu', 20)}</span>` : ''}
    <div><div class="crumb">${crumb || 'PowerFit'}</div><h1>${title}</h1></div><div class="sp"></div>
    ${rol === 'R' ? `<div class="chip"${go('supl')}>${I('dollar', 15)}<span>Dólar hoy <b>$950,32</b></span></div>` : `<div class="chip">${I('cal', 15)}<span>Jueves 08/10/2026</span></div>`}
    <div class="rel"><div class="user"${go(menu ? (rol === 'R' ? 'recep_dash' : 'inst_dash') : (rol === 'R' ? 'user_menu' : 'inst_user_menu'))}><span class="av">${user[0]}</span><div><b>${user[1]}</b><small>${user[2]}</small></div>${I('down', 16)}</div>${menuDD}</div></header>`;
  return `<div class="app">${side}<main class="main">${top}<section class="content">${body}</section></main>${over}</div>`;
}
const modal = (body, w = 460, back) => `<div class="ovl"${back ? go(back) : ''}></div><div class="modal" style="width:${w}px">${body}</div>`;

function loginPage({ rut: r = '', pass = '', errR, errP, banner = '', foc, gR, gP, gBtn, gLink = 'recuperar', btnTxt = 'Ingresar', dis }) {
  return `<div class="login"><div class="lpanel"><div class="logo big"><span class="lg">${I('dumb', 26)}</span><div><b>PowerFit</b><small>Sistema de gestión del gimnasio</small></div></div>
    <h2>Socios, clases, pagos y suplementos en un solo lugar.</h2>
    <ul><li>${I('idcard', 18)} Fichas con RUT validado</li><li>${I('cal', 18)} Yoga, Spinning y Crossfit con control de cupos</li><li>${I('door', 18)} Control de ingreso por membresía</li><li>${I('dollar', 18)} Suplementos con el dólar del día</li></ul>
    <div class="lfoot">Uso exclusivo de trabajadores de PowerFit</div></div>
    <div class="lform"><div class="fcard"><h1>Iniciar sesión</h1><p class="sub">Ingresa con tu RUT y tu contraseña de trabajador.</p>${banner}
      ${field({ label: 'RUT', value: r, ph: 'Ej: 12.345.678-5', icon: 'idcard', err: errR, g: gR, focus: foc === 'r' })}
      ${field({ label: 'Contraseña', value: pass, ph: 'Tu contraseña', icon: 'lock', type: 'pass', err: errP, g: gP, focus: foc === 'p' })}
      <div class="lrow">${linkA('¿Olvidaste tu contraseña?', gLink)}</div>
      ${btn(btnTxt, { g: gBtn, w: 360, dis })}
      <div class="lhelp">${I('lock', 14)} Tras 5 intentos fallidos la cuenta se bloquea 15 minutos.</div></div></div></div>`;
}
function recPage({ r = '', mail = '', errR, errM, banner = '', gR, gM, gBtn, done }) {
  const body = done ? `${banner}<div style="margin-top:22px">${btn('Volver a iniciar sesión', { g: 'login', w: 360, icon: 'back' })}</div>` :
    `${banner}${field({ label: 'RUT', value: r, ph: 'Ej: 22.222.222-2', icon: 'idcard', err: errR, g: gR })}
     ${field({ label: 'Correo registrado', value: mail, ph: 'nombre@powerfit.cl', icon: 'mail', err: errM, g: gM })}
     ${btn('Enviar enlace de recuperación', { g: gBtn, w: 360 })}<div class="lrow c">${linkA('← Volver a iniciar sesión', 'login')}</div>`;
  return `<div class="login"><div class="lpanel"><div class="logo big"><span class="lg">${I('dumb', 26)}</span><div><b>PowerFit</b><small>Sistema de gestión del gimnasio</small></div></div>
    <h2>Recupera el acceso a tu cuenta de forma segura.</h2><ul><li>${I('mail', 18)} Te enviamos un enlace a tu correo registrado</li><li>${I('clock', 18)} El enlace vence en 30 minutos</li><li>${I('lock', 18)} Nunca te pediremos tu contraseña por correo</li></ul>
    <div class="lfoot">Uso exclusivo de trabajadores de PowerFit</div></div>
    <div class="lform"><div class="fcard"><span class="kic or" style="margin-bottom:14px">${I('key', 20)}</span><h1>Recuperar contraseña</h1><p class="sub">Ingresa tu RUT y el correo con que te registró el administrador.</p>${body}</div></div></div>`;
}

// ---------- Datos ----------
const S = {
  ana: [rut(12345678), 'Ana Pérez', badge('Vigente', 'g'), '07/11/2026'],
  pedro: [rut(15678432), 'Pedro González', badge('Pendiente de pago', 'y'), '—'],
  agustin: [rut(19283746), 'Agustín Reyes', badge('Vencida', 'r'), '08/09/2026'],
  daniela: [rut(16432198), 'Daniela Fuentes', badge('Vigente', 'g'), '20/10/2026'],
  matias: [rut(18765432), 'Matías Lagos', badge('Vencida', 'r'), '30/09/2026'],
  josefa: [rut(17234567), 'Josefa Muñoz', badge('Vigente', 'g'), '15/11/2026'],
};
const RUT_MALO = '12.345.678-9', RUT_NOREG = rut(9876543);
const verBtn = (g) => btn('Ver ficha', { k: 'ghost', sm: true, g });
const sociosRows = (o = {}) => Object.entries(S).map(([k, v]) => [`<span class="mono">${v[0]}</span>`, `<b>${v[1]}</b>`, v[2], v[3], o[k] || verBtn(k === 'pedro' ? 'socio_ok' : 'socio_ficha')]);
function sociosBody({ search = '', filtro, rows, chip = '' }) {
  return card(`<div class="tools">${field({ value: search, ph: 'Buscar por RUT o nombre…', icon: 'search', g: search ? 'socios' : 'socios_busqueda', w: 330, focus: !!search })}
    ${select({ value: 'Estado: Todos', g: filtro ? 'socios' : 'socios_filtro_abierto', open: filtro, w: 220 })}${chip}<div class="sp"></div>${btn('Nuevo socio', { icon: 'plus', g: 'socio_nuevo' })}</div>
    ${table(['RUT', 'Nombre', 'Membresía', 'Vence', ''], rows)}<div class="tfoot">Mostrando ${rows.length} de 128 socios</div>`, { pad: 18 });
}

// Inscripción
const CLASES = [
  ['yoga', 'Yoga', 'Lunes 09:00', '60 min', '8 cupos disponibles', '$15.000'],
  ['spin', 'Spinning', 'Martes 18:00', '45 min', '4 bicicletas disponibles', '$18.000'],
  ['cross', 'Crossfit', 'Miércoles 20:00', '50 min', 'Sin cupos (10 de 10 vendibles)', '$22.000'],
  ['yoga2', 'Yoga', 'Jueves 19:00', '60 min', '15 cupos disponibles', '$15.000'],
];
const tipoB = (t) => badge(t, t === 'Yoga' ? 'v' : t === 'Spinning' ? 'b' : 'o');
function inscBody({ socio, socioOpen, clase, claseOpen, lineas = [], alerta = '', gGuardar, gAgregar, gClase }) {
  const total = lineas.reduce((a, l) => a + l[3], 0);
  const fmt = (n) => '$' + n.toLocaleString('es-CL').replace(/,/g, '.');
  const det = lineas.length ? table(['#', 'Clase', 'Día y hora', 'Valor mensual', ''], lineas.map((l, i) => [String(i + 1), tipoB(l[0]), l[1], fmt(l[3]), iconBtn('trash', l[4], 'Quitar clase')])) :
    `<div class="empty">${I('clip', 30)}<b>Aún no hay clases en esta inscripción</b><span>Elige una clase y presiona «Agregar»</span></div>`;
  return `<div class="grid2">${card(`${alerta}
    ${select({ label: 'Socio', value: socio, ph: 'Buscar socio por RUT o nombre…', g: socio ? undefined : 'insc_socio_abierto', open: socioOpen })}
    ${select({ label: 'Mes de la inscripción', value: 'Octubre 2026' })}
    <div class="row2">${select({ label: 'Clase', value: clase, ph: 'Selecciona Yoga, Spinning o Crossfit…', g: gClase, open: claseOpen, ddw: 470 })}<div class="fld" style="width:auto"><label>&nbsp;</label>${btn('Agregar', { k: 'ghost', icon: 'plus', g: gAgregar, dis: !gAgregar })}</div></div>
    <div class="msg" style="margin-top:-4px">El sistema verifica el cupo de la clase antes de agregarla.</div>`, { title: '1. Datos de la inscripción' })}
    ${card(`${det}<div class="tot"><span>Total mensual</span><b>${fmt(total)}</b></div><div class="acts">${btn('Cancelar', { k: 'ghost', g: 'recep_dash' })}${btn('Guardar inscripción', { g: gGuardar, dis: !gGuardar })}</div>`, { title: '2. Detalle de clases reservadas', right: `<span class="muted">${lineas.length} clase(s)</span>` })}</div>`;
}
const L_YOGA = ['Yoga', 'Lunes 09:00', '', 15000], L_SPIN = ['Spinning', 'Martes 18:00', '', 18000];
const claseOpts = (gy, gc) => CLASES.map(([k, t, d, du, c, p]) => opt(`${tipoB(t)} <b style="margin-left:6px">${d}</b> <span class="muted">· ${du} · ${p}</span>`, { sub: c, g: k === 'yoga' ? gy : k === 'cross' ? gc : undefined, hov: k === 'yoga', dis: k === 'cross', tag: k === 'cross' ? badge('LLENO', 'r') : '' })).join('');

// Cobro
function cobroBody({ sel, medio, medioOpen, gCobrar }) {
  const radio = (on, g) => `<span class="radio ${on ? 'on' : ''}"${go(g)}></span>`;
  const rows = [
    { c: [radio(sel, sel ? undefined : 'cobro_sel'), '<b>Ana Pérez</b>', 'Octubre 2026', 'Yoga + Spinning', '<b>$33.000</b>', badge('Pendiente', 'y'), ''], cls: sel ? 'hl' : '' },
    { c: [radio(false), '<b>Pedro González</b>', 'Octubre 2026', 'Crossfit', '<b>$22.000</b>', badge('Pendiente', 'y'), ''] },
    { c: ['', '<b>Josefa Muñoz</b>', 'Octubre 2026', 'Yoga', '$15.000', badge('Pagada 02/10', 'g'), btn('Cobrar', { k: 'ghost', sm: true, g: 'cobro_doble' })] },
  ];
  const panel = sel ? `<div class="sum"><div><span>Socio</span><b>Ana Pérez · ${S.ana[0]}</b></div><div><span>Mes</span><b>Octubre 2026</b></div><div><span>Detalle</span><b>Yoga lun 09:00 · Spinning mar 18:00</b></div><div class="big"><span>Total a cobrar</span><b>$33.000</b></div></div>
     ${select({ label: 'Medio de pago', value: medio, g: medioOpen ? 'cobro_sel' : medio ? 'cobro_medio_abierto' : 'cobro_medio_abierto', open: medioOpen })}
     <div class="acts">${btn('Cancelar', { k: 'ghost', g: 'cobro' })}${btn('Confirmar cobro', { g: gCobrar, dis: !gCobrar, icon: 'card' })}</div>`
    : `<div class="empty">${I('card', 30)}<b>Selecciona una inscripción pendiente</b><span>Marca el círculo de la inscripción que vas a cobrar</span></div>`;
  return `<div class="grid2 w60">${card(table(['', 'Socio', 'Mes', 'Clases', 'Total', 'Estado', ''], rows), { title: 'Inscripciones del mes', right: `<span class="muted">2 pendientes</span>` })}${card(panel, { title: 'Registrar pago' })}</div>`;
}

// Ingreso
function ingresoBody({ r = '', res = '', gField = 'ingreso_lleno', gBtn, foc }) {
  const recientes = table(['Hora', 'Socio', 'Resultado'], [['10:41', 'Daniela Fuentes', badge('Permitido', 'g')], ['10:38', 'Matías Lagos', badge('Rechazado · vencida', 'r')], ['10:30', 'Josefa Muñoz', badge('Permitido', 'g')]]);
  return `<div class="grid2 w60">${card(`<p class="muted" style="margin:0 0 16px">Ingresa el RUT del socio que llega al gimnasio. El sistema valida el RUT y revisa si su membresía está vigente.</p>
    <div class="row2">${field({ value: r, ph: 'RUT del socio (ej: 12.345.678-5)', icon: 'idcard', g: gField, focus: foc })}${btn('Verificar ingreso', { g: gBtn, dis: !gBtn, icon: 'door' })}</div>${res}`, { title: 'Control de ingreso', pad: 22 })}
    ${card(recientes, { title: 'Ingresos recientes', right: '<span class="muted">Hoy</span>' })}</div>`;
}
const resBox = (k, ic, t, lines, acts) => `<div class="res ${k}"><span class="ric">${I(ic, 34)}</span><div><h2>${t}</h2>${lines.map(l => `<div>${l}</div>`).join('')}<div class="acts l">${acts}</div></div></div>`;

// Suplementos
const SUP = [['PROT-01', 'Proteína Whey 2 lb', 'US$ 45,00', '$42.765', '10'], ['CREA-02', 'Creatina monohidrato 300 g', 'US$ 28,50', '$27.084', '6'], ['BCAA-03', 'BCAA 2:1:1 200 g', 'US$ 22,00', '$20.907', '3'], ['PRE-04', 'Pre-entreno 30 servicios', 'US$ 35,90', '$34.117', '0']];
function suplBody({ banner, rows, newRow }) {
  const r = (rows || SUP).map((s, i) => ({ c: [`<span class="mono">${s[0]}</span>`, `<b>${s[1]}</b>`, s[2], `<b>${s[3]}</b>`, +s[4] === 0 ? badge('Sin stock', 'r') : +s[4] <= 3 ? badge(s[4] + ' · bajo', 'y') : s[4], +s[4] === 0 ? btn('Vender', { k: 'ghost', sm: true, dis: true }) : btn('Vender', { k: 'ghost', sm: true, g: i === 0 ? 'venta' : undefined, icon: 'card' })], cls: s[5] }));
  return `${banner}${card(`<div class="tools"><div class="dolar"><span class="kic gr">${I('dollar', 18)}</span><div><b>Dólar observado: $950,32</b><small>Fuente: API mindicador.cl (Banco Central) · actualizado hoy 09:00</small></div></div><div class="sp"></div>${btn('Actualizar dólar', { k: 'ghost', icon: 'refresh', g: 'supl_api_error' })}${btn('Nuevo suplemento', { icon: 'plus', g: 'supl_nuevo' })}</div>
    ${table(['Código', 'Producto', 'Costo USD', 'Precio venta CLP', 'Stock', ''], r)}<div class="tfoot">Precio CLP = costo USD × dólar del día × 1,0 (margen definido por el administrador)</div>`, { pad: 18 })}`;
}
function ventaModal({ cant = '', err, total = '—', gField = 'venta_lleno', gOk }) {
  return modal(`<div class="mh"><h3>Vender suplemento</h3><span class="ax"${go('supl')}>${I('x', 18)}</span></div>
    <div class="sum"><div><span>Producto</span><b>Proteína Whey 2 lb (PROT-01)</b></div><div><span>Precio unitario</span><b>$42.765</b></div><div><span>Stock disponible</span><b>10 unidades</b></div></div>
    ${field({ label: 'Cantidad', value: cant, ph: 'Ej: 1', err, g: gField, focus: !cant })}
    <div class="tot"><span>Total de la venta</span><b>${total}</b></div><div class="acts">${btn('Cancelar', { k: 'ghost', g: 'supl' })}${btn('Confirmar venta', { g: gOk, dis: !gOk })}</div>`, 470, 'supl');
}
function suplForm({ cod = '', nom = '', usd = '', stock = '', clp = '—', errU, gCod, gUsd, gOk, errCod }) {
  return `<div class="grid2 w60">${card(`<div class="row2">${field({ label: 'Código', value: cod, ph: 'Ej: PROT-05', g: gCod, err: errCod })}${field({ label: 'Stock inicial', value: stock, ph: 'Unidades' })}</div>
    ${field({ label: 'Nombre del producto', value: nom, ph: 'Ej: Proteína vegana 1 kg' })}
    ${field({ label: 'Costo en dólares (USD)', value: usd, ph: 'Ej: 39,90', icon: 'dollar', err: errU, g: gUsd, help: 'Debe ser mayor que 0. Se convierte con el dólar del día.' })}
    <div class="acts">${btn('Cancelar', { k: 'ghost', g: 'supl' })}${btn('Guardar suplemento', { g: gOk, dis: !gOk })}</div>`, { title: 'Datos del suplemento' })}
    ${card(`<div class="calc"><div><span>Costo USD</span><b>${usd || '—'}</b></div><div><span>× Dólar del día</span><b>$950,32</b></div><div class="big"><span>= Precio de venta CLP</span><b>${clp}</b></div></div><div class="msg">${I('info', 13)} El precio se recalcula solo cada vez que se actualiza el dólar.</div>`, { title: 'Precio calculado' })}</div>`;
}

// Instructor
const misClasesRows = (extra) => [
  [tipoB('Yoga'), 'Lunes', '09:00', '60 min', '12 / 20', '<b>8</b> (20 − 12)', btn('Ver nómina', { k: 'ghost', sm: true, g: 'nomina' })],
  [tipoB('Spinning'), 'Martes', '18:00', '45 min', '11 / 15', '<b>4</b> (bicicletas operativas − inscritos)', btn('Ver nómina', { k: 'ghost', sm: true, g: 'nomina' })],
  [tipoB('Crossfit'), 'Miércoles', '20:00', '50 min', '10 / 12', '<b>0</b> (12 − 2 reservados − 10)', btn('Ver nómina', { k: 'ghost', sm: true, g: 'nomina' })],
  [tipoB('Yoga'), 'Jueves', '19:00', '60 min', '5 / 20', '<b>15</b>', btn('Ver nómina', { k: 'ghost', sm: true, g: 'nomina' })],
  ...(extra ? [{ c: [tipoB('Crossfit'), 'Viernes', '19:00', '50 min', '0 / 12', '<b>10</b> ' + badge('Nueva', 'g'), btn('Ver nómina', { k: 'ghost', sm: true, g: 'nomina' })], cls: 'hl' }] : []),
];
const misClasesBody = (extra) => card(`<div class="tools"><p class="muted" style="margin:0">Los cupos disponibles se calculan con la regla de cada tipo de clase.</p><div class="sp"></div>${btn('Crear clase', { icon: 'plus', g: 'clase_nueva' })}</div>${table(['Tipo', 'Día', 'Hora', 'Duración', 'Inscritos', 'Cupos disponibles', ''], misClasesRows(extra))}`, { pad: 18 });
const TIPOS = (g) => [['Yoga', '20 colchonetas · 60 min · $15.000/mes'], ['Spinning', '15 bicicletas · 45 min · $18.000/mes'], ['Crossfit', '12 cupos (2 reservados para clases de prueba) · 50 min · $22.000/mes']].map(([t, s]) => opt(tipoB(t), { sub: s, g: t === 'Crossfit' ? g : undefined, hov: t === 'Crossfit' })).join('');
const DIAS = (gV, gL) => ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'].map(d => opt(d, { g: d === 'Viernes' ? gV : d === 'Lunes' ? gL : undefined, hov: d === 'Viernes', sub: d === 'Lunes' ? 'Ya tienes Yoga a las 09:00' : undefined })).join('');
function claseForm({ tipo, tipoOpen, dia, diaOpen, hora = '', alerta = '', gOk, info, errH }) {
  return `<div class="grid2 w60">${card(`${alerta}${select({ label: 'Tipo de clase', value: tipo ? tipoB(tipo) : '', g: tipoOpen ? 'clase_nueva' : 'clase_tipo_abierto', open: tipoOpen })}
    <div class="row2">${select({ label: 'Día de la semana', value: dia, g: tipo ? (diaOpen ? 'clase_nueva_tipo' : 'clase_dia_abierto') : undefined, open: diaOpen })}${field({ label: 'Hora de inicio', value: hora, ph: 'HH:MM', icon: 'clock', err: errH })}</div>
    <div class="acts">${btn('Cancelar', { k: 'ghost', g: 'mis_clases' })}${btn('Guardar clase', { g: gOk, dis: !gOk })}</div>`, { title: 'Nueva clase semanal' })}
    ${card(info || `<div class="empty">${I('info', 28)}<b>Elige un tipo de clase</b><span>Verás su cupo, duración y precio</span></div>`, { title: 'Reglas del tipo de clase' })}</div>`;
}
const infoCross = `<div class="sum"><div><span>Cupo máximo</span><b>12 personas</b></div><div><span>Cupos reservados</span><b>2 (clases de prueba)</b></div><div><span>Cupos vendibles</span><b>10</b></div><div><span>Duración</span><b>50 minutos</b></div><div class="big"><span>Valor mensual</span><b>$22.000</b></div></div>`;
const ALUMNOS = ['Ana Pérez', 'Daniela Fuentes', 'Josefa Muñoz', 'Pedro González', 'Matías Lagos', 'Ignacio Vera', 'Fernanda Díaz', 'Tomás Rivas'];
function nominaBody({ marcados = 0, claseOpen, banner = '', gGuardar, gChk }) {
  const rows = ALUMNOS.map((n, i) => { const on = i < marcados && i !== 4; return { c: [`<span class="chk ${on ? 'on' : ''}"${go(gChk)}>${I(on ? 'sqok' : 'sq', 19)}</span>`, `<b>${n}</b>`, `<span class="mono">${Object.values(S).find(s => s[1] === n)?.[0] || rut(20111222 + i * 1371)}</span>`, on ? badge('Presente', 'g') : marcados ? badge('Ausente', 'n') : '<span class="muted">Sin marcar</span>'], cls: on ? 'hl2' : '' }; });
  return `${banner}${card(`<div class="tools">${select({ value: `${tipoB('Yoga')} <b style="margin-left:6px">Lunes 09:00</b> · hoy`, g: claseOpen ? 'nomina' : 'nomina_clase_abierta', w: 330, open: claseOpen })}<div class="sp"></div><span class="muted">${marcados ? '7 presentes · 1 ausente' : '8 inscritos'}</span>${btn('Marcar todos', { k: 'ghost', icon: 'check', g: 'nomina_marcada' })}${btn('Guardar asistencia', { g: gGuardar, dis: !gGuardar })}</div>
    ${table(['', 'Socio', 'RUT', 'Asistencia'], rows)}`, { pad: 18 })}`;
}

// ---------- PANTALLAS ----------
const recepDash = (toastHtml = '', extra = {}) => app({ act: 'Inicio', title: 'Inicio', crumb: 'Recepción', ...extra,
  body: `${toastHtml}<div class="kpis">${kpi('users', 'Socios activos', '128', '+6 este mes', 'or')}${kpi('alert', 'Membresías vencidas', '9', 'requieren cobro', 'rd')}${kpi('door', 'Ingresos hoy', '47', 'hasta las 10:42', 'gr')}${kpi('dollar', 'Dólar observado', '$950,32', 'mindicador.cl', 'bl')}</div>
  <div class="grid2">${card(`<div class="qa">${btn('Nuevo socio', { icon: 'plus', g: 'socio_nuevo' })}${btn('Nueva inscripción', { k: 'ghost', icon: 'clip', g: 'insc' })}${btn('Control de ingreso', { k: 'ghost', icon: 'door', g: 'ingreso' })}${btn('Vender suplemento', { k: 'ghost', icon: 'box', g: 'supl' })}</div>`, { title: 'Accesos rápidos' })}
  ${card(table(['Clase', 'Hora', 'Cupos', ''], [[tipoB('Yoga'), '09:00', '8 disponibles', iconBtn('edit', 'acceso_denegado', 'Editar clase')], [tipoB('Spinning'), '18:00', '4 disponibles', iconBtn('edit', 'acceso_denegado', 'Editar clase')], [tipoB('Crossfit'), '20:00', badge('Lleno', 'r'), iconBtn('edit', 'acceso_denegado', 'Editar clase')]]), { title: 'Clases de hoy' })}</div>
  ${card(table(['Socio', 'RUT', 'Vence', 'Estado', ''], [['<b>Agustín Reyes</b>', S.agustin[0], '08/09/2026', badge('Vencida', 'r'), btn('Cobrar', { k: 'ghost', sm: true, g: 'cobro' })], ['<b>Matías Lagos</b>', S.matias[0], '30/09/2026', badge('Vencida', 'r'), btn('Cobrar', { k: 'ghost', sm: true, g: 'cobro' })], ['<b>Daniela Fuentes</b>', S.daniela[0], '20/10/2026', badge('Vence en 12 días', 'y'), btn('Cobrar', { k: 'ghost', sm: true, g: 'cobro' })]]), { title: 'Membresías por cobrar' })}` });
const instDash = (toastHtml = '', extra = {}) => app({ rol: 'I', act: 'Inicio', title: 'Inicio', crumb: 'Instructor', ...extra,
  body: `${toastHtml}<div class="kpis">${kpi('cal', 'Mis clases semanales', '4', 'Yoga, Spinning y Crossfit', 'or')}${kpi('users', 'Alumnos inscritos', '38', 'en octubre', 'bl')}${kpi('check', 'Asistencia promedio', '86%', 'últimas 4 semanas', 'gr')}${kpi('alert', 'Clases llenas', '1', 'Crossfit miércoles', 'rd')}</div>
  <div class="grid2">${card(`<div class="next"><span class="kic or">${I('clock', 20)}</span><div><b>${tipoB('Yoga')} Lunes 09:00 · 60 min</b><div class="muted">12 inscritos de 20 · Sala 1</div></div><div class="sp"></div>${btn('Tomar asistencia', { icon: 'check', g: 'nomina' })}</div>
  <div class="next"><span class="kic bl">${I('clock', 20)}</span><div><b>${tipoB('Spinning')} Martes 18:00 · 45 min</b><div class="muted">11 inscritos · 13 bicicletas operativas</div></div><div class="sp"></div>${btn('Ver nómina', { k: 'ghost', g: 'nomina' })}</div>`, { title: 'Próximas clases' })}
  ${card(`<div class="qa">${btn('Crear clase', { icon: 'plus', g: 'clase_nueva' })}${btn('Mis clases', { k: 'ghost', icon: 'cal', g: 'mis_clases' })}</div><div class="msg" style="margin-top:14px">${I('info', 13)} Solo los instructores pueden crear o modificar clases.</div>`, { title: 'Accesos rápidos' })}</div>` });

const SC = [];
const add = (id, nombre, cu, html) => SC.push({ id, nombre, cu, html });

// ===== CU-01/02/03 Login =====
add('login', 'Inicio de sesión — formulario vacío', 'CU-01', loginPage({ gR: 'login_lleno', gP: 'login_lleno_mal', gBtn: 'login_requeridos' }));
add('login_requeridos', 'Inicio de sesión — campos obligatorios sin completar', 'CU-01', loginPage({ errR: 'Ingresa tu RUT.', errP: 'Ingresa tu contraseña.', gR: 'login_lleno_instructor', gP: 'login_lleno', banner: '' }));
add('login_lleno', 'Inicio de sesión — formulario con datos (recepcionista)', 'CU-01', loginPage({ rut: '22.222.222-2', pass: 'Recepcion123', gBtn: 'recep_ok', gR: 'login', foc: 'p' }));
add('login_lleno_instructor', 'Inicio de sesión — formulario con datos (instructora)', 'CU-01', loginPage({ rut: '11.111.111-1', pass: 'Instructor123', gBtn: 'inst_ok', gR: 'login', foc: 'p' }));
add('login_lleno_mal', 'Inicio de sesión — datos con contraseña incorrecta', 'CU-01', loginPage({ rut: '22.222.222-2', pass: 'clave1234', gBtn: 'login_error', gR: 'login', foc: 'p' }));
add('login_error', 'Inicio de sesión incorrecto', 'CU-01', loginPage({ rut: '22.222.222-2', banner: alert('err', 'RUT o contraseña incorrectos.', 'Te quedan 4 intentos antes de que la cuenta se bloquee por 15 minutos.'), errP: 'Vuelve a escribir tu contraseña.', gR: 'login_lleno', gP: 'login_lleno', gBtn: 'login_bloqueado' }));
add('login_bloqueado', 'Cuenta bloqueada por 5 intentos fallidos', 'CU-03', loginPage({ rut: '22.222.222-2', banner: alert('warn', 'Cuenta bloqueada temporalmente.', 'Se registraron 5 intentos fallidos. Podrás intentarlo de nuevo en 15 minutos (10:57) o recuperar tu contraseña.', { icon: 'lock' }), btnTxt: 'Ingresar (bloqueado 14:52)', dis: true, gR: 'login' }));
add('recep_ok', 'Inicio de sesión correcto — panel de la recepcionista', 'CU-01', recepDash(toast('ok', 'Inicio de sesión correcto', '¡Bienvenida, Valentina! Rol: Recepcionista.', 'recep_dash')));
add('login_salida', 'Sesión cerrada correctamente', 'CU-04', loginPage({ banner: alert('info', 'Cerraste sesión correctamente.', 'Por seguridad, cierra el navegador si usas un equipo compartido.'), gR: 'login_lleno', gP: 'login_lleno_mal', gBtn: 'login_requeridos' }));
add('recuperar', 'Recuperar contraseña — formulario vacío', 'CU-02', recPage({ gR: 'recuperar_lleno', gM: 'recuperar_lleno_mal', gBtn: 'recuperar_lleno' }));
add('recuperar_lleno', 'Recuperar contraseña — formulario con datos', 'CU-02', recPage({ r: '22.222.222-2', mail: 'vsoto@powerfit.cl', gBtn: 'recuperar_ok', gR: 'recuperar' }));
add('recuperar_lleno_mal', 'Recuperar contraseña — datos que no coinciden', 'CU-02', recPage({ r: '22.222.222-2', mail: 'valentina@gmail.com', gBtn: 'recuperar_error', gR: 'recuperar' }));
add('recuperar_ok', 'Recuperar contraseña — enlace enviado', 'CU-02', recPage({ done: true, banner: alert('ok', 'Te enviamos un enlace a v•••••@powerfit.cl', 'Ábrelo antes de 30 minutos para crear una contraseña nueva. Si no lo ves, revisa la carpeta de spam.') }));
add('recuperar_error', 'Recuperar contraseña — error', 'CU-02', recPage({ r: '22.222.222-2', mail: 'valentina@gmail.com', banner: alert('err', 'Los datos no coinciden con un trabajador registrado.', 'Revisa el RUT y el correo, o pide al administrador que actualice tu correo.'), errM: 'Este correo no corresponde al RUT ingresado.', gM: 'recuperar_lleno', gR: 'recuperar_lleno', gBtn: 'recuperar_lleno' }));

// ===== Navegación general =====
add('recep_dash', 'Panel de la recepcionista (Inicio) con sidebar', 'General', recepDash());
add('sidebar_contraido', 'Sidebar contraído (solo íconos)', 'General', recepDash('', { collapsed: true }));
add('user_menu', 'Menú de usuario desplegado', 'CU-04', recepDash('', { menu: true }));
add('logout_modal', 'Confirmación de cierre de sesión', 'CU-04', recepDash('', { over: modal(`<div class="mc"><span class="kic or big">${I('logout', 26)}</span><h3>¿Cerrar sesión?</h3><p class="muted">Tendrás que ingresar de nuevo tu RUT y contraseña.</p><div class="acts c">${btn('Cancelar', { k: 'ghost', g: 'recep_dash' })}${btn('Cerrar sesión', { k: 'dan', g: 'login_salida' })}</div></div>`, 400, 'recep_dash') }));
add('acceso_denegado', 'Acceso denegado: la recepcionista no puede modificar clases', 'CU-17', app({ act: 'Inicio', title: 'Acceso denegado', crumb: 'Recepción / Clases',
  body: `<div class="denied">${card(`<span class="kic rd big">${I('ban', 30)}</span><h2>No tienes permiso para crear ni modificar clases</h2><p class="muted">Esta acción es exclusiva del rol <b>Instructor</b>. El intento quedó registrado (código 403).</p><div class="acts c">${btn('Volver al inicio', { icon: 'back', g: 'recep_dash' })}</div>`, { pad: 36 })}</div>` }));

// ===== CU-05/06/07 Socios =====
add('socios', 'Listado de socios', 'CU-07', app({ act: 'Socios', title: 'Socios', crumb: 'Recepción', body: sociosBody({ rows: sociosRows() }) }));
add('socios_filtro_abierto', 'Listado de socios — combobox de estado desplegado', 'CU-07', app({ act: 'Socios', title: 'Socios', crumb: 'Recepción',
  body: sociosBody({ filtro: [opt('Todos', { sel: true, g: 'socios' }), opt(badge('Vigente', 'g'), { g: 'socios' }), opt(badge('Vencida', 'r'), { hov: true, g: 'socios_filtrados' }), opt(badge('Pendiente de pago', 'y'), { g: 'socios' })].join(''), rows: sociosRows() }) }));
add('socios_filtrados', 'Listado de socios filtrado por «Vencida»', 'CU-07', app({ act: 'Socios', title: 'Socios', crumb: 'Recepción',
  body: sociosBody({ chip: `<span class="fchip">Estado: Vencida <span title="Quitar filtro"${go('socios')}>${I('x', 13)}</span></span>`, rows: sociosRows().filter((r, i) => [2, 4].includes(i)).map(r => { r[4] = btn('Cobrar', { k: 'ghost', sm: true, icon: 'card', g: 'cobro' }); return r; }) }).replace('Estado: Todos', 'Estado: Vencida') }));
add('socios_busqueda', 'Listado de socios — búsqueda por nombre', 'CU-07', app({ act: 'Socios', title: 'Socios', crumb: 'Recepción', body: sociosBody({ search: 'Ana', rows: sociosRows().slice(0, 1) }) }));
add('socio_ficha', 'Ficha del socio', 'CU-07', app({ act: 'Socios', title: 'Ana Pérez', crumb: 'Recepción / Socios',
  body: `<div class="tools" style="margin-bottom:16px">${btn('Volver a socios', { k: 'ghost', icon: 'back', g: 'socios' })}<div class="sp"></div>${btn('Nueva inscripción', { k: 'ghost', icon: 'clip', g: 'insc' })}${btn('Cobrar mensualidad', { icon: 'card', g: 'cobro' })}</div>
  <div class="grid2">${card(`<div class="sum"><div><span>RUT</span><b>${S.ana[0]}</b></div><div><span>Teléfono</span><b>+56 9 8765 4321</b></div><div><span>Correo</span><b>ana.perez@gmail.com</b></div><div><span>Socia desde</span><b>07/08/2026</b></div></div>`, { title: 'Datos personales' })}
  ${card(`<div class="sum"><div><span>Estado</span><b>${badge('Vigente', 'g')}</b></div><div><span>Inicio</span><b>08/10/2026</b></div><div><span>Vencimiento</span><b>07/11/2026</b></div><div><span>Días restantes</span><b>30</b></div></div>`, { title: 'Membresía' })}</div>
  ${card(table(['Mes', 'Clases', 'Total', 'Estado'], [['Octubre 2026', 'Yoga lun 09:00 · Spinning mar 18:00', '$33.000', badge('Pagada', 'g')], ['Septiembre 2026', 'Yoga lun 09:00', '$15.000', badge('Pagada', 'g')]]), { title: 'Inscripciones mensuales' })}` }));
const socioForm = (o) => card(`<div class="row2">${field({ label: 'RUT *', value: o.r, ph: 'Ej: 15.678.432-K', icon: 'idcard', err: o.errR, ok: o.okR, g: o.gR, help: 'Se valida el dígito verificador (módulo 11).' })}${field({ label: 'Nombre completo *', value: o.n, ph: 'Nombre y apellido', err: o.errN })}</div>
  <div class="row2">${field({ label: 'Teléfono', value: o.t, ph: '+56 9 …' })}${field({ label: 'Correo electrónico', value: o.m, ph: 'nombre@correo.cl', icon: 'mail' })}</div>
  <div class="note">${I('info', 15)} La membresía se crea automáticamente en estado <b>Pendiente de pago</b> hasta que se cobre la primera mensualidad.</div>
  <div class="acts">${btn('Cancelar', { k: 'ghost', g: 'socios' })}${btn('Guardar socio', { g: o.gOk, dis: o.dis })}</div>`, { title: 'Datos del nuevo socio', pad: 24 });
add('socio_nuevo', 'Registrar socio — formulario vacío', 'CU-05', app({ act: 'Socios', title: 'Nuevo socio', crumb: 'Recepción / Socios', body: `<div class="narrow">${socioForm({ gR: 'socio_nuevo_lleno', gOk: 'socio_nuevo_requeridos' })}</div>` }));
add('socio_nuevo_requeridos', 'Registrar socio — campos obligatorios', 'CU-05', app({ act: 'Socios', title: 'Nuevo socio', crumb: 'Recepción / Socios', body: `<div class="narrow">${alert('err', 'Revisa los campos marcados.', 'El RUT y el nombre son obligatorios.')}${socioForm({ errR: 'Ingresa el RUT del socio.', errN: 'Ingresa el nombre del socio.', gR: 'socio_nuevo_lleno', gOk: 'socio_nuevo_requeridos' })}</div>` }));
add('socio_nuevo_lleno', 'Registrar socio — formulario con datos (RUT válido)', 'CU-05', app({ act: 'Socios', title: 'Nuevo socio', crumb: 'Recepción / Socios', body: `<div class="narrow">${socioForm({ r: S.pedro[0], okR: true, n: 'Pedro González', t: '+56 9 7654 3210', m: 'pedro.gonzalez@gmail.com', gR: 'socio_nuevo_rut_mal', gOk: 'socio_ok' })}</div>` }));
add('socio_nuevo_rut_mal', 'Registrar socio — error: RUT inválido', 'CU-06', app({ act: 'Socios', title: 'Nuevo socio', crumb: 'Recepción / Socios', body: `<div class="narrow">${socioForm({ r: RUT_MALO, errR: 'RUT inválido: el dígito verificador no corresponde (debería ser 5).', n: 'Pedro González', t: '+56 9 7654 3210', m: 'pedro.gonzalez@gmail.com', gR: 'socio_nuevo_lleno', dis: true })}</div>` }));
add('socio_ok', 'Registrar socio — socio creado con éxito', 'CU-05', app({ act: 'Socios', title: 'Pedro González', crumb: 'Recepción / Socios', body: `${toast('ok', 'Socio registrado correctamente', 'Pedro González · membresía «Pendiente de pago».', 'socios')}
  <div class="tools" style="margin-bottom:16px">${btn('Volver a socios', { k: 'ghost', icon: 'back', g: 'socios' })}<div class="sp"></div>${btn('Inscribir en clases', { icon: 'clip', g: 'insc' })}</div>
  <div class="grid2">${card(`<div class="sum"><div><span>RUT</span><b>${S.pedro[0]}</b></div><div><span>Teléfono</span><b>+56 9 7654 3210</b></div><div><span>Correo</span><b>pedro.gonzalez@gmail.com</b></div><div><span>Socio desde</span><b>08/10/2026</b></div></div>`, { title: 'Datos personales' })}
  ${card(`<div class="sum"><div><span>Estado</span><b>${badge('Pendiente de pago', 'y')}</b></div><div><span>Siguiente paso</span><b>Inscribir en clases y cobrar</b></div></div>`, { title: 'Membresía' })}</div>` }));

// ===== CU-08/09 Inscripción =====
const insc = (o) => app({ act: 'Inscripciones', title: 'Nueva inscripción mensual', crumb: 'Recepción / Inscripciones', body: inscBody(o) });
const ANA = `<b>Ana Pérez</b> <span class="muted">· ${S.ana[0]}</span>`;
add('insc', 'Inscripción mensual — formulario vacío', 'CU-08', insc({}));
add('insc_socio_abierto', 'Inscripción mensual — combobox de socio desplegado', 'CU-08', insc({ socioOpen: `<div class="ddsearch">${I('search', 15)} <span>an</span><span class="caret"></span></div>${opt('<b>Ana Pérez</b>', { sub: S.ana[0] + ' · Vigente', g: 'insc_socio', hov: true })}${opt('<b>Daniela Fuentes</b>', { sub: S.daniela[0] + ' · Vigente' })}${opt('<b>Matías Lagos</b>', { sub: S.matias[0] + ' · Vencida' })}` }));
add('insc_socio', 'Inscripción mensual — socio seleccionado', 'CU-08', insc({ socio: ANA, gClase: 'insc_clase_abierto' }));
add('insc_clase_abierto', 'Inscripción mensual — combobox de clases con cupos', 'CU-09', insc({ socio: ANA, claseOpen: claseOpts('insc_1clase', 'insc_cupo_lleno') }));
add('insc_1clase', 'Inscripción mensual — una clase en el detalle', 'CU-08', insc({ socio: ANA, clase: `${tipoB('Spinning')} <b style="margin-left:6px">Martes 18:00</b> <span class="muted">· $18.000</span>`, gAgregar: 'insc_2clases', gClase: 'insc_clase_abierto', lineas: [[...L_YOGA.slice(0, 3), 15000, 'insc_socio']], gGuardar: 'insc_ok' }));
add('insc_2clases', 'Inscripción mensual — dos clases y total calculado', 'CU-08', insc({ socio: ANA, gClase: 'insc_clase_abierto', lineas: [['Yoga', 'Lunes 09:00', '', 15000, 'insc_1clase'], ['Spinning', 'Martes 18:00', '', 18000, 'insc_1clase']], gGuardar: 'insc_ok' }));
add('insc_cupo_lleno', 'Inscripción mensual — error: cupo lleno', 'CU-09', insc({ socio: ANA, gClase: 'insc_clase_abierto', alerta: alert('err', 'No se puede agregar Crossfit miércoles 20:00: la clase no tiene cupos.', 'Ya se vendieron los 10 cupos (12 − 2 reservados para clases de prueba). Elige otro horario.', { g: 'insc_socio' }), clase: `${tipoB('Crossfit')} <b style="margin-left:6px">Miércoles 20:00</b>` }));
add('insc_ok', 'Inscripción mensual — guardada con éxito', 'CU-08', app({ act: 'Inscripciones', title: 'Inscripción guardada', crumb: 'Recepción / Inscripciones', body: `<div class="denied">${card(`<span class="kic gr big">${I('ok', 30)}</span><h2>Inscripción de octubre guardada</h2><p class="muted">Ana Pérez · 2 clases (Yoga lunes 09:00 y Spinning martes 18:00) · <b>Total $33.000</b><br>Estado: ${badge('Pendiente de pago', 'y')}</p><div class="acts c">${btn('Nueva inscripción', { k: 'ghost', icon: 'plus', g: 'insc' })}${btn('Cobrar ahora', { icon: 'card', g: 'cobro_sel' })}</div>`, { pad: 36 })}</div>` }));

// ===== CU-10/11 Cobro =====
const cobro = (o, over = '', title = 'Cobro de mensualidades') => app({ act: 'Cobros', title, crumb: 'Recepción / Cobros', body: cobroBody(o), over });
add('cobro', 'Cobro de mensualidad — sin selección', 'CU-10', cobro({}));
add('cobro_sel', 'Cobro de mensualidad — inscripción seleccionada', 'CU-10', cobro({ sel: true }));
add('cobro_medio_abierto', 'Cobro de mensualidad — combobox de medio de pago', 'CU-10', cobro({ sel: true, medioOpen: ['Efectivo', 'Tarjeta de débito', 'Tarjeta de crédito', 'Transferencia'].map(m => opt(m, { g: m === 'Tarjeta de débito' ? 'cobro_lleno' : undefined, hov: m === 'Tarjeta de débito' })).join('') }));
add('cobro_lleno', 'Cobro de mensualidad — datos completos', 'CU-10', cobro({ sel: true, medio: 'Tarjeta de débito', gCobrar: 'cobro_ok' }));
add('cobro_ok', 'Cobro registrado y membresía renovada', 'CU-11', app({ act: 'Cobros', title: 'Pago registrado', crumb: 'Recepción / Cobros', body: `<div class="denied">${card(`<span class="kic gr big">${I('ok', 30)}</span><h2>Pago de $33.000 registrado</h2><p class="muted">Ana Pérez · Octubre 2026 · Tarjeta de débito<br>Membresía renovada: ${badge('Vigente', 'g')} hasta el <b>07/11/2026</b></p><div class="acts c">${btn('Volver a cobros', { k: 'ghost', icon: 'back', g: 'cobro' })}${btn('Ver comprobante', { icon: 'print', g: 'comprobante' })}</div>`, { pad: 36 })}</div>` }));
add('comprobante', 'Comprobante de pago', 'CU-10', app({ act: 'Cobros', title: 'Pago registrado', crumb: 'Recepción / Cobros', body: '', over: modal(`<div class="mh"><h3>Comprobante N° 000482</h3><span class="ax"${go('cobro_ok')}>${I('x', 18)}</span></div><div class="recibo"><div class="rlogo"><span class="lg">${I('dumb', 18)}</span><b>PowerFit</b></div><div class="sum"><div><span>Fecha</span><b>08/10/2026 10:45</b></div><div><span>Socio</span><b>Ana Pérez · ${S.ana[0]}</b></div><div><span>Yoga · lunes 09:00</span><b>$15.000</b></div><div><span>Spinning · martes 18:00</span><b>$18.000</b></div><div><span>Medio de pago</span><b>Tarjeta de débito</b></div><div class="big"><span>Total pagado</span><b>$33.000</b></div><div><span>Membresía vigente hasta</span><b>07/11/2026</b></div><div><span>Atendido por</span><b>Valentina Soto</b></div></div></div><div class="acts">${btn('Cerrar', { k: 'ghost', g: 'cobro' })}${btn('Imprimir', { icon: 'print', g: 'cobro' })}</div>`, 480, 'cobro_ok') }));
add('cobro_doble', 'Cobro de mensualidad — error: inscripción ya pagada', 'CU-10', app({ act: 'Cobros', title: 'Cobro de mensualidades', crumb: 'Recepción / Cobros', body: alert('err', 'Esta inscripción ya fue pagada el 02/10/2026.', 'Josefa Muñoz · Octubre 2026 · $15.000. El sistema no permite cobrar dos veces la misma inscripción.', { g: 'cobro' }) + cobroBody({}) }));

// ===== CU-12/13 Ingreso =====
const ing = (o) => app({ act: 'Control de ingreso', title: 'Control de ingreso', crumb: 'Recepción', body: ingresoBody(o) });
add('ingreso', 'Control de ingreso — vacío', 'CU-12', ing({ foc: true }));
add('ingreso_lleno', 'Control de ingreso — RUT ingresado (socia al día)', 'CU-12', ing({ r: S.ana[0], gBtn: 'ingreso_ok', gField: 'ingreso' }));
add('ingreso_ok', 'Control de ingreso — ingreso permitido', 'CU-13', ing({ r: S.ana[0], gField: 'ingreso', res: resBox('ok', 'ok', 'Ingreso permitido', ['<b>Ana Pérez</b> · ' + S.ana[0], 'Membresía vigente hasta el 07/11/2026 (30 días).', 'Ingreso registrado a las 10:42.'], btn('Registrar siguiente', { icon: 'door', g: 'ingreso_lleno_vencido' })) }));
add('ingreso_lleno_vencido', 'Control de ingreso — RUT ingresado (socio vencido)', 'CU-12', ing({ r: S.agustin[0], gBtn: 'ingreso_denegado', gField: 'ingreso' }));
add('ingreso_denegado', 'Control de ingreso — rechazado por membresía vencida', 'CU-13', ing({ r: S.agustin[0], gField: 'ingreso', res: resBox('err', 'ban', 'Ingreso rechazado: membresía vencida', ['<b>Agustín Reyes</b> · ' + S.agustin[0], 'La membresía venció el 08/09/2026 (hace 30 días).', 'Para ingresar debe pagar la mensualidad.'], btn('Siguiente socio', { k: 'ghost', g: 'ingreso_lleno_noreg' }) + btn('Cobrar mensualidad', { icon: 'card', g: 'cobro' })) }));
add('ingreso_lleno_noreg', 'Control de ingreso — RUT de persona no registrada', 'CU-12', ing({ r: RUT_NOREG, gBtn: 'ingreso_noreg', gField: 'ingreso' }));
add('ingreso_noreg', 'Control de ingreso — RUT no registrado', 'CU-12', ing({ r: RUT_NOREG, gField: 'ingreso', res: resBox('warn', 'alert', 'RUT no registrado', [`El RUT ${RUT_NOREG} es válido, pero no pertenece a ningún socio.`, '¿Desea registrarlo como socio nuevo?'], btn('Intentar de nuevo', { k: 'ghost', g: 'ingreso' }) + btn('Registrar socio', { icon: 'plus', g: 'socio_nuevo' })) }));

// ===== CU-14/15/16 Suplementos =====
const supl = (body, over = '', title = 'Suplementos') => app({ act: 'Suplementos', title, crumb: 'Recepción', body, over });
add('supl', 'Suplementos — listado con dólar del día', 'CU-14', supl(suplBody({ banner: '' })));
add('supl_api_error', 'Suplementos — error: API del dólar no disponible', 'CU-16', supl(suplBody({ banner: alert('warn', 'No se pudo conectar con la API del dólar (mindicador.cl).', 'Se usa el último valor guardado: $948,10 del 07/10/2026. Los precios se recalcularán cuando la API responda.', { g: 'supl' }) })));
add('supl_nuevo', 'Registrar suplemento — formulario vacío', 'CU-15', supl(suplForm({ gCod: 'supl_nuevo_lleno', gUsd: 'supl_nuevo_error' }), '', 'Nuevo suplemento'));
add('supl_nuevo_lleno', 'Registrar suplemento — datos y precio CLP calculado', 'CU-15', supl(suplForm({ cod: 'PROT-05', nom: 'Proteína vegana 1 kg', usd: 'US$ 39,90', stock: '12', clp: '$37.918', gOk: 'supl_ok', gUsd: 'supl_nuevo_error' }), '', 'Nuevo suplemento'));
add('supl_nuevo_error', 'Registrar suplemento — error: precio inválido', 'CU-15', supl(suplForm({ cod: 'PROT-05', nom: 'Proteína vegana 1 kg', usd: '-39,90', stock: '12', errU: 'El costo debe ser un número mayor que 0.', gUsd: 'supl_nuevo_lleno' }), '', 'Nuevo suplemento'));
add('supl_ok', 'Registrar suplemento — guardado con éxito', 'CU-15', supl(suplBody({ banner: toast('ok', 'Suplemento guardado', 'Proteína vegana 1 kg · $37.918 (US$ 39,90 × $950,32).', 'supl'), rows: [['PROT-05', 'Proteína vegana 1 kg', 'US$ 39,90', '$37.918', '12', 'hl'], ...SUP] })));
add('venta', 'Vender suplemento — formulario vacío', 'CU-14', supl(suplBody({ banner: '' }), ventaModal({})));
add('venta_lleno', 'Vender suplemento — cantidad ingresada', 'CU-14', supl(suplBody({ banner: '' }), ventaModal({ cant: '2', total: '$85.530', gOk: 'venta_ok', gField: 'venta_error' })));
add('venta_error', 'Vender suplemento — error: stock insuficiente', 'CU-14', supl(suplBody({ banner: '' }), ventaModal({ cant: '15', err: 'Stock insuficiente: solo quedan 10 unidades.', gField: 'venta_lleno' })));
add('venta_ok', 'Vender suplemento — venta registrada', 'CU-14', supl(suplBody({ banner: toast('ok', 'Venta registrada', '2 × Proteína Whey 2 lb = $85.530. Stock restante: 8.', 'supl'), rows: [['PROT-01', 'Proteína Whey 2 lb', 'US$ 45,00', '$42.765', '8', 'hl'], ...SUP.slice(1)] })));

// ===== CU-17/18/19 Instructor =====
add('inst_ok', 'Inicio de sesión correcto — panel de la instructora', 'CU-01', instDash(toast('ok', 'Inicio de sesión correcto', '¡Bienvenida, Camila! Rol: Instructor.', 'inst_dash')));
add('inst_dash', 'Panel de la instructora (Inicio) con sidebar', 'General', instDash());
add('inst_user_menu', 'Menú de usuario de la instructora', 'CU-04', instDash('', { menu: true }));
add('mis_clases', 'Mis clases — listado con cupos por tipo', 'CU-17', app({ rol: 'I', act: 'Mis clases', title: 'Mis clases', crumb: 'Instructor', body: misClasesBody() }));
const cf = (o, t = 'Crear clase') => app({ rol: 'I', act: 'Crear clase', title: t, crumb: 'Instructor / Clases', body: claseForm(o) });
add('clase_nueva', 'Crear clase — formulario vacío', 'CU-17', cf({}));
add('clase_tipo_abierto', 'Crear clase — combobox de tipo desplegado', 'CU-17', cf({ tipoOpen: TIPOS('clase_nueva_tipo') }));
add('clase_nueva_tipo', 'Crear clase — tipo seleccionado (reglas visibles)', 'CU-17', cf({ tipo: 'Crossfit', info: infoCross }));
add('clase_dia_abierto', 'Crear clase — combobox de día desplegado', 'CU-17', cf({ tipo: 'Crossfit', diaOpen: DIAS('clase_nueva_lleno', 'clase_error'), info: infoCross }));
add('clase_nueva_lleno', 'Crear clase — formulario con datos', 'CU-17', cf({ tipo: 'Crossfit', dia: 'Viernes', hora: '19:00', gOk: 'clase_ok', info: infoCross }));
add('clase_error', 'Crear clase — error: horario ocupado', 'CU-17', cf({ tipo: 'Crossfit', dia: 'Lunes', hora: '09:00', errH: 'Ya tienes Yoga el lunes a las 09:00.', alerta: alert('err', 'Horario ocupado.', 'Un instructor no puede dictar dos clases a la misma hora. Elige otro día u hora.', { g: 'clase_nueva_tipo' }), info: infoCross }));
add('clase_ok', 'Crear clase — clase creada con éxito', 'CU-17', app({ rol: 'I', act: 'Mis clases', title: 'Mis clases', crumb: 'Instructor', body: toast('ok', 'Clase creada', 'Crossfit · viernes 19:00 · 10 cupos vendibles.', 'mis_clases') + misClasesBody(true) }));
const nom = (o) => app({ rol: 'I', act: 'Asistencia', title: 'Nómina y asistencia', crumb: 'Instructor / Asistencia', body: nominaBody(o) });
add('nomina', 'Nómina de la clase', 'CU-18', nom({ gChk: 'nomina_marcada' }));
add('nomina_clase_abierta', 'Nómina — combobox de clase desplegado', 'CU-18', nom({ gChk: 'nomina_marcada', claseOpen: [opt(`${tipoB('Yoga')} <b>Lunes 09:00</b>`, { sub: 'Hoy · 8 inscritos', sel: true, g: 'nomina' }), opt(`${tipoB('Spinning')} <b>Martes 18:00</b>`, { sub: 'Asistencia ya registrada (06/10 18:52)', hov: true, g: 'asistencia_error' }), opt(`${tipoB('Crossfit')} <b>Miércoles 20:00</b>`, { sub: '10 inscritos' }), opt(`${tipoB('Yoga')} <b>Jueves 19:00</b>`, { sub: '5 inscritos' })].join('') }));
add('nomina_marcada', 'Registrar asistencia — alumnos marcados', 'CU-19', nom({ marcados: 8, gGuardar: 'asistencia_ok', gChk: 'nomina' }));
add('asistencia_ok', 'Registrar asistencia — guardada con éxito', 'CU-19', nom({ marcados: 8, banner: toast('ok', 'Asistencia registrada', 'Yoga lunes 09:00: 7 presentes y 1 ausente.', 'inst_dash') }));
add('asistencia_error', 'Registrar asistencia — error: ya registrada', 'CU-19', nom({ banner: alert('err', 'La asistencia de Spinning martes 18:00 ya fue registrada (06/10/2026 18:52).', 'Solo se puede registrar una vez por clase y fecha. Si hay un error, contacta al administrador.', { g: 'nomina' }) }));

// ---------- CSS ----------
const CSS = `*{box-sizing:border-box;margin:0}body{width:1280px;height:800px;overflow:hidden;font-family:'Inter','Inter Variable',sans-serif;font-size:14px;color:#111827;background:#F6F7F9;-webkit-font-smoothing:antialiased}
.app{display:flex;height:800px;position:relative}.side{width:236px;background:#16181D;color:#AEB4BE;padding:20px 14px;display:flex;flex-direction:column;flex-shrink:0}
.side.mini{width:72px;align-items:center}.side.mini a{width:44px;height:44px;justify-content:center;padding:0}
.logo{display:flex;align-items:center;gap:11px;margin:0 4px 26px}.logo b{color:#fff;font-size:17px;display:block;letter-spacing:-.2px}.logo small{font-size:11.5px;color:#7E8592}
.lg{width:36px;height:36px;border-radius:10px;background:linear-gradient(135deg,#F97316,#C2410C);display:grid;place-items:center;color:#fff;flex-shrink:0}
.sect{font-size:10.5px;letter-spacing:1.2px;color:#6B7280;margin:0 10px 8px;font-weight:600}
.side a{display:flex;align-items:center;gap:11px;padding:10px 12px;border-radius:9px;margin-bottom:3px;font-weight:500;color:#C3C8D0}.side a.on{background:rgba(249,115,22,.16);color:#FDBA74}
.sfoot{margin-top:auto}.tip{display:flex;gap:8px;align-items:center;font-size:11.5px;color:#7E8592;padding:10px;border:1px solid #2A2E36;border-radius:9px}
.main{flex:1;display:flex;flex-direction:column;min-width:0}.top{height:68px;background:#fff;border-bottom:1px solid #E5E7EB;display:flex;align-items:center;gap:14px;padding:0 28px;flex-shrink:0}
.top h1{font-size:19px;letter-spacing:-.3px}.crumb{font-size:12px;color:#6B7280;margin-bottom:1px}.sp{flex:1}
.chip{display:flex;align-items:center;gap:7px;padding:7px 12px;border-radius:99px;background:#F0FDF4;color:#166534;font-size:12.5px;border:1px solid #BBF7D0}
.user{display:flex;align-items:center;gap:10px;padding:5px 10px 5px 5px;border-radius:10px;border:1px solid #E5E7EB}.user b{font-size:13px;display:block}.user small{font-size:11.5px;color:#6B7280}
.av{width:34px;height:34px;border-radius:50%;background:#FFEDD5;color:#C2410C;display:grid;place-items:center;font-weight:700;font-size:13px}
.ibtn{width:36px;height:36px;display:inline-grid;place-items:center;border-radius:9px;border:1px solid #E5E7EB;color:#374151;background:#fff}.ibtn.ham{border:none}
.content{padding:22px 28px;flex:1;overflow:hidden;position:relative}
.card{background:#fff;border:1px solid #E5E7EB;border-radius:14px;margin-bottom:16px}.ch{display:flex;align-items:center;margin-bottom:14px}.ch h3{font-size:15px;flex:1}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-bottom:16px}.kpi{background:#fff;border:1px solid #E5E7EB;border-radius:14px;padding:16px;display:flex;gap:14px;align-items:center}
.kic{width:42px;height:42px;border-radius:11px;display:inline-grid;place-items:center;flex-shrink:0}.kic.big{width:60px;height:60px;border-radius:16px;margin-bottom:14px}
.or{background:#FFEDD5;color:#C2410C}.rd{background:#FEE2E2;color:#B91C1C}.gr{background:#DCFCE7;color:#15803D}.bl{background:#DBEAFE;color:#1D4ED8}
.kt{font-size:12.5px;color:#6B7280}.kv{font-size:22px;font-weight:700;letter-spacing:-.4px}.ks{font-size:11.5px;color:#9CA3AF}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid2.w60{grid-template-columns:1.35fr 1fr}.grid2>.card{margin-bottom:16px}
.qa{display:flex;flex-wrap:wrap;gap:10px}.next{display:flex;align-items:center;gap:12px;padding:12px;border:1px solid #F1F2F4;border-radius:11px;margin-bottom:10px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;height:42px;padding:0 16px;border-radius:9px;font:600 14px Inter,sans-serif;border:1px solid transparent;white-space:nowrap}
.btn.pri{background:#EA580C;color:#fff}.btn.ghost{background:#fff;border-color:#D1D5DB;color:#1F2937}.btn.dan{background:#DC2626;color:#fff}.btn.sm{height:32px;padding:0 11px;font-size:12.5px}
.btn.dis{opacity:.45}.btn.pri.dis{background:#9CA3AF}
.fld{margin-bottom:15px;width:100%}.fld label{display:block;font-size:13px;font-weight:600;color:#374151;margin-bottom:6px}
.inp{height:44px;border:1px solid #D1D5DB;border-radius:9px;display:flex;align-items:center;gap:9px;padding:0 12px;background:#fff;position:relative}
.inp .val{flex:1;white-space:nowrap;overflow:hidden;display:flex;align-items:center;gap:4px}.inp .ic{color:#9CA3AF;display:flex}.ph{color:#9CA3AF}
.inp.focus{border-color:#F97316;box-shadow:0 0 0 3px rgba(249,115,22,.18)}.inp.err{border-color:#DC2626;box-shadow:0 0 0 3px rgba(220,38,38,.12)}.inp.okb{border-color:#16A34A}.inp.ro{background:#F9FAFB}
.erric{color:#DC2626;display:flex}.okic{color:#16A34A;display:flex}.chev{color:#6B7280;display:flex}
.caret{width:1.5px;height:19px;background:#111;margin-left:-6px}
.msg{font-size:12.5px;color:#6B7280;margin-top:6px;display:flex;gap:5px;align-items:center}.msg.e{color:#DC2626;font-weight:500}
.rel{position:relative}.dd{position:absolute;left:0;right:0;top:calc(100% + 6px);background:#fff;border:1px solid #E5E7EB;border-radius:11px;box-shadow:0 12px 32px rgba(17,24,39,.16);padding:6px;z-index:20}
.opt{padding:9px 11px;border-radius:8px;display:flex;align-items:center;gap:10px;justify-content:space-between}.opt>div:first-child{flex:1}.opt .sub{font-size:12px;color:#6B7280;margin-top:2px}
.opt.hov{background:#FFF7ED;outline:1px solid #FED7AA}.opt.dis{opacity:.75}.opt.dis .sub{color:#B91C1C}.tick{color:#EA580C;display:flex}
.ddsearch{display:flex;align-items:center;gap:7px;padding:9px 11px;border-bottom:1px solid #F1F2F4;margin:-2px -2px 6px;color:#6B7280}
.umenu{left:auto;width:250px}.uhead{padding:8px 11px}.uhead b{display:block}.uhead span{font-size:12px;color:#6B7280}.sep{height:1px;background:#F1F2F4;margin:4px 0}.row{display:flex;gap:9px;align-items:center;color:#B91C1C;font-weight:600}
.badge{display:inline-flex;align-items:center;padding:3px 9px;border-radius:99px;font-size:12px;font-weight:600;white-space:nowrap}
.badge.g{background:#DCFCE7;color:#166534}.badge.r{background:#FEE2E2;color:#991B1B}.badge.y{background:#FEF3C7;color:#92400E}.badge.v{background:#EDE9FE;color:#5B21B6}.badge.b{background:#DBEAFE;color:#1E40AF}.badge.o{background:#FFEDD5;color:#9A3412}.badge.n{background:#F3F4F6;color:#4B5563}
.tb{width:100%;border-collapse:collapse}.tb th{text-align:left;font-size:12px;color:#6B7280;font-weight:600;padding:10px 10px;border-bottom:1px solid #E5E7EB;background:#F9FAFB}
.tb td{padding:11px 10px;border-bottom:1px solid #F1F2F4;vertical-align:middle}.tb tr.hl td{background:#FFF7ED}.tb tr.hl2 td{background:#F7FEF9}.mono{font-variant-numeric:tabular-nums;color:#374151}
.tools{display:flex;align-items:center;gap:12px;margin-bottom:14px}.tools .fld{margin-bottom:0}.tfoot{font-size:12px;color:#9CA3AF;margin-top:10px}
.fchip{display:inline-flex;align-items:center;gap:6px;background:#FFEDD5;color:#9A3412;border-radius:99px;padding:6px 10px;font-size:12.5px;font-weight:600}
.alert{display:flex;gap:12px;padding:13px 14px;border-radius:11px;border:1px solid;margin-bottom:16px;align-items:flex-start}.alert .atx{flex:1;font-size:13.5px}.alert .atx div{margin-top:2px;opacity:.9}
.alert.ok{background:#F0FDF4;border-color:#BBF7D0;color:#166534}.alert.err{background:#FEF2F2;border-color:#FECACA;color:#991B1B}.alert.warn{background:#FFFBEB;border-color:#FDE68A;color:#92400E}.alert.info{background:#EFF6FF;border-color:#BFDBFE;color:#1E40AF}
.aic{display:flex;margin-top:1px}.ax{display:flex;opacity:.7;padding:2px}
.toast{position:absolute;top:16px;right:28px;width:400px;background:#fff;border:1px solid #E5E7EB;border-left:4px solid #16A34A;border-radius:12px;box-shadow:0 14px 34px rgba(17,24,39,.18);display:flex;gap:12px;padding:14px;z-index:30}
.toast .aic{color:#16A34A}.toast .atx{flex:1;font-size:13.5px}.toast .atx div{color:#4B5563;margin-top:2px}
.row2{display:flex;gap:14px;align-items:flex-start}.row2>.fld{flex:1}.row2>.btn{margin-top:0;height:44px}
.empty{display:flex;flex-direction:column;align-items:center;gap:6px;padding:34px 10px;color:#9CA3AF;text-align:center}.empty b{color:#4B5563}.empty span{font-size:12.5px}
.tot{display:flex;justify-content:space-between;align-items:center;padding:14px 4px 4px;margin-top:6px;border-top:1px dashed #E5E7EB}.tot b{font-size:22px;letter-spacing:-.4px}
.acts{display:flex;gap:10px;justify-content:flex-end;margin-top:18px}.acts.c{justify-content:center}.acts.l{justify-content:flex-start;margin-top:14px}
.muted{color:#6B7280}.narrow{max-width:760px}.note{display:flex;gap:8px;align-items:center;background:#F9FAFB;border:1px solid #F1F2F4;padding:10px 12px;border-radius:9px;font-size:13px;color:#4B5563}
.sum>div{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #F1F2F4;gap:12px}.sum span{color:#6B7280}.sum>div.big b{font-size:20px}.sum>div.big{border-bottom:none}
.radio{width:18px;height:18px;border-radius:50%;border:2px solid #9CA3AF;display:inline-block}.radio.on{border:5px solid #EA580C}
.res{display:flex;gap:18px;padding:20px;border-radius:14px;margin-top:6px;border:1px solid}.res h2{font-size:19px;margin-bottom:6px}.res div>div{margin-bottom:3px}
.res.ok{background:#F0FDF4;border-color:#86EFAC;color:#14532D}.res.err{background:#FEF2F2;border-color:#FCA5A5;color:#7F1D1D}.res.warn{background:#FFFBEB;border-color:#FCD34D;color:#78350F}.ric{display:flex}
.dolar{display:flex;gap:11px;align-items:center}.dolar small{display:block;color:#6B7280;font-size:12px}
.calc>div{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #F1F2F4}.calc span{color:#6B7280}.calc .big b{font-size:24px;color:#C2410C}.calc .big{border:none}
.chk{display:flex;color:#9CA3AF}.chk.on{color:#16A34A}
.denied{display:flex;justify-content:center;padding-top:40px}.denied .card{width:600px;text-align:center}.denied h2{font-size:21px;margin-bottom:8px;letter-spacing:-.3px}.denied p{line-height:1.6}
.ovl{position:absolute;inset:0;background:rgba(17,24,39,.5);z-index:40}.modal{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);background:#fff;border-radius:16px;padding:24px;z-index:41;box-shadow:0 24px 60px rgba(0,0,0,.3)}
.mh{display:flex;align-items:center;margin-bottom:12px}.mh h3{flex:1;font-size:17px}.mc{text-align:center}.mc h3{font-size:19px;margin-bottom:6px}
.recibo{border:1px dashed #D1D5DB;border-radius:11px;padding:14px 16px}.rlogo{display:flex;gap:9px;align-items:center;margin-bottom:6px}.rlogo .lg{width:28px;height:28px;border-radius:8px}
.login{display:flex;height:800px}.lpanel{width:560px;background:radial-gradient(circle at 20% 0%,#3B1D0E 0,#16181D 55%);color:#E5E7EB;padding:48px 52px;display:flex;flex-direction:column}
.logo.big b{font-size:21px}.logo.big .lg{width:46px;height:46px;border-radius:13px}.lpanel h2{font-size:30px;line-height:1.25;letter-spacing:-.6px;margin:70px 0 30px;color:#fff;font-weight:700}
.lpanel ul{list-style:none;padding:0}.lpanel li{display:flex;gap:12px;align-items:center;margin-bottom:16px;color:#C9CDD3;font-size:15px}.lpanel li svg{color:#FB923C}.lfoot{margin-top:auto;font-size:12.5px;color:#7E8592}
.lform{flex:1;display:grid;place-items:center;background:#fff}.fcard{width:360px}.fcard h1{font-size:26px;letter-spacing:-.5px;margin-bottom:6px}.fcard .sub{color:#6B7280;margin-bottom:24px}
.lrow{display:flex;justify-content:flex-end;margin:-4px 0 18px}.lrow.c{justify-content:center;margin:18px 0 0}.lnk{color:#C2410C;font-weight:600;font-size:13.5px}.lhelp{display:flex;gap:7px;align-items:center;font-size:12px;color:#9CA3AF;margin-top:18px;justify-content:center}`;

(async () => {
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1.5 });
  const ids = new Set(SC.map(s => s.id)); const mapa = []; const faltan = [];
  for (let i = 0; i < SC.length; i++) {
    const s = SC[i]; s.n = 'M' + String(i + 1).padStart(2, '0');
  }
  const num = Object.fromEntries(SC.map(s => [s.id, s.n]));
  for (const s of SC) {
    await pg.setContent(`<!doctype html><html><head><meta charset="utf-8"><style>${CSS}</style></head><body>${s.html}</body></html>`);
    await pg.evaluate(() => document.fonts.ready);
    const hs = await pg.$$eval('[data-go]', els => els.map(e => { const r = e.getBoundingClientRect(); return { go: e.dataset.go, x: Math.round(r.x), y: Math.round(r.y), w: Math.round(r.width), h: Math.round(r.height), t: (() => { const c = e.classList; const lab = e.closest('.fld')?.querySelector('label')?.innerText.replace(/[*\s]+$/, ''); if (c.contains('inp')) return (c.contains('sel') ? 'Combobox ' : 'Campo ') + (lab && lab.trim() ? '«' + lab.trim() + '»' : '«' + (e.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 40) + '»'); if (c.contains('opt')) return 'Opción «' + e.innerText.trim().replace(/\s+/g, ' ').slice(0, 45) + '»'; if (c.contains('ham')) return 'Botón menú ☰'; if (c.contains('ovl')) return 'Clic fuera del cuadro'; if (c.contains('ax')) return 'Botón cerrar ×'; if (c.contains('radio')) return 'Selector de fila (círculo)'; if (c.contains('chk')) return 'Casilla de asistencia'; if (c.contains('user')) return 'Menú de usuario (avatar)'; if (e.closest('.side.mini')) return 'Ícono del menú lateral'; if (e.title) return e.title; const t = (e.innerText || e.getAttribute('title') || '').trim().replace(/\s+/g, ' ').slice(0, 60); return t ? (c.contains('btn') ? 'Botón «' + t + '»' : c.contains('lnk') ? 'Enlace «' + t + '»' : e.closest('nav') ? 'Menú «' + t + '»' : '«' + t + '»') : 'Ícono'; })(), nav: !!e.closest('aside,header') }; }));
    hs.forEach(h => { if (!ids.has(h.go)) faltan.push(s.id + ' -> ' + h.go); h.dest = num[h.go]; });
    const file = `${s.n}_${s.id}.png`;
    await pg.screenshot({ path: OUT + file });
    fs.mkdirSync(OUT + '../jpg', { recursive: true }); await pg.screenshot({ path: OUT + '../jpg/' + s.n + '.jpg', type: 'jpeg', quality: 80, scale: 'css' });
    mapa.push({ n: s.n, id: s.id, nombre: s.nombre, cu: s.cu, file, hotspots: hs });
  }
  // pantallas a las que nadie llega
  const llegan = new Set(mapa.flatMap(m => m.hotspots.map(h => h.go)));
  const huerfanas = SC.filter(s => !llegan.has(s.id) && s.id !== 'login').map(s => s.id);
  fs.writeFileSync(OUT + '../mapa.json', JSON.stringify(mapa, null, 1));
  console.log('pantallas', SC.length, 'destinos inexistentes', faltan, 'huérfanas', huerfanas);
  await b.close();
})();
