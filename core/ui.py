"""Look & feel: dashboard CSS (dark glassmorphism theme), Thinking-Orbs intro, loader and mascot."""
import json
from contextlib import contextmanager

import streamlit as st
import streamlit.components.v1 as components

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, button, input, textarea { font-family:'Inter',sans-serif !important; }
.stApp { background:#090D16 !important; color:#F8FAFC !important; }
header[data-testid="stHeader"] { background:transparent !important; }
.block-container { padding-top:1.8rem; max-width:1280px; }
.element-container:has(iframe[height="0"]) { position:absolute; height:0; width:0; overflow:hidden; opacity:0; }

/* Sidebar Styling */
[data-testid="stSidebar"] { 
    background:#0D1322 !important; 
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius:0 24px 24px 0; 
}
[data-testid="stSidebar"] * { color:#94A3B8 !important; }
.cm-brand { display:flex; align-items:center; gap:10px; font-weight:800; font-size:1.2rem; color:#FFFFFF !important; }
.cm-logo { width:36px; height:36px; border-radius:12px; background:linear-gradient(135deg, #3B82F6, #6366F1); color:#fff !important; display:grid; place-items:center; box-shadow:0 4px 14px rgba(59,130,246,0.4); }
.cm-welcome { font-size:1.9rem; font-weight:800; line-height:1.15; margin:18px 0 4px; color:#FFFFFF !important; }
.cm-sub { color:#94A3B8 !important; font-size:.85rem; margin-bottom:14px; }

[data-testid="stSidebar"] div[role="radiogroup"] { gap:6px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding:10px 14px; border-radius:14px; width:100%; cursor:pointer; transition:all .25s ease; background:transparent; }
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display:none; }
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:rgba(255,255,255,0.05); transform:translateX(3px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background:rgba(59, 130, 246, 0.15) !important; border: 1px solid rgba(59, 130, 246, 0.3); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * { color:#60A5FA !important; font-weight:700 !important; }

/* Dashboard Glassmorphism Cards */
.cm-card { 
    background: linear-gradient(180deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius:20px; 
    padding:20px; 
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(12px);
    animation:fadeUp .65s cubic-bezier(.2,.8,.2,1) both; 
    animation-delay:var(--d,0s); 
    overflow:hidden; 
}
.cm-card.dark { 
    background: linear-gradient(180deg, #0F172A 0%, #090D16 100%) !important; 
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
}
.cm-card .t { font-size:.82rem; color:#94A3B8 !important; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; } 
.cm-card .v { font-size:2rem; font-weight:800; letter-spacing:-.5px; margin-top:6px; color:#FFFFFF !important; }
.cm-pill { font-size:.72rem; font-weight:700; padding:4px 10px; border-radius:999px; margin-left:8px; vertical-align:middle; }
.cm-pill.g { background:rgba(34, 197, 94, 0.15); color:#4ADE80 !important; border:1px solid rgba(34, 197, 94, 0.3); } 
.cm-pill.r { background:rgba(239, 68, 68, 0.15); color:#F87171 !important; border:1px solid rgba(239, 68, 68, 0.3); } 
.cm-pill.b { background:rgba(59, 130, 246, 0.15); color:#60A5FA !important; border:1px solid rgba(59, 130, 246, 0.3); }

.cm-spark { width:100%; height:36px; margin-top:8px; }
.cm-spark path { stroke-dasharray:400; stroke-dashoffset:400; animation:draw 1.6s .4s ease forwards; }

.cm-h1 { font-size:1.8rem; font-weight:800; margin:0; color:#FFFFFF !important; } 
.cm-crumb { color:#94A3B8 !important; font-size:.85rem; margin-bottom:20px; }

.cm-feat { 
    background: rgba(18, 24, 38, 0.7) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius:20px; 
    padding:22px; 
    min-height:140px; 
    transition:all .25s ease;
    backdrop-filter: blur(10px);
    animation:fadeUp .65s both; 
    animation-delay:var(--d,0s); 
}
.cm-feat:hover { transform:translateY(-4px); border-color:rgba(59,130,246,0.4) !important; box-shadow:0 12px 28px rgba(0,0,0,0.4); }
.cm-feat .i { font-size:1.8rem; } 
.cm-feat b { display:block; margin:10px 0 4px; color:#FFFFFF !important; font-size:1.05rem; } 
.cm-feat span { color:#94A3B8 !important; font-size:.88rem; line-height:1.4; }

.cm-chip { display:inline-block; font-size:.72rem; font-weight:700; padding:4px 12px; border-radius:999px; background:rgba(255,255,255,0.08); color:#CBD5E1 !important; margin-top:6px; }
.cm-chip.r { background:rgba(239, 68, 68, 0.15); color:#F87171 !important; } 
.cm-chip.o { background:rgba(245, 158, 11, 0.15); color:#FBBF24 !important; } 
.cm-chip.g { background:rgba(34, 197, 94, 0.15); color:#4ADE80 !important; }

/* Streamlit Native Element Overrides */
div[data-testid="stMetricValue"] { color: #FFFFFF !important; }
div[data-testid="stMetricLabel"] { color: #94A3B8 !important; }
[data-testid="stForm"], [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] { 
    border-radius:18px !important; 
    background:rgba(18, 24, 38, 0.8) !important; 
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
}

.stTabs [data-baseweb="tab-list"] { gap:8px; background:transparent; }
.stTabs button[data-baseweb="tab"] { background:rgba(255,255,255,0.06) !important; border-radius:999px; padding:6px 20px; color:#94A3B8 !important; border:1px solid rgba(255,255,255,0.08); }
.stTabs button[data-baseweb="tab"][aria-selected="true"] { background:#3B82F6 !important; color:#FFFFFF !important; border-color:#3B82F6; }
.stTabs button[data-baseweb="tab"][aria-selected="true"] p { color:#fff !important; }

.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button, .stLinkButton > a { 
    border-radius:999px; 
    font-weight:600; 
    background: linear-gradient(135deg, #3B82F6, #4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
    transition:all .2s ease; 
}
.stButton > button:hover, .stFormSubmitButton > button:hover { transform:translateY(-2px); box-shadow:0 8px 20px rgba(59, 130, 246, 0.4); }

.cm-loader { display:flex; align-items:center; gap:14px; padding:12px 20px; background:#0F172A; color:#fff; border-radius:999px; width:fit-content; font-weight:600; font-size:.9rem; border:1px solid rgba(255,255,255,0.1); }
.cm-ring { position:relative; width:34px; height:34px; animation:spin 2.4s linear infinite; }
.cm-ring span { position:absolute; left:50%; top:50%; width:4px; height:4px; margin:-2px; border-radius:50%; background:#60A5FA;
                transform:rotate(calc(var(--i)*36deg)) translateY(-14px); animation:pulse 1.2s ease-in-out infinite; animation-delay:calc(var(--i)*-.12s); }
@keyframes spin { to { transform:rotate(360deg) } }
@keyframes pulse { 50% { opacity:.25; transform:rotate(calc(var(--i)*36deg)) translateY(-14px) scale(.5) } }
@keyframes fadeUp { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
@keyframes draw { to { stroke-dashoffset:0 } }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title, crumb):
    st.markdown(f'<p class="cm-h1">{title}</p><p class="cm-crumb">{crumb}</p>', unsafe_allow_html=True)


_SPARK = ('<svg class="cm-spark" viewBox="0 0 200 34" preserveAspectRatio="none"><path d="M0 28 C20 10,35 30,60 18 S100 4,125 16 '
          'S170 30,200 6" fill="none" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/></svg>')


def stat_card(title, value, pill="", kind="g", dark=False, delay=0.0):
    pill_html = f'<span class="cm-pill {kind}">{pill}</span>' if pill else ""
    stroke_color = "#3B82F6" if dark else "#60A5FA"
    return (f'<div class="cm-card {"dark" if dark else ""}" style="--d:{delay}s"><div class="t">{title}</div>'
            f'<div class="v">{value}{pill_html}</div>{_SPARK.format(c=stroke_color)}</div>')


def feature_card(icon, title, text, delay=0.0):
    return f'<div class="cm-feat" style="--d:{delay}s"><div class="i">{icon}</div><b>{title}</b><span>{text}</span></div>'


@contextmanager
def loading(label="Thinking…"):
    slot = st.empty()
    dots = "".join(f'<span style="--i:{i}"></span>' for i in range(10))
    slot.markdown(f'<div class="cm-loader"><div class="cm-ring">{dots}</div>{label}</div>', unsafe_allow_html=True)
    try:
        yield
    finally:
        slot.empty()


def _run_in_parent(js):
    safe = json.dumps(js).replace("</", "<\\/")
    components.html(f"<script>const s=parent.document.createElement('script');s.textContent={safe};"
                    f"parent.document.body.appendChild(s);s.remove();</script>", height=0)


ORBS_JS = r"""
(function(){
  const d=document; if(d.getElementById('cm-intro')) return;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const o=d.createElement('div'); o.id='cm-intro';
  o.style.cssText='position:fixed;inset:0;background:#090D16;z-index:2147483000;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;transition:opacity .8s ease;font-family:Inter,sans-serif';
  o.innerHTML='<canvas width="440" height="440" style="width:220px;height:220px"></canvas>'+
    '<div style="color:#fff;font-size:22px;font-weight:700">Campus<span style="color:#3B82F6">Mate</span></div>'+
    '<div id="cm-msg" style="color:#94a3b8;font-size:13px;height:16px">Waking up your dashboard…</div>';
  d.body.appendChild(o);
  const x=o.querySelector('canvas').getContext('2d'), msg=o.querySelector('#cm-msg'), N=260, R=24, pts=[];
  for(let i=0;i<N;i++){ const y=1-2*(i+.5)/N, r=Math.sqrt(1-y*y), a=i*Math.PI*(3-Math.sqrt(5)); pts.push([Math.cos(a)*r,y,Math.sin(a)*r]); }
  const words=['Waking up your dashboard…','Syncing reminders…','Counting expenses…','Ready!'];
  const T=reduce?600:3300, t0=performance.now(), ease=t=>t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;
  function frame(now){
    const t=now-t0, ang=t/900, morph=ease(Math.min(1,Math.max(0,(t-1500)/900)));
    x.clearRect(0,0,440,440);
    for(let i=0;i<N;i++){
      const p=pts[i]; let cx=p[0]*Math.cos(ang)+p[2]*Math.sin(ang), cz=-p[0]*Math.sin(ang)+p[2]*Math.cos(ang), cy=p[1], alpha=1, size=1.4+(cz+1)*1.1;
      if(i<R){ const a=i/R*Math.PI*2-ang; cx+=(Math.cos(a)-cx)*morph; cy+=(Math.sin(a)-cy)*morph; cz-=cz*morph; size+=morph*1.2; } else alpha=1-morph;
      x.globalAlpha=Math.max(0,alpha*(.35+.65*(cz+1)/2)); x.fillStyle='#60A5FA'; x.beginPath(); x.arc(220+cx*150,220+cy*150,size,0,7); x.fill();
    }
    msg.textContent=words[Math.min(3,Math.floor(Math.max(t,0)/T*4))];
    if(t<T) requestAnimationFrame(frame); else { o.style.opacity=0; setTimeout(()=>o.remove(),850); }
  }
  requestAnimationFrame(frame);
})();
"""


def orbs_intro():
    if not st.session_state.get("intro_done"):
        st.session_state["intro_done"] = True
        _run_in_parent(ORBS_JS)


MASCOT_JS = r"""
(function(){
  const d=document;
  if(!window.__cmMascot){
    const box=d.createElement('div'); box.id='cm-mascot';
    box.style.cssText='position:fixed;right:18px;bottom:84px;width:100px;height:100px;z-index:9999;cursor:pointer;animation:cmfloat 3.2s ease-in-out infinite;filter:drop-shadow(0 8px 14px rgba(0,0,0,.5))';
    const face=d.createElement('div'); face.style.cssText='width:100%;height:100%;background-size:300% 300%;background-repeat:no-repeat;transition:transform .2s';
    const bub=d.createElement('div'); bub.style.cssText='position:absolute;right:88px;bottom:70px;background:#0F172A;color:#fff;padding:8px 12px;border-radius:14px;font:600 12px Inter,sans-serif;white-space:nowrap;opacity:0;transform:scale(.8);transition:all .25s;border:1px solid rgba(255,255,255,0.1);';
    box.append(face,bub); d.body.appendChild(box);
    const st=d.createElement('style'); st.textContent='@keyframes cmfloat{50%{transform:translateY(-7px)}}'; d.head.appendChild(st);
    const DIR='/app/static/cap-directions.webp', REA='/app/static/cap-reactions.webp';
    const MOODS={happy:0,love:1,sparkle:2,surprised:3,starry:4,blush:5,sleepy:6,dizzy:7,laugh:8};
    let busy=false, idle=null;
    const cell=i=>((i%3)*50)+'% '+(Math.floor(i/3)*50)+'%';
    function look(i){ face.style.backgroundImage='url('+DIR+')'; face.style.backgroundPosition=cell(i); }
    function sleepTimer(){ clearTimeout(idle); idle=setTimeout(()=>react('sleepy','zzz… tap me'),45000); }
    function react(name,say){
      busy=true; clearTimeout(idle);
      face.style.backgroundImage='url('+REA+')'; face.style.backgroundPosition=cell(MOODS[name]!==undefined?MOODS[name]:0); face.style.transform='scale(1.12)';
      if(say){ bub.textContent=say; bub.style.opacity=1; bub.style.transform='scale(1)'; }
      setTimeout(()=>{ busy=false; face.style.transform=''; bub.style.opacity=0; bub.style.transform='scale(.8)'; look(4); sleepTimer(); },2600);
    }
    d.addEventListener('mousemove',e=>{
      if(busy) return; const r=box.getBoundingClientRect(), dx=e.clientX-(r.left+r.width/2), dy=e.clientY-(r.top+r.height/2), T=70;
      look((dy<-T?0:dy>T?2:1)*3+(dx<-T?0:dx>T?2:1)); sleepTimer();
    });
    box.addEventListener('click',()=>react(['happy','laugh','sparkle','starry','blush'][Math.floor(Math.random()*5)],'Hi! 👋'));
    look(4); sleepTimer(); window.__cmMascot={react};
  }
  if(window.__pendingMood){ window.__cmMascot.react(window.__pendingMood[0],window.__pendingMood[1]); window.__pendingMood=null; }
})();
"""


def react(mood, text=""):
    st.session_state["mascot"] = (mood, text)


def mascot():
    mood = st.session_state.pop("mascot", None)
    pending = f"window.__pendingMood={json.dumps(list(mood))};" if mood else ""
    _run_in_parent(pending + MASCOT_JS)
