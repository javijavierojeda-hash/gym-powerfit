# chilemarmol.cl — Sitio web (v1)

Sitio estático (HTML + CSS + JS, sin build) con scroll suave y animaciones ligadas al scroll.

## Ver en local
```bash
cd chilemarmol
python3 -m http.server 8080
# abrir http://localhost:8080
```

## Páginas
| Archivo | Qué es |
|---|---|
| `index.html` | Home: hero, manifiesto, especialidades, 6 proyectos, proceso, cifras, servicios, contacto |
| `proyectos.html` | Los 18 proyectos con filtros por categoría (`?cat=cocinas`) |
| `proyecto.html` | Detalle de un proyecto (`?p=cocina-lo-barnechea`) |

## Cómo cambiar contenido (todo en `assets/js/data.js`)
- **WhatsApp:** `SITE.whatsapp` → número real en formato `569XXXXXXXX`.
- **Cifras:** `SITE.stats` (hoy son de ejemplo, confirmar antes de publicar).
- **Proyectos:** cada uno tiene título, ubicación, año, superficie, servicios, resumen e imágenes.
  - `featured: true` lo muestra en el Home (máximo 6).
- **Imágenes propias:** copia la foto en `assets/img/` y en `images` usa la ruta, ej. `"assets/img/cocina-1.jpg"`.
  Recomendado: JPG/WebP de 2000 px de ancho, menos de 400 KB.

## Tecnología y decisiones
- **GSAP + ScrollTrigger + Lenis** alojados en `assets/vendor/` (no CDN): más rápido y sin scripts de terceros.
- **Content-Security-Policy** en cada página: solo se ejecutan scripts propios.
- Los datos se insertan con métodos DOM (sin `innerHTML`): evita inyección de HTML.
- **Accesible:** respeta "reducir movimiento", funciona sin JavaScript, menú con teclado (Esc cierra).
- Proceso horizontal fijado solo en pantallas ≥1024 px; en celular es vertical.

## Pendientes
- Número de WhatsApp, email, Instagram, dirección del mapa (`SITE.address` y `SITE.mapQuery`) y cifras reales.
- Fotos y video propios (el hero acepta video fácilmente).
- Logo definitivo (hoy es texto).
- Dominio y hosting (Netlify/Vercel), y mover esta carpeta a un repo propio `chilemarmol`.
