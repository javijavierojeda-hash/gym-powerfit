/* ==========================================================================
   Chile Mármol — Datos del sitio
   Este es el ÚNICO archivo que necesitas editar para cambiar contenido:
   número de WhatsApp, cifras, categorías y proyectos.
   ========================================================================== */

/* Configuración general.
   PENDIENTE: reemplazar el número de WhatsApp y las cifras por los reales. */
window.SITE = {
  name: "Chile Mármol",
  // Formato internacional sin "+", espacios ni guiones (ej: 56912345678).
  whatsapp: "56900000000",
  whatsappMessage: "Hola Chile Mármol, quiero cotizar un proyecto de remodelación.",
  email: "contacto@chilemarmol.cl",
  city: "Santiago, Chile",
  // PENDIENTE: dirección real del showroom/taller (se usa en el mapa).
  address: "Santiago, Chile",
  mapQuery: "Santiago, Chile",
  hours: "Lunes a viernes · 9:00 a 18:30",
  instagram: "https://www.instagram.com/",
  // PENDIENTE: cifras de ejemplo, confirmar con la empresa antes de publicar.
  stats: [
    { value: 120, prefix: "+", suffix: "", label: "Proyectos entregados" },
    { value: 15, prefix: "", suffix: "", label: "Años de experiencia" },
    { value: 6, prefix: "", suffix: "", label: "Especialidades" },
    { value: 100, prefix: "", suffix: "%", label: "Diseñado a medida" },
  ],
};

/* Imágenes genéricas (Unsplash) por ahora.
   Para usar fotos propias: pon el archivo en assets/img/ y en el proyecto
   reemplaza la referencia por la ruta, ej: "assets/img/cocina-vitacura.jpg". */
window.img = function (ref, width) {
  if (ref.indexOf("/") !== -1) return ref; // ruta local
  return "https://images.unsplash.com/photo-" + ref + "?auto=format&fit=crop&q=80&w=" + width;
};

/* Opciones del cotizador (el tipo de proyecto sale de CATEGORIES) */
window.QUOTE = {
  materials: ["Mármol", "Granito", "Cuarzo", "Porcelanato", "Madera", "Aún no lo sé"],
  timing: ["Lo antes posible", "1 a 3 meses", "3 a 6 meses", "Solo estoy cotizando"],
};

window.CATEGORIES = [
  { slug: "empresas", name: "Empresas", lead: "Casas matrices, showrooms y espacios de marca que comunican quién eres." },
  { slug: "locales", name: "Locales comerciales", lead: "Retail y gastronomía pensados para vender desde la vitrina." },
  { slug: "oficinas", name: "Oficinas", lead: "Espacios de trabajo que mejoran la forma en que trabaja tu equipo." },
  { slug: "cocinas", name: "Cocinas", lead: "Cocinas a medida en mármol, cuarzo y piedra natural." },
  { slug: "inmobiliarias", name: "Inmobiliarias", lead: "Pilotos, áreas comunes y terminaciones para proyectos en venta." },
  { slug: "hogares", name: "Hogares", lead: "Remodelaciones integrales de casas y departamentos." },
];

/* Proyectos de ejemplo. `featured: true` = aparece en el Home (máx. 6). */
window.PROJECTS = [
  // ── Empresas ───────────────────────────────────────────────────────────
  {
    slug: "casa-matriz-andes", category: "empresas", featured: true,
    title: "Casa Matriz Andes", location: "Las Condes", year: 2025, area: "1.200 m²",
    services: ["Arquitectura interior", "Obra civil", "Mobiliario a medida"],
    summary: "Remodelación completa de tres pisos corporativos con recepción en mármol travertino y salas de directorio a medida.",
    challenge: "La empresa crecía y sus tres pisos tenían distribuciones distintas, recepción poco representativa y salas que no daban abasto.",
    solution: "Unificamos los tres niveles con un mismo lenguaje: recepción en travertino, salas de directorio con acústica y mobiliario fabricado en nuestro taller.",
    result: "Una sede que recibe clientes con la misma calidad que la marca promete, entregada sin detener la operación.",
    materials: ["Travertino", "Roble natural", "Vidrio acústico"],
    duration: "16 semanas",
    images: ["1486406146926-c627a92ad1ab", "1517502884422-41eaead166d4", "1497366754035-f200968a6e72"],
  },
  {
    slug: "showroom-vitacura", category: "empresas",
    title: "Showroom Vitacura", location: "Vitacura", year: 2024, area: "420 m²",
    services: ["Diseño de experiencia", "Iluminación", "Revestimientos en piedra"],
    summary: "Un showroom que funciona como galería: muros en piedra natural, iluminación escénica y circulación fluida.",
    challenge: "Exhibir productos de alto valor en un local sin luz natural y con una circulación confusa.",
    solution: "Diseñamos un recorrido tipo galería con muros en piedra natural e iluminación escénica regulable por zona.",
    result: "El tiempo promedio de visita aumentó y el espacio se usa también para eventos de la marca.",
    materials: ["Piedra natural", "Microcemento", "Iluminación LED"],
    duration: "10 semanas",
    images: ["1586023492125-27b2c045efd7", "1513694203232-719a280e022f", "1618221195710-dd6b41faaea6"],
  },
  {
    slug: "lobby-nueva-las-condes", category: "empresas",
    title: "Lobby Nueva Las Condes", location: "Las Condes", year: 2023, area: "380 m²",
    services: ["Arquitectura interior", "Pavimentos de mármol", "Gestión de obra"],
    summary: "Renovación de lobby corporativo con pavimento de mármol continuo y mesón de recepción tallado en una sola pieza.",
    challenge: "Un lobby de alto tráfico con pavimento desgastado y una recepción que no transmitía la categoría del edificio.",
    solution: "Pavimento continuo de mármol con juntas mínimas y un mesón de recepción tallado en una sola pieza en nuestro taller.",
    result: "Un acceso renovado que soporta el tráfico diario y fue ejecutado por etapas para no cerrar el edificio.",
    materials: ["Mármol Crema Marfil", "Acero inoxidable", "Madera"],
    duration: "8 semanas",
    images: ["1618219908412-a29a1bb7b86e", "1497366754035-f200968a6e72", "1517502884422-41eaead166d4"],
  },

  // ── Locales comerciales ────────────────────────────────────────────────
  {
    slug: "boutique-alonso-de-cordova", category: "locales", featured: true,
    title: "Boutique Alonso de Córdova", location: "Vitacura", year: 2025, area: "160 m²",
    services: ["Diseño de retail", "Mobiliario a medida", "Obra"],
    summary: "Tienda de moda con exhibidores en mármol blanco y una vitrina pensada para detener a quien pasa.",
    challenge: "Una vitrina que pasaba desapercibida y un interior que no permitía exhibir toda la colección.",
    solution: "Exhibidores modulares en mármol blanco, vitrina con iluminación propia y probadores más amplios.",
    result: "Más visitas desde la calle y una tienda que cambia de layout en minutos según la temporada.",
    materials: ["Mármol Carrara", "Latón", "Espejo"],
    duration: "6 semanas",
    images: ["1567401893414-76b7b1e5a7a5", "1441986300917-64674bd600d8", "1586023492125-27b2c045efd7"],
  },
  {
    slug: "restaurante-lastarria", category: "locales",
    title: "Restaurante Lastarria", location: "Santiago Centro", year: 2024, area: "240 m²",
    services: ["Arquitectura interior", "Barra en piedra", "Iluminación"],
    summary: "Restaurante de autor con barra de 9 metros en granito negro y salón de doble altura.",
    challenge: "Abrir un restaurante en un edificio antiguo, con plazos ajustados y normativa sanitaria exigente.",
    solution: "Gestionamos permisos, reforzamos la estructura y construimos una barra de 9 metros en granito negro.",
    result: "El restaurante abrió en la fecha comprometida y la barra se convirtió en su imagen en redes sociales.",
    materials: ["Granito negro", "Ladrillo recuperado", "Acero"],
    duration: "12 semanas",
    images: ["1555396273-367ea4eb4db5", "1617806118233-18e1de247200", "1564078516393-cf04bd966897"],
  },
  {
    slug: "cafe-italia", category: "locales",
    title: "Café Barrio Italia", location: "Providencia", year: 2023, area: "90 m²",
    services: ["Diseño integral", "Mesones a medida", "Obra"],
    summary: "Cafetería de barrio con mesones de mármol Carrara y un layout que duplicó su capacidad.",
    challenge: "Un local pequeño donde cabían pocas mesas y la barra quedaba escondida.",
    solution: "Rediseñamos la planta para llevar la barra al frente y fabricamos mesones de mármol a medida.",
    result: "La capacidad se duplicó y el café ganó una fachada reconocible en el barrio.",
    materials: ["Mármol Carrara", "Madera de pino", "Cerámica artesanal"],
    duration: "5 semanas",
    images: ["1617806118233-18e1de247200", "1555396273-367ea4eb4db5", "1615529182904-14819c35db37"],
  },

  // ── Oficinas ───────────────────────────────────────────────────────────
  {
    slug: "oficinas-nueva-costanera", category: "oficinas", featured: true,
    title: "Oficinas Nueva Costanera", location: "Vitacura", year: 2025, area: "850 m²",
    services: ["Space planning", "Habilitación", "Mobiliario"],
    summary: "Habilitación de planta libre para 90 personas: zonas de foco, salas colaborativas y una cafetería central.",
    challenge: "Pasar a una planta libre para 90 personas sin perder concentración ni privacidad.",
    solution: "Zonificamos en áreas de foco, colaboración y encuentro, con salas vidriadas y una cafetería central.",
    result: "Un espacio que el equipo usa todos los días y que redujo la demanda de salas de reunión.",
    materials: ["Alfombra modular", "Vidrio templado", "Cuarzo"],
    duration: "14 semanas",
    images: ["1531973576160-7125cd663d86", "1504384308090-c894fdcc538d", "1497366811353-6870744d04b2"],
  },
  {
    slug: "estudio-juridico-isidora", category: "oficinas",
    title: "Estudio Jurídico Isidora", location: "Las Condes", year: 2024, area: "520 m²",
    services: ["Arquitectura interior", "Acústica", "Carpintería fina"],
    summary: "Oficinas de un estudio jurídico con salas acústicas, madera noble y recepción en piedra.",
    challenge: "Un estudio jurídico que necesitaba confidencialidad total en reuniones y una imagen sobria.",
    solution: "Salas con aislación acústica certificada, carpintería fina en nogal y recepción en piedra.",
    result: "Oficinas silenciosas y elegantes que refuerzan la confianza de sus clientes.",
    materials: ["Nogal", "Piedra caliza", "Paneles acústicos"],
    duration: "11 semanas",
    images: ["1517502884422-41eaead166d4", "1497215728101-856f4ea42174", "1497366754035-f200968a6e72"],
  },
  {
    slug: "cowork-providencia", category: "oficinas",
    title: "Cowork Providencia", location: "Providencia", year: 2023, area: "640 m²",
    services: ["Diseño integral", "Obra civil", "Equipamiento"],
    summary: "Reconversión de una casona en cowork flexible manteniendo su estructura original.",
    challenge: "Convertir una casona antigua en cowork sin perder su valor patrimonial.",
    solution: "Mantuvimos la estructura original y sumamos instalaciones nuevas, mobiliario flexible y salas modulares.",
    result: "Un cowork con identidad propia que alcanzó alta ocupación en sus primeros meses.",
    materials: ["Madera recuperada", "Acero negro", "Porcelanato"],
    duration: "12 semanas",
    images: ["1524758631624-e2822e304c36", "1497366811353-6870744d04b2", "1497366216548-37526070297c"],
  },

  // ── Cocinas ────────────────────────────────────────────────────────────
  {
    slug: "cocina-lo-barnechea", category: "cocinas", featured: true,
    title: "Cocina Lo Barnechea", location: "Lo Barnechea", year: 2025, area: "38 m²",
    services: ["Diseño de cocina", "Isla en mármol", "Muebles a medida"],
    summary: "Cocina abierta con isla de 3,6 metros en mármol Calacatta y muebles de piso a cielo.",
    challenge: "Una cocina cerrada y oscura en una casa familiar donde la vida pasa alrededor de la mesa.",
    solution: "Abrimos la cocina al living con una isla de 3,6 metros en Calacatta y muebles de piso a cielo hechos a medida.",
    result: "La cocina pasó a ser el corazón de la casa, con más guardado y luz natural.",
    materials: ["Mármol Calacatta", "Madera enchapada", "Herrajes de cierre suave"],
    duration: "7 semanas",
    images: ["1622372738946-62e02505feb3", "1556912173-3bb406ef7e77", "1484154218962-a197022b5858"],
  },
  {
    slug: "cocina-la-reina", category: "cocinas",
    title: "Cocina La Reina", location: "La Reina", year: 2024, area: "24 m²",
    services: ["Diseño de cocina", "Cubiertas de cuarzo", "Obra"],
    summary: "Integración de cocina y comedor con cubiertas de cuarzo y carpintería en roble.",
    challenge: "Integrar cocina y comedor en un departamento con poco espacio de guardado.",
    solution: "Diseñamos muebles altos hasta el cielo y cubiertas de cuarzo resistentes al uso diario.",
    result: "Una cocina luminosa, fácil de mantener y con el doble de capacidad de guardado.",
    materials: ["Cuarzo blanco", "Roble", "Cerámica"],
    duration: "5 semanas",
    images: ["1556911220-bff31c812dba", "1556912173-3bb406ef7e77", "1600489000022-c2086d79f9d4"],
  },
  {
    slug: "cocina-chicureo", category: "cocinas",
    title: "Cocina Chicureo", location: "Chicureo", year: 2023, area: "30 m²",
    services: ["Diseño de cocina", "Piedra natural", "Electrodomésticos"],
    summary: "Cocina familiar con mesón en granito, despensa oculta y zona de desayuno.",
    challenge: "Una familia grande que necesitaba una cocina práctica para cocinar todos los días.",
    solution: "Mesón en granito, despensa oculta tras puertas a medida y una zona de desayuno integrada.",
    result: "Una cocina robusta, ordenada y pensada para durar muchos años.",
    materials: ["Granito gris", "Melamina premium", "Cerámica subway"],
    duration: "6 semanas",
    images: ["1600489000022-c2086d79f9d4", "1484154218962-a197022b5858", "1556911220-bff31c812dba"],
  },

  // ── Inmobiliarias ──────────────────────────────────────────────────────
  {
    slug: "edificio-parque-araucano", category: "inmobiliarias", featured: true,
    title: "Edificio Parque Araucano", location: "Las Condes", year: 2025, area: "64 unidades",
    services: ["Terminaciones", "Áreas comunes", "Departamento piloto"],
    summary: "Terminaciones de 64 departamentos, hall de acceso en mármol y piloto de venta llave en mano.",
    challenge: "Entregar 64 departamentos con terminaciones de alto estándar dentro del plazo de venta.",
    solution: "Coordinamos cuadrillas por piso, estandarizamos detalles y diseñamos el hall de acceso en mármol.",
    result: "Entrega a tiempo para la recepción municipal y un piloto que apoyó la venta en verde.",
    materials: ["Mármol", "Porcelanato gran formato", "Carpintería en serie"],
    duration: "9 meses",
    images: ["1460317442991-0ec209397118", "1560448204-e02f11c3d0e2", "1493809842364-78817add7ffb"],
  },
  {
    slug: "condominio-vina-del-mar", category: "inmobiliarias",
    title: "Condominio Viña del Mar", location: "Viña del Mar", year: 2024, area: "32 unidades",
    services: ["Áreas comunes", "Paisajismo interior", "Gestión de obra"],
    summary: "Diseño y ejecución de áreas comunes: lobby, gimnasio y quincho con vista al mar.",
    challenge: "Áreas comunes expuestas al clima costero, la humedad y la sal.",
    solution: "Seleccionamos materiales resistentes al ambiente marino y diseñamos lobby, gimnasio y quincho.",
    result: "Espacios comunes que se mantienen como nuevos y suman valor al proyecto.",
    materials: ["Granito flameado", "Madera tratada", "Acero inoxidable"],
    duration: "5 meses",
    images: ["1574362848149-11496d93a7c7", "1600573472550-8090b5e0745e", "1512917774080-9991f1c4c750"],
  },
  {
    slug: "piloto-nunoa", category: "inmobiliarias",
    title: "Piloto Ñuñoa", location: "Ñuñoa", year: 2023, area: "2 pilotos",
    services: ["Interiorismo", "Mobiliario", "Styling para venta"],
    summary: "Dos departamentos piloto diseñados para vender: cada metro cuadrado pensado para la visita.",
    challenge: "Lograr que dos departamentos piloto vendieran el proyecto en pocas visitas.",
    solution: "Interiorismo completo, mobiliario a escala y styling pensado para la fotografía y la visita.",
    result: "Pilotos que la inmobiliaria usó en toda su campaña digital.",
    materials: ["Mobiliario a medida", "Textiles", "Iluminación decorativa"],
    duration: "6 semanas",
    images: ["1493809842364-78817add7ffb", "1564078516393-cf04bd966897", "1600121848594-d8644e57abab"],
  },

  // ── Hogares ────────────────────────────────────────────────────────────
  {
    slug: "casa-los-dominicos", category: "hogares", featured: true,
    title: "Casa Los Dominicos", location: "Las Condes", year: 2025, area: "320 m²",
    services: ["Remodelación integral", "Arquitectura interior", "Mármol y piedra"],
    summary: "Remodelación integral de una casa de los años 80: nueva planta, luz natural y baños en mármol.",
    challenge: "Una casa de los años 80 con espacios compartimentados, poca luz y baños antiguos.",
    solution: "Redistribuimos la planta, ampliamos ventanales y renovamos los baños completos en mármol.",
    result: "Una casa luminosa e integrada, con terminaciones que no requieren mantención constante.",
    materials: ["Mármol Bianco", "Roble europeo", "Ventanas termopanel"],
    duration: "5 meses",
    images: ["1604014237800-1c9102c219da", "1600607687939-ce8a6c25118c", "1620626011761-996317b8d101"],
  },
  {
    slug: "departamento-providencia", category: "hogares",
    title: "Departamento Providencia", location: "Providencia", year: 2024, area: "140 m²",
    services: ["Remodelación integral", "Carpintería", "Iluminación"],
    summary: "Departamento clásico reconvertido: muros abiertos, pisos de madera recuperados y cocina integrada.",
    challenge: "Un departamento clásico con muros que dividían todo y pisos deteriorados.",
    solution: "Abrimos espacios, recuperamos los pisos de madera originales e integramos la cocina al living.",
    result: "Un departamento que mantiene su carácter y se siente el doble de amplio.",
    materials: ["Parquet recuperado", "Cuarzo", "Pintura mineral"],
    duration: "10 semanas",
    images: ["1600210492486-724fe5c67fb0", "1502672260266-1c1ef2d93688", "1616486338812-3dadae4b4ace"],
  },
  {
    slug: "bano-principal-vitacura", category: "hogares",
    title: "Baño Principal Vitacura", location: "Vitacura", year: 2023, area: "18 m²",
    services: ["Diseño de baño", "Mármol a medida", "Obra"],
    summary: "Baño principal revestido en mármol de piso a cielo, con vanitorio tallado y ducha a ras.",
    challenge: "Un baño principal anticuado, con filtraciones y una ducha incómoda.",
    solution: "Impermeabilizamos completo, revestimos en mármol de piso a cielo e instalamos ducha a ras y vanitorio tallado.",
    result: "Un baño de nivel hotel, sin filtraciones y fácil de limpiar.",
    materials: ["Mármol Calacatta", "Grifería negra mate", "Vidrio templado"],
    duration: "4 semanas",
    images: ["1604709177225-055f99402ea3", "1620626011761-996317b8d101", "1552321554-5fefe8c9ef14"],
  },
];
