// ══════════════════════════════════════════════════════════════════════════
// Category system
// ══════════════════════════════════════════════════════════════════════════
const CATS = [
  { key:"image",  label:"Bilder",          color:"var(--c-img)",   fmts:["jpeg","png","gif","webp","bmp","tiff","ico","tga","ppm","pcx","heic","heif","avif","psd","psb","eps","svg","pbm","pgm"] },
  { key:"raw",    label:"RAW-Kamera",      color:"var(--c-raw)",   fmts:["cr3","cr2","nef","nrw","arw","srf","sr2","raf","orf","rw2","dng","pef","3fr","fff","mrw","erf","mos","mef"] },
  { key:"audio",  label:"Audio",           color:"var(--c-audio)", fmts:["mp3","wav","ogg","flac","aac","opus","wma","aiff","ac3","mp2","midi","mid"] },
  { key:"video",  label:"Video",           color:"var(--c-video)", fmts:["mp4","avi","mov","mkv","webm","flv","wmv","mpg","ts","3gp","mxf","rm"] },
  { key:"data",   label:"Tabellen / Daten",color:"var(--c-data)",  fmts:["csv","tsv","json","xlsx","xls","xml","parquet","feather","orc","sqlite","db","html","txt","yaml","toml","h5","hdf5","nc","ods"] },
  { key:"doc",    label:"Dokumente",       color:"var(--c-doc)",   fmts:["pdf","docx","doc","odt","rtf","pptx","ppt","odp","epub","fb2","ipynb","markdown","latex","rst","vsdx","msg","eml"] },
  { key:"3d",     label:"3D / BIM / CAD",  color:"var(--c-3d)",    fmts:["dxf","stl","obj","ply","glb","off","dae","step","brep","iges","svg","ifc","ifczip","3dm","x3d","vrml","amf"] },
  { key:"embd",   label:"Stickerei",       color:"var(--c-embd)",  fmts:["pes","dst","exp","jef","xxx","vp3","hus","sew","vip","csd","esd","u01","phb","phc","inb"] },
  { key:"gis",    label:"GIS / Geo",       color:"var(--c-gis)",   fmts:["geojson","kml","kmz","gpx","shp"] },
  { key:"font",   label:"Schriften",       color:"var(--c-font)",  fmts:["ttf","otf","woff","woff2"] },
  { key:"med",    label:"Medizin / LiDAR", color:"var(--c-med)",   fmts:["dcm","las","laz"] },
  { key:"pcb",    label:"PCB / G-Code",    color:"var(--c-pcb)",   fmts:["gbr","gtl","gbl","gts","gbs","gko","ger","gcode","nc","cnc","tap","ngc","mpf"] },
  { key:"arch",   label:"Archive",         color:"var(--c-arch)",  fmts:["zip","7z","rar","tar","tar_gz","tar_bz2"] },
  { key:"pim",    label:"Kontakte / Kalender", color:"var(--c-pim)", fmts:["vcf","ics"] },
  { key:"sub",    label:"Untertitel",      color:"var(--c-sub)",   fmts:["srt","vtt","ass","ssa","sub"] },
  { key:"mol",    label:"Chemie / Moleküle",color:"var(--c-mol)",  fmts:["mol","sdf","pdb"] },
];

// Kategorie-Beschreibungen für die Formate-Übersicht (/formate).
const CAT_DESC = {
  image: "JPG, JPEG, PNG, WEBP, HEIC, AVIF, TIFF, BMP, GIF, SVG, ICO, PBM, PGM, PPM, TGA, PCX sowie PSD/PSB (Photoshop) — Bildformate frei ineinander umwandeln.",
  raw:   "CR2, CR3, NEF, NRW, ARW, SRF, SR2, RAF, ORF, RW2, DNG, PEF, 3FR, FFF, MRW, ERF, MOS, MEF — Kamera-Rohdaten aller großen Hersteller in normale Bildformate umwandeln.",
  audio: "MP3, WAV, FLAC, AAC, OGG, M4A, OPUS, WMA, AIFF, AC3, MP2. MIDI zu JSON.",
  video: "MP4, AVI, MOV, MKV, WEBM, FLV, WMV, MPG, TS, 3GP. Video zu Audio: MP4 zu MP3, MP4 zu WAV.",
  data:  "CSV, JSON, XML, YAML, TOML, XLSX, ODS, TSV, Parquet, Feather, ORC, SQLite. Datenformate frei ineinander umwandeln.",
  doc:   "PDF, DOCX, DOC, ODT, RTF, PPTX, PPT, ODP, EPUB, FB2, IPYNB (Jupyter), Markdown, LaTeX. Dokumente zwischen allen gängigen Formaten konvertieren.",
  "3d":  "STL, OBJ, GLB, PLY, OFF, DAE (Collada), AMF, VRML, X3D, DXF, STEP, IGES, BREP, IFC, 3DM (Rhino). STL zu OBJ, OBJ zu STL, DXF zu PDF, DXF zu PNG.",
  embd:  "PES (Brother), DST (Tajima), JEF (Janome), VP3 (Husqvarna Viking), HUS, SEW, EXP (Melco), XXX (Singer), VIP (Pfaff), CSD, ESD, U01, PHB, PHC, INB — Stickdateien zwischen über 80 Formaten konvertieren.",
  gis:   "GeoJSON, Shapefile (SHP), KML, KMZ, GPX. CSV zu GeoJSON, GeoJSON zu Shapefile.",
  font:  "TTF, OTF, WOFF, WOFF2 — Schriftdateien zwischen allen Web- und Desktop-Schriftformaten konvertieren.",
  med:   "DICOM (DCM) zu PNG, TIFF, JPEG. LAS, LAZ Punktwolken (LiDAR).",
  pcb:   "Gerber-Dateien (GBR, GTL, GBL, GTS, GBS, GKO) für Leiterplatten-Fertigung sowie G-Code (NC, CNC, TAP, NGC, MPF) für CNC-Fräsen und 3D-Drucker.",
  arch:  "ZIP, 7Z, TAR, TAR.GZ, TAR.BZ2, RAR — zwischen Archivformaten konvertieren.",
  pim:   "VCF (vCard) und ICS (iCalendar) — Kontakte und Kalendereinträge für den Import in andere Adressbuch- oder Kalender-Apps umwandeln.",
  sub:   "SRT, VTT, ASS, SSA, SUB — Untertiteldateien zwischen allen gängigen Formaten für Videoplayer und Streaming-Plattformen konvertieren.",
  mol:   "MOL, SDF, PDB — Molekülstrukturdateien aus Cheminformatik und Strukturbiologie zwischen Formaten umwandeln.",
};

function getCat(fmt) {
  for (const c of CATS) {
    if (c.fmts.includes(fmt)) return c;
  }
  return { key:"other", label:"Sonstige", color:"var(--c-other)", fmts:[] };
}

// ══════════════════════════════════════════════════════════════════════════
// Format normalization
// ══════════════════════════════════════════════════════════════════════════
const ALIAS = {
  jpg:"jpeg", jpe:"jpeg", jfif:"jpeg",
  tif:"tiff", md:"markdown", htm:"html",
  stp:"step", p21:"step", igs:"iges", gltf:"glb",
  m4a:"aac", m4b:"aac", mid:"midi",
  yml:"yaml", tgz:"tar_gz", tbz2:"tar_bz2", txz:"tar_xz",
  vcard:"vcf", ical:"ics", h5:"hdf5",
};
function normFmt(s) { const f=s.toLowerCase().replace(/^\./,''); return ALIAS[f]||f; }
function fileExt(n) { const p=n.split('.'); return p.length>1?p.pop():''; }
function fmtBytes(n) {
  if(n<1024) return n+' B';
  if(n<1048576) return (n/1024).toFixed(1)+' KB';
  if(n<1073741824) return (n/1048576).toFixed(1)+' MB';
  return (n/1073741824).toFixed(1)+' GB';
}

function catIcon(key) {
  const ids = { image:'i-cat-image', raw:'i-cat-raw', audio:'i-cat-audio', video:'i-cat-video',
                data:'i-cat-data', doc:'i-cat-doc', '3d':'i-cat-3d', embd:'i-cat-embd',
                gis:'i-cat-gis', font:'i-cat-font', med:'i-cat-med', pcb:'i-cat-pcb',
                arch:'i-cat-arch', pim:'i-cat-pim', sub:'i-cat-sub', mol:'i-cat-mol' };
  return `<svg class="icon"><use href="#${ids[key] || 'i-folder'}"/></svg>`;
}

function hexAlpha(cssVar, alpha) {
  // For CSS custom properties we can't compute hex easily; return a fallback rgba
  // We'll map known colors
  const map = {
    'var(--c-img)':'236,72,153','var(--c-raw)':'245,158,11','var(--c-audio)':'16,185,129',
    'var(--c-video)':'249,115,22','var(--c-data)':'59,130,246','var(--c-doc)':'99,102,241',
    'var(--c-3d)':'6,182,212','var(--c-embd)':'239,68,68','var(--c-gis)':'34,197,94',
    'var(--c-font)':'168,85,247','var(--c-med)':'20,184,166','var(--c-pcb)':'132,204,22',
    'var(--c-arch)':'139,92,246','var(--c-pim)':'245,158,11',
    'var(--c-sub)':'6,182,212','var(--c-mol)':'16,185,129','var(--c-other)':'107,114,128',
  };
  const rgb = map[cssVar] || '107,114,128';
  return `rgba(${rgb},${alpha})`;
}
