/**
 * PHISHGUARD CREATIVE CONTROL PANEL
 * -------------------------------
 * Change ANY theme below. Changes are reflected when the page is reloaded.
 * Browser Customize panel deliberately exposes only theme + grid.
 * Add a new theme by copying an object and giving it a unique key.
 * effect options: paper | boxes | ascii | water | orbit | trail | film | waves | nodes | scanlines
 * layouts: editorial | brutal | strict | centered | offset | condensed | framed | mono | monumental | luminous
 * heading markup is LOCAL TRUSTED CONTENT ONLY; never fill this with user URL or API response.
 */
window.PHISHGUARD_CONFIG = {
  defaultTheme: 'folio',
  grid: true,
  apiEndpoint: '/analyze',
  apiTimeoutMs: 20000,
  scanMinDurationMs: 1100,
  scanPhrases: ['READING THE SIGNAL', 'EVALUATING URL STRUCTURE', 'FORMING AN ASSESSMENT'],
  motion: 0.75,             // Global scale: 0–1
  particleDensity: 1,      // Global effect density: 0.3–2
  maxPixelRatio: 1.7,      // Canvas performance control
  headlineOverride: '',    // Optional HTML string, affects all themes when non-empty
  reducedMotionRespect: true,
  useLenis: true,
  themes: {
    folio: {
      name: '01 / FOLIO', tagline: 'Newspaper / ink', reference: 'Niccolò Miranda',
      layout: 'editorial', effect: 'paper',
      colors: { bg:'#e9e4d8', ink:'#272c27', muted:'#777569', line:'#a9a69a', panel:'#dad4c7', accent:'#405b52', button:'#262b28', buttonInk:'#efe9db' },
      fonts: { display:'"Bodoni Moda", Georgia, serif', body:'"DM Sans", sans-serif', mono:'"DM Mono", monospace' },
      heading: 'THE WEB <em>isn’t</em><br><span>always</span> honest.', subtitle:'Read between the links.', eyebrow:'THE DAILY DIGITAL / VOL. 001',
      typography: { title:'clamp(4.8rem, 10.6vw, 11.5rem)', weight:500, tracking:'-.082em', leading:.86 },
      geometry: { radius:'0px', inputRadius:'0px', edge:'1px', width:'1180px', heroAlign:'left', grain:.17 },
      animation: { entry:'rise', hover:'underline', speed:.95, amplitude:1.0 },
    },
    signal: {
      name: '02 / SIGNAL', tagline: 'Generative / grid', reference: '2xA Studio',
      layout: 'strict', effect: 'boxes',
      colors: { bg:'#d7e3d2', ink:'#0f211e', muted:'#496a60', line:'#85a093', panel:'#c2d4c6', accent:'#114b40', button:'#142b24', buttonInk:'#edffdc' },
      fonts: { display:'"Space Grotesk", sans-serif', body:'"Manrope", sans-serif', mono:'"IBM Plex Mono", monospace' },
      heading:'IDENTIFY<span> /</span><br>THE SIGNAL.', subtitle:'Computational reading for suspicious addresses.', eyebrow:'PG [PROGRAM_01] / ACTIVE',
      typography: { title:'clamp(5rem, 11vw, 12rem)', weight:700, tracking:'-.085em', leading:.84 },
      geometry: { radius:'2px', inputRadius:'2px', edge:'2px', width:'1240px', heroAlign:'left', grain:.03 },
      animation: { entry:'clip', hover:'shift', speed:.65, amplitude:1.3 },
    },
    mono: {
      name: '03 / MONO', tagline: 'Brutalist / monochrome', reference: 'bleibtgleich',
      layout: 'brutal', effect: 'trail',
      colors: { bg:'#edece6', ink:'#0b0b0b', muted:'#64645e', line:'#333333', panel:'#d8d7d0', accent:'#181818', button:'#000000', buttonInk:'#ffffff' },
      fonts: { display:'"Archivo Black", sans-serif', body:'"Archivo", sans-serif', mono:'"IBM Plex Mono", monospace' },
      heading:'IS THIS<br><span>LINK</span> REAL?', subtitle:'Challenge what the address claims.', eyebrow:'REALITY CHECK / 001',
      typography: { title:'clamp(4.2rem, 10.7vw, 11.2rem)', weight:800, tracking:'-.10em', leading:.85 },
      geometry: { radius:'0px', inputRadius:'0px', edge:'3px', width:'1310px', heroAlign:'left', grain:.02 },
      animation: { entry:'snap', hover:'invert', speed:.4, amplitude:1.4 },
    },
    liquid: {
      name: '04 / LIQUID', tagline: 'Fluid / ambient', reference: 'Thibaut-inspired interaction',
      layout: 'centered', effect: 'water',
      colors: { bg:'#c5dcdf', ink:'#143a46', muted:'#476d78', line:'#90b7bf', panel:'#e0eced', accent:'#386c84', button:'#183e48', buttonInk:'#e9f5ee' },
      fonts: { display:'"Instrument Serif", Georgia, serif', body:'"Manrope", sans-serif', mono:'"DM Mono", monospace' },
      heading:'Look <em>beneath</em><br><span>the surface.</span>', subtitle:'Appearances are easy to imitate.', eyebrow:'DEPTH / SURFACE / SIGNAL',
      typography: { title:'clamp(5rem, 10.3vw, 11.7rem)', weight:400, tracking:'-.068em', leading:.92 },
      geometry: { radius:'26px', inputRadius:'100px', edge:'1px', width:'1120px', heroAlign:'center', grain:.02 },
      animation: { entry:'float', hover:'glow', speed:1.4, amplitude:.7 },
    },
    terminal: {
      name: '05 / TERMINAL', tagline: 'ASCII / computing', reference: '2xA — MiAO World',
      layout: 'mono', effect: 'ascii',
      colors: { bg:'#101714', ink:'#c6efb6', muted:'#6ca679', line:'#34533d', panel:'#19251c', accent:'#9bdf8b', button:'#b8f4a0', buttonInk:'#102116' },
      fonts: { display:'"IBM Plex Mono", monospace', body:'"IBM Plex Mono", monospace', mono:'"IBM Plex Mono", monospace' },
      heading:'> TEST_THE<br><span>UNKNOWN_</span>', subtitle:'Input URL. Inspect structural evidence.', eyebrow:'PHISHGUARD_OS  1.0 / READY',
      typography: { title:'clamp(3.1rem, 8vw, 8rem)', weight:600, tracking:'-.085em', leading:1.02 },
      geometry: { radius:'0px', inputRadius:'0px', edge:'1px', width:'1190px', heroAlign:'left', grain:0 },
      animation: { entry:'type', hover:'invert', speed:.55, amplitude:.5 },
    },
    atelier: {
      name: '06 / ATELIER', tagline: 'Typography / atelier', reference: 'Danilo De Marco',
      layout: 'offset', effect: 'paper',
      colors: { bg:'#f0ebdf', ink:'#382d2b', muted:'#82716d', line:'#beb0a7', panel:'#e4dbcf', accent:'#654738', button:'#382d2b', buttonInk:'#fff8ee' },
      fonts: { display:'"Bodoni Moda", Georgia, serif', body:'"DM Sans", sans-serif', mono:'"DM Mono", monospace' },
      heading:'A <em>second</em><br><span>opinion.</span>', subtitle:'Good judgment begins with a closer look.', eyebrow:'STUDIO OF DIGITAL CAUTION',
      typography: { title:'clamp(5.2rem, 11vw, 12.3rem)', weight:500, tracking:'-.095em', leading:.95 },
      geometry: { radius:'0px', inputRadius:'0px', edge:'1px', width:'1160px', heroAlign:'left', grain:.1 },
      animation: { entry:'float', hover:'underline', speed:1.1, amplitude:.55 },
    },
    cinema: {
      name: '07 / CINEMA', tagline: 'Filmstrip / frame', reference: 'Strom Lab — filmstrip concept',
      layout: 'framed', effect: 'film',
      colors: { bg:'#1b1a19', ink:'#eee8dc', muted:'#9c968c', line:'#575249', panel:'#2c2b29', accent:'#c8b895', button:'#d9d1c2', buttonInk:'#1b1a19' },
      fonts: { display:'"Barlow Condensed", sans-serif', body:'"DM Sans", sans-serif', mono:'"IBM Plex Mono", monospace' },
      heading:'EVERY LINK<br><span>HAS A STORY.</span>', subtitle:'Inspect the frame before you follow it.', eyebrow:'FRAME 01 / DIGITAL EVIDENCE',
      typography: { title:'clamp(5.2rem, 13vw, 15rem)', weight:800, tracking:'-.055em', leading:.77 },
      geometry: { radius:'0px', inputRadius:'0px', edge:'1px', width:'1200px', heroAlign:'center', grain:.15 },
      animation: { entry:'clip', hover:'shift', speed:.8, amplitude:1.2 },
    },
    orbit: {
      name: '08 / ORBIT', tagline: 'Spiral / motion', reference: 'Generative motion exploration',
      layout: 'centered', effect: 'orbit',
      colors: { bg:'#e6e3f0', ink:'#27233f', muted:'#746e91', line:'#b6b0cb', panel:'#dcd7ea', accent:'#4d3a86', button:'#29223b', buttonInk:'#f5f0ff' },
      fonts: { display:'"Syne", sans-serif', body:'"Manrope", sans-serif', mono:'"DM Mono", monospace' },
      heading:'QUESTION<br><span>THE PATTERN.</span>', subtitle:'Look twice. Decide with evidence.', eyebrow:'INSIDE THE SIGNAL / 008',
      typography: { title:'clamp(4.4rem, 9.8vw, 11rem)', weight:800, tracking:'-.09em', leading:.88 },
      geometry: { radius:'20px', inputRadius:'16px', edge:'1px', width:'1220px', heroAlign:'center', grain:.03 },
      animation: { entry:'rotate', hover:'glow', speed:1.05, amplitude:1.2 },
    },
    archive: {
      name: '09 / ARCHIVE', tagline: 'Museum / archival', reference: 'Miranda editorial & print',
      layout: 'editorial', effect: 'scanlines',
      colors: { bg:'#e2d6bd', ink:'#463b2e', muted:'#8b7a64', line:'#b3a184', panel:'#d6c6a7', accent:'#6d5140', button:'#48392a', buttonInk:'#f7efdd' },
      fonts: { display:'"Instrument Serif", Georgia, serif', body:'"Archivo", sans-serif', mono:'"DM Mono", monospace' },
      heading:'THE ART OF<br><em>doubt.</em>', subtitle:'An index of the things addresses reveal.', eyebrow:'ARCHIVE NO. 09 — THE INTERNET',
      typography: { title:'clamp(5.5rem, 13vw, 14rem)', weight:400, tracking:'-.065em', leading:.82 },
      geometry: { radius:'0px', inputRadius:'0px', edge:'1px', width:'1140px', heroAlign:'left', grain:.2 },
      animation: { entry:'rise', hover:'underline', speed:1.2, amplitude:.8 },
    },
    nocturne: {
      name: '10 / NOCTURNE', tagline: 'Light / nodes', reference: 'Interactive contemporary studios',
      layout: 'luminous', effect: 'nodes',
      colors: { bg:'#070f19', ink:'#d9e8f3', muted:'#7893ab', line:'#243b52', panel:'#0b1c2b', accent:'#7bb8c8', button:'#c7ebee', buttonInk:'#101e2b' },
      fonts: { display:'"Space Grotesk", sans-serif', body:'"Manrope", sans-serif', mono:'"IBM Plex Mono", monospace' },
      heading:'NOT ALL<br><span>IS AS IT SEEMS.</span>', subtitle:'An extra layer of perspective.', eyebrow:'NETWORK / STRUCTURE / CONTEXT',
      typography: { title:'clamp(4.2rem, 10vw, 11.5rem)', weight:600, tracking:'-.087em', leading:.9 },
      geometry: { radius:'10px', inputRadius:'50px', edge:'1px', width:'1190px', heroAlign:'left', grain:0 },
      animation: { entry:'float', hover:'glow', speed:1.0, amplitude:.9 },
    },
  },
};
