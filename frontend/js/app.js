(() => {
  'use strict';
  const $ = (id) => document.getElementById(id);
  const master = window.PHISHGUARD_CONFIG;
  if (!master || !master.themes) { console.error('Missing /js/config.js'); return; }
  const storageKey = 'phishguard-ten-directions-v1';
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(storageKey) || '{}') || {}; } catch (_) {}
  const reduced = master.reducedMotionRespect !== false && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const state = { theme: master.themes[saved.theme] ? saved.theme : master.defaultTheme, grid: typeof saved.grid === 'boolean' ? saved.grid : master.grid, analyzing: false };
  let activeTheme, lenis = null, animationTimer = null, rafId = 0, lastDraw = 0, ctx, dpr = 1, w = 0, h = 0, phase = 0;
  let pointer = {x:-1000, y:-1000, moving:false}, trails = [], ripples = [];
  const canvas = $('ambientCanvas'); ctx = canvas.getContext('2d', {alpha: true});
  const css = (k,v) => document.documentElement.style.setProperty(k, String(v));
  const safe = (s, fallback) => typeof s === 'string' && s.length < 256 ? s : fallback;
  const store = () => { try {localStorage.setItem(storageKey, JSON.stringify({theme:state.theme,grid:state.grid}));}catch(_){} };
  function applyTheme({animate = true} = {}) {
    const t = master.themes[state.theme] || master.themes[master.defaultTheme]; activeTheme = t;
    const root = document.body;
    root.dataset.theme = state.theme;
    root.dataset.layout = t.layout;
    for (const [k,v] of Object.entries(t.colors)) css('--'+k.replace(/[A-Z]/g, x=>'-'+x.toLowerCase()), v);
    css('--button',t.colors.button); css('--button-ink',t.colors.buttonInk);
    css('--display',t.fonts.display); css('--body',t.fonts.body); css('--mono',t.fonts.mono);
    css('--title-size',t.typography.title); css('--title-weight',t.typography.weight); css('--title-tracking',t.typography.tracking); css('--title-leading',t.typography.leading);
    css('--radius',t.geometry.radius); css('--input-radius',t.geometry.inputRadius);css('--edge',t.geometry.edge);css('--content-width',t.geometry.width);css('--grain-opacity',t.geometry.grain);css('--hero-align',t.geometry.heroAlign);
    css('--animate-speed',Math.max(.1,t.animation.speed));
    $('heroTitle').innerHTML = master.headlineOverride || t.heading; // Locally authored HTML only; no user or API content.
    $('eyebrow').textContent = t.eyebrow; $('heroSubtitle').textContent = t.subtitle;
    $('headerMiddle').textContent = t.tagline.toUpperCase();
    $('heroGrid').hidden = !state.grid; $('gridToggle').checked = !!state.grid;
    $('modeLabel').textContent = 'URL-ONLY / ML CLASSIFICATION';
    document.querySelectorAll('.theme-item').forEach(b => b.setAttribute('aria-pressed',String(b.dataset.theme === state.theme)));
    document.querySelector('meta[name="theme-color"]').setAttribute('content',t.colors.bg);
    trails=[];ripples=[];phase=0;
    if (animate && !reduced && window.gsap) {
      window.gsap.fromTo('.hero-content', {opacity:0,y:t.animation.entry==='snap'?0:25}, {opacity:1,y:0,duration:Math.max(.3,t.animation.speed),ease:t.animation.entry==='snap'?'steps(4)':'power3.out',clearProps:'transform'});
    }
    draw(0);
  }
  function buildThemeChooser() {
    const root = $('themeList'); root.replaceChildren();
    Object.entries(master.themes).forEach(([key,t],i)=>{
      const b=document.createElement('button');b.type='button';b.className='theme-item';b.dataset.theme=key;b.setAttribute('aria-pressed','false');b.setAttribute('aria-label',`Activate theme ${t.name}: ${t.tagline}`);
      b.style.setProperty('--swatch-bg',t.colors.bg);b.style.setProperty('--swatch-ink',t.colors.ink);b.style.setProperty('--swatch-font',t.fonts.display);
      const sw=document.createElement('div');sw.className='theme-swatch';sw.textContent='Aa';const ln=document.createElement('span');ln.className='swatch-line';sw.append(ln);
      const info=document.createElement('div');info.className='theme-item-copy';const num=document.createElement('span');num.className='theme-number';num.textContent=String(i+1).padStart(2,'0')+' / 10';const name=document.createElement('strong');name.textContent=t.name.replace(/^\d+\s*\/\s*/,'')+' — '+t.tagline;const ref=document.createElement('span');ref.className='theme-reference';ref.textContent=t.reference;info.append(num,name,ref);b.append(sw,info);
      b.addEventListener('click',()=>{state.theme=key;applyTheme();store();});root.append(b);
    });
  }
 function openSettings() {
    const panel = $('settingsPanel');
    const backdrop = $('settingsBackdrop');

    backdrop.hidden = false;
    panel.hidden = false;

    // Stop background page scrolling.
    document.body.style.overflow = 'hidden';

    // Pause Lenis while the Customize panel is open.
    if (lenis) {
        lenis.stop();
    }

    // Start the theme list at the top.
    panel.scrollTop = 0;

    $('settingsClose').focus({ preventScroll: true });
}

function closeSettings() {
    const panel = $('settingsPanel');
    const backdrop = $('settingsBackdrop');

    panel.hidden = true;
    backdrop.hidden = true;

    document.body.style.overflow = '';

    // Restore normal page scrolling.
    if (lenis) {
        lenis.start();
    }

    $('settingsOpen').focus({ preventScroll: true });
}
  $('settingsOpen').addEventListener('click',openSettings);$('settingsClose').addEventListener('click',closeSettings);$('settingsBackdrop').addEventListener('click',closeSettings);
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('settingsPanel').hidden)closeSettings();});
  $('gridToggle').addEventListener('change',e=>{state.grid=!!e.target.checked;applyTheme({animate:false});store();});
  // Fluid responsive canvas. Abstract visualizations, not representations of the ML algorithm.
  function resize(){const box=canvas.getBoundingClientRect();w=Math.max(1,box.width);h=Math.max(1,box.height);dpr=Math.min(window.devicePixelRatio||1,Number(master.maxPixelRatio)||1.7);canvas.width=Math.floor(w*dpr);canvas.height=Math.floor(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);}
  function hexRgb(hex){const x=hex.replace('#','');return [parseInt(x.slice(0,2),16),parseInt(x.slice(2,4),16),parseInt(x.slice(4,6),16)];}
  const rgba=(hex,a)=>{const [r,g,b]=hexRgb(hex);return `rgba(${r},${g},${b},${a})`;};
  function line(x1,y1,x2,y2,color,width=1){ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.lineWidth=width;ctx.strokeStyle=color;ctx.stroke();}
  function circle(x,y,r,stroke,width=1){ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.lineWidth=width;ctx.strokeStyle=stroke;ctx.stroke();}
  let points = Array.from({length:90},(_,i)=>({x:(i*0.61803398875)%1,y:(i*.754877666)%1,phase:i*1.27}));
  function draw(time){
    if(!ctx||!activeTheme)return;
    const t=activeTheme,ink=t.colors.accent,back=t.colors.ink;ctx.clearRect(0,0,w,h);
    if (!state.grid) return;
    const density=Math.max(.3,Math.min(2,Number(master.particleDensity)||1));
    const s = Math.min(w,h), speed = reduced?0:Math.max(.1,Number(master.motion)||.7) * t.animation.speed;
    const tick=time*.001*speed, effect=t.effect;
    if(effect==='paper'){
      for(let i=0;i<75*density;i++){const px=(i*171.77)%w,py=(i*347.93)%h;ctx.fillStyle=rgba(back,i%4===0?.11:.055);ctx.fillRect(px,py,i%5===0?2:1,1);}
      line(w*.84,0,w*.84,h,rgba(ink,.09));line(w*.11,0,w*.11,h,rgba(ink,.09));
    } else if(effect==='boxes'){
      const cell=Math.max(28,58/density),cols=Math.ceil(w/cell),rows=Math.ceil(h/cell);
      for(let y=0;y<rows;y++)for(let x=0;x<cols;x++){
        const px=x*cell+cell*.12,py=y*cell+cell*.12;
        const dist=Math.hypot(pointer.x-px,pointer.y-py),factor=Math.max(0,1-dist/250);
        ctx.strokeStyle=rgba(ink,.055+factor*.36);ctx.lineWidth=.8+factor*.8;const n=cell*(.7+factor*.18);ctx.strokeRect(px,py,n,n);
        if(factor>.12){ctx.fillStyle=rgba(ink,.06+factor*.1);ctx.fillRect(px,py,n,n);}
      }
    } else if(effect==='ascii'){
      const chars=['.','+','/','[',':','_','0','1','#','%','*'];ctx.font='12px monospace';
      for(let y=14;y<h;y+=22)for(let x=5;x<w;x+=16){const val=Math.sin(x*.014+y*.025+tick*1.2)+Math.cos(x*.009-y*.019-tick*.7);const idx=Math.floor(((val+2)/4)*chars.length);ctx.fillStyle=rgba(ink,.07+Math.abs(val)*.07);ctx.fillText(chars[Math.min(chars.length-1,Math.max(0,idx))],x,y);}
    } else if(effect==='water'){
      const cx=w*.5,cy=h*.52;for(let j=0;j<12;j++){const r=75+j*43+Math.sin(tick*1.5+j*.6)*9;ctx.beginPath();for(let a=0;a<=Math.PI*2+.04;a+=.07){const radius=r+Math.sin(a*4+tick*2.2+j*.6)*9+Math.cos(a*7-tick+j)*4;const xx=cx+Math.cos(a)*radius,yy=cy+Math.sin(a)*radius*.78;if(a===0)ctx.moveTo(xx,yy);else ctx.lineTo(xx,yy);}ctx.strokeStyle=rgba(ink,.07+(.08*j/12));ctx.stroke();}
      ripples=ripples.filter(x=>time-x.at<2300);ripples.forEach(p=>{const q=(time-p.at)/2300;circle(p.x,p.y,5+q*180,rgba(ink,(1-q)*.33),1.5);circle(p.x,p.y,10+q*105,rgba(ink,(1-q)*.18),.7);});
    } else if(effect==='trail'){
      trails=trails.filter(p=>time-p.at<1200);ctx.font=`800 ${Math.max(25,Math.min(72,w*.05))}px Arial`;ctx.textAlign='center';trails.forEach(p=>{const q=(time-p.at)/1200;ctx.fillStyle=rgba(ink,(1-q)*.18);ctx.fillText('?',p.x,p.y)});ctx.textAlign='left';
      for(let j=0;j<9;j++)line(0,(j+1)*h/10,w,(j+1)*h/10,rgba(ink,.06));
    } else if(effect==='film'){
      const fw=80;for(let x=-fw;x<w+fw;x+=fw){const o=(tick*12)%fw;ctx.strokeStyle=rgba(ink,.2);ctx.strokeRect(x+o,22,fw-10,64);ctx.strokeRect(x+o,h-86,fw-10,64);for(let k=0;k<3;k++){ctx.fillStyle=rgba(ink,.09);ctx.fillRect(x+o+10+k*21,9,12,7);ctx.fillRect(x+o+10+k*21,h-17,12,7);}}line(0,h*.5,w,h*.5,rgba(ink,.07));
    } else if(effect==='orbit'){
      const cx=w*.52,cy=h*.47;for(let i=0;i<11;i++){const r=90+i*50;ctx.beginPath();ctx.ellipse(cx,cy,r,r*.66,tick*.03+i*.15,.18+tick*.09+i*.35,Math.PI*1.55+tick*.09+i*.35);ctx.strokeStyle=rgba(ink,.07+i*.008);ctx.lineWidth=1.1;ctx.stroke();const angle=tick*.33+(i*1.13);const px=cx+Math.cos(angle)*r,py=cy+Math.sin(angle)*r*.66;ctx.fillStyle=rgba(ink,.38);ctx.beginPath();ctx.arc(px,py,1.5+i*.06,0,Math.PI*2);ctx.fill();}
    } else if(effect==='scanlines'){
      for(let y=0;y<h;y+=7){line(0,y,w,y,rgba(ink,y%21===0?.085:.025));}for(let x=0;x<w;x+=w/7)line(x,0,x,h,rgba(ink,.035));
    } else if(effect==='nodes'){
      const p=points.slice(0,Math.round(80*density));for(let i=0;i<p.length;i++){const a=p[i],ax=a.x*w+Math.sin(tick+a.phase)*18,ay=a.y*h+Math.cos(tick+a.phase)*15;ctx.fillStyle=rgba(ink,.18);ctx.beginPath();ctx.arc(ax,ay,1.7,0,Math.PI*2);ctx.fill();if(i%3!==0)continue;for(let j=i+1;j<p.length;j++){const b=p[j],bx=b.x*w+Math.sin(tick+b.phase)*18,by=b.y*h+Math.cos(tick+b.phase)*15,dist=Math.hypot(ax-bx,ay-by);if(dist<180)line(ax,ay,bx,by,rgba(ink,.12*(1-dist/180)));}}if(pointer.x>0)circle(pointer.x,pointer.y,86,rgba(ink,.11));
    }
  }
  function animateFrame(time){if(time-lastDraw>33){draw(time);lastDraw=time;}rafId=requestAnimationFrame(animateFrame);}
  document.addEventListener('pointermove',e=>{if(e.pointerType==='touch')return;pointer={x:e.clientX,y:e.clientY,moving:true};if(activeTheme?.effect==='trail'){if(!trails.length||Math.hypot(trails[trails.length-1].x-e.clientX,trails[trails.length-1].y-e.clientY)>35)trails.push({x:e.clientX,y:e.clientY,at:performance.now()});if(trails.length>22)trails.shift();}}, {passive:true});
  document.addEventListener('pointerdown',e=>{if(activeTheme?.effect==='water')ripples.push({x:e.clientX,y:e.clientY,at:performance.now()});},{passive:true});
  window.addEventListener('resize',resize,{passive:true});document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(rafId);rafId=0;}else if(!rafId&&!reduced)rafId=requestAnimationFrame(animateFrame);});
  function addItems(id,items,fallback){const root=$(id);root.replaceChildren();(Array.isArray(items)&&items.length?items:[fallback]).slice(0,60).forEach(x=>{const li=document.createElement('li');li.textContent=String(x);root.append(li);});}
  function renderResult(data){
    const score=Number(data.risk_score),valid=Number.isFinite(score);
    $('riskNumber').textContent=valid?String(Math.min(100,Math.max(0,Math.round(score)))):'—';
    $('riskPill').textContent=(data.risk_level||'UNRATED').toString().toUpperCase()+' / RISK';
    $('verdictText').textContent=data.prediction===1?'Potential phishing.':data.prediction===0?'Predicted legitimate.':'Classification unavailable.';
    $('reportUrl').textContent=String(data.url||'');$('reportModel').textContent='MODEL / '+String(data.model_name||'UNKNOWN');$('reportMode').textContent='MODE / '+String(data.analysis_mode||'URL-ONLY');
    $('resultTimestamp').textContent=new Date().toLocaleString();
    addItems('indicatorList',data.indicators,'No rule-based indicators flagged. This does not establish safety.');
    addItems('recommendationList',data.recommendations,'Verify the destination independently before sharing sensitive information.');
    const features=$('featureList');features.replaceChildren();Object.entries(data.features||{}).slice(0,150).forEach(([k,v])=>{const cell=document.createElement('div');cell.className='feature-cell';const key=document.createElement('span');key.textContent=k.replaceAll('_',' ').toUpperCase();const value=document.createElement('strong');value.textContent=String(v);cell.append(key,value);features.append(cell);});
    $('resultSection').hidden=false;if(!reduced&&window.gsap)window.gsap.fromTo('.score-panel,.verdict-panel',{opacity:0,y:30},{opacity:1,y:0,duration:.72,stagger:.12,ease:'power3.out'});
    $('resultSection').scrollIntoView({behavior:reduced?'instant':'smooth',block:'start'});
  }
  function toggleBusy(on){state.analyzing=on;$('checkButton').disabled=on;$('urlInput').disabled=on;$('checkLabel').textContent=on?'READING':'CHECK';}
  function startScan(){const overlay=$('scanOverlay');overlay.hidden=false;$('scanProgress').style.width='0%';requestAnimationFrame(()=>$('scanProgress').style.width='90%');const phrases=Array.isArray(master.scanPhrases)&&master.scanPhrases.length?master.scanPhrases:['ANALYZING ADDRESS'];let ix=0;$('scanPhrase').textContent=phrases[0];animationTimer=setInterval(()=>{$('scanPhrase').textContent=phrases[++ix%phrases.length];},620);}
  function stopScan(){clearInterval(animationTimer);$('scanProgress').style.width='100%';$('scanOverlay').hidden=true;}
  async function analyze(url){const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),Number(master.apiTimeoutMs)||20000);try{const response=await fetch(master.apiEndpoint||'/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({url}),signal:controller.signal});let data;try{data=await response.json()}catch(_){throw new Error('The API returned a response that is not JSON.')}if(!response.ok){const detail=typeof data.detail==='string'?data.detail:`API error ${response.status}`;throw new Error(detail)}if(!data||typeof data!=='object'||!('prediction'in data))throw new Error('The API response does not match the expected model contract.');return data;}catch(e){if(e.name==='AbortError')throw new Error('The analysis timed out. Check the FastAPI server.');if(e instanceof TypeError)throw new Error('Cannot reach FastAPI. Open the site through http://127.0.0.1:8000 and check /health.');throw e;}finally{clearTimeout(timeout)}}
  $('scanForm').addEventListener('submit',async e=>{e.preventDefault();if(state.analyzing)return;$('errorMessage').hidden=true;const url=$('urlInput').value.trim();let parsed;try{parsed=new URL(url);if(!['http:','https:'].includes(parsed.protocol)||!parsed.hostname)throw new Error('Enter a full http:// or https:// website address.');if(parsed.username||parsed.password)throw new Error('Please omit usernames and passwords from the URL.');if(url.length>4096)throw new Error('The URL is too long.');}catch(err){$('errorMessage').textContent=err.message||'Enter a complete website address including https://';$('errorMessage').hidden=false;return;}
    toggleBusy(true);$('resultSection').hidden=true;startScan();const started=performance.now();try{const result=await analyze(url);const minimum=reduced?0:Math.max(0,Number(master.scanMinDurationMs)||0);await new Promise(res=>setTimeout(res,Math.max(0,minimum-(performance.now()-started))));stopScan();renderResult(result);}catch(err){stopScan();$('errorMessage').textContent=err.message||'Scan failed.';$('errorMessage').hidden=false;}finally{toggleBusy(false);}
  });
  $('scanAgain').addEventListener('click',()=>{$('resultSection').hidden=true;$('urlInput').value='';$('scanner').scrollIntoView({behavior:reduced?'instant':'smooth'});$('urlInput').focus({preventScroll:true});});
function initLenis() {
    if (reduced || !master.useLenis || !window.Lenis) return;

    lenis = new window.Lenis({
        autoRaf: true,
        duration: 1.1,
        smoothWheel: true,

        prevent: (node) => {
            return Boolean(node.closest('#settingsPanel'));
        }
    });
}
buildThemeChooser();resize();applyTheme({animate:false});if(!reduced)rafId=requestAnimationFrame(animateFrame);window.addEventListener('load',initLenis,{once:true});})();
