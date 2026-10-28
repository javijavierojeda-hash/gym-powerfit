# Plan web — chilemarmol.cl

Empresa de muebles, proyectos y artículos decorativos en mármol y piedras preciosas.
Objetivo: sitio moderno con scroll narrativo, mucho blanco y tipografía manuscrita + sans.

> **Para la nueva sesión:** lee este archivo completo y sigue el plan.
> Primer entregable: prototipo del Hero + la "veta" animada (sección 3).
> Usa el MCP de 21st.dev (servidor `21st`, clave en `API_KEY_21ST`) para buscar
> componentes base y adáptalos SIEMPRE a la paleta y tipografías de este plan.

---

## 0. Pendientes detectados

- **Dominio:** chilemarmol.cl no resolvía DNS al investigar → verificar en nic.cl si está registrado.
- **Repositorio:** crear un repo propio `chilemarmol` (no mezclar con gym-powerfit) y mover ahí `.mcp.json`.
- **merlino.cl:** no se pudo revisar (bloqueado por red). La técnica de scroll de este plan es distinta a propósito.
- **Seguridad:** la API key de 21st.dev que se pegó en el chat debe estar rotada; la vigente vive solo en el secreto del entorno `API_KEY_21ST`.

## 1. Concepto: "La veta"

Hilo conductor de toda la web: **una veta de mármol (SVG fino, gris/latón) que se dibuja mientras haces scroll**, conectando secciones y guiando la vista.
Por qué: la animación nace del producto (el mármol), no es un adorno genérico → identidad propia y difícil de copiar.

## 2. Arquitectura del sitio

```
Inicio (one-page con scroll narrativo)
 ├─ Hero: pieza de mármol en macro + título manuscrito
 ├─ Manifiesto: "Piedra con historia" (texto grande que se revela por líneas)
 ├─ Colecciones: galería horizontal pinneada (Muebles · Mesas · Decoración · Piedras preciosas)
 ├─ Materiales: Carrara, Travertino, Negro Marquina, Lapislázuli chileno…
 ├─ Proceso / Taller: de la cantera a tu casa (4 pasos)
 ├─ Proyectos: casos reales con antes/después
 └─ Contacto / Cotiza (WhatsApp + formulario)
Internas: /colecciones/[categoria], /proyectos/[slug], /nosotros
```

Diferenciador: Chile es uno de los pocos países con **lapislázuli** → sección destacada si la empresa lo trabaja.

## 3. Técnicas de scroll (una por sección, sin saturar)

| Sección | Efecto | Herramienta |
|---|---|---|
| Global | Scroll suave con inercia | Lenis |
| Hero | Zoom lento a la imagen + título letra a letra | GSAP + SplitText |
| Manifiesto | Palabras pasan de gris a negro al leerlas | ScrollTrigger `scrub` |
| Colecciones | Sección fija, piezas avanzan en horizontal | ScrollTrigger `pin` |
| Materiales | Imágenes se abren como losa partida | `clip-path` + GSAP |
| Veta conductora | SVG se dibuja según el progreso del scroll | `stroke-dashoffset` |
| Proyectos | Parallax suave de 2 capas | ScrollTrigger |

Reglas:
- **Móvil:** sin pin horizontal ni scroll-jacking; versiones simplificadas.
- **`prefers-reduced-motion`:** la web se ve completa sin animaciones.

## 4. Tipografía

- **Manuscrita (solo acentos, máx. ~10% del texto):** Corinthia o Pinyon Script.
- **Sans (todo lo demás):** Manrope o General Sans.
- Combinación tipo: "Piezas que *perduran*" — la palabra clave en manuscrita, más grande, montada sobre la sans.

## 5. Paleta (design tokens)

| Token | Color | Uso |
|---|---|---|
| `--marmol` | `#FAF8F5` | Fondo principal (blanco cálido) |
| `--blanco` | `#FFFFFF` | Tarjetas / contraste |
| `--piedra` | `#1C1B19` | Textos |
| `--veta` | `#8C8A85` | Líneas, textos secundarios |
| `--laton` | `#B08D57` | Acento: botones, veta animada |
| `--lapislazuli` | `#26619C` | Acento solo en sección piedras preciosas |

Por qué blanco cálido: el `#FFF` puro cansa y se ve "plantilla"; el cálido se parece al mármol real y realza las fotos.

## 6. Stack

- **Astro** (HTML estático → muy rápido y buen SEO; escala a catálogo).
- **GSAP + ScrollTrigger + SplitText** (100% gratis desde 2025) + **Lenis**.
- **Tailwind CSS** con los tokens de la sección 5.
- **21st.dev (MCP)** para componentes base, siempre adaptados a la marca.
- **CMS:** Decap o Sanity para que la empresa suba productos/proyectos.
- **Hosting:** Vercel o Netlify (HTTPS + CDN).

## 7. Seguridad y rendimiento

- Formulario con honeypot + Cloudflare Turnstile y validación en servidor.
- Headers: CSP, HSTS, X-Frame-Options. Nunca API keys en el cliente ni en el repo.
- Imágenes AVIF/WebP con `srcset` y lazy loading (las fotos son el mayor peso).
- Metas: LCP < 2.5 s, CLS < 0.1; precargar imagen del hero.
- SEO local: JSON-LD `LocalBusiness`, Google Business Profile, Open Graph.

## 8. Fases

1. Brief y contenido (logo, fotos macro profesionales, catálogo, textos).
2. Diseño (wireframe → prototipo HTML/Figma).
3. Desarrollo (maqueta → animaciones → CMS).
4. QA (celulares reales, accesibilidad, Lighthouse).
5. Lanzamiento (dominio, analítica, Search Console, Google Business).

## 9. Preguntas abiertas para el cliente

1. ¿Tienen logo y fotos de sus piezas, o usamos imágenes de referencia?
2. ¿Solo catálogo + cotización por WhatsApp, o tienda online con pago (Webpay / Mercado Pago)?
3. ¿El dominio ya está comprado?
