"""Look & feel: dashboard CSS (video 1), Thinking-Orbs intro (video 2), loader and the mascot."""
import json
from contextlib import contextmanager

import streamlit as st
import streamlit.components.v1 as components

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, .stApp, button, input, textarea { font-family:'Inter',sans-serif !important; }
.stApp { background:#EEF0F4; }
header[data-testid="stHeader"] { background:transparent; }
.block-container { padding-top:2rem; max-width:1250px; }
.element-container:has(iframe[height="0"]) { position:absolute; height:0; width:0; overflow:hidden; opacity:0; }

[data-testid="stSidebar"] { background:#fff; border-radius:0 28px 28px 0; box-shadow:0 0 40px rgba(0,0,0,.05); }
.cm-brand { display:flex; align-items:center; gap:10px; font-weight:800; font-size:1.2rem; }
.cm-logo { width:34px; height:34px; border-radius:10px; background:#2F5BFF; color:#fff; display:grid; place-items:center; }
.cm-welcome { font-size:1.9rem; font-weight:800; line-height:1.15; margin:18px 0 4px; }
.cm-sub { color:#8A8D98; font-size:.8rem; margin-bottom:14px; }
[data-testid="stSidebar"] div[role="radiogroup"] { gap:6px; }
[data-testid="stSidebar"] div[role="radiogroup"] label { padding:10px 14px; border-radius:14px; width:100%; cursor:pointer; transition:all .25s ease; }
[data-testid="stSidebar"] div[role="radiogroup"] label > div:first-child { display:none; }
[data-testid="stSidebar"] div[role="radiogroup"] label:hover { background:#F1F2F6; transform:translateX(3px); }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) { background:#0B0B0F; }
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) * { color:#fff !important; }

.cm-card { background:#fff; border-radius:22px; padding:18px 20px; box-shadow:0 2px 14px rgba(20,20,40,.05);
           animation:fadeUp .65s cubic-bezier(.2,.8,.2,1) both; animation-delay:var(--d,0s); overflow:hidden; }
.cm-card.dark { background:#0B0B0F; color:#fff; }
.cm-card .t { font-size:.82rem; color:#8A8D98; font-weight:500; } .cm-card.dark .t { color:#B6B8C2; }
.cm-card .v { font-size:1.9rem; font-weight:800; letter-spacing:-.5px; margin-top:4px; }
.cm-pill { font-size:.7rem; font-weight:700; padding:3px 8px; border-radius:999px; margin-left:8px; vertical-align:middle; }
.cm-pill.g { background:#DDF7E6; color:#188A45; } .cm-pill.r { background:#FFE0E0; color:#C23030; } .cm-pill.b { background:#E1E9FF; color:#2F5BFF; }
.cm-spark { width:100%; height:34px; margin-top:6px; }
.cm-spark path { stroke-dasharray:400; stroke-dashoffset:400; animation:draw 1.6s .4s ease forwards; }
.cm-h1 { font-size:1.6rem; font-weight:800; margin:0; } .cm-crumb { color:#8A8D98; font-size:.8rem; margin-bottom:16px; }
.cm-feat { background:#fff; border-radius:22px; padding:20px; min-height:140px; transition:transform .25s, box-shadow .25s;
           animation:fadeUp .65s both; animation-delay:var(--d,0s); }
.cm-feat:hover { transform:translateY(-5px); box-shadow:0 14px 30px rgba(47,91,255,.12); }
.cm-feat .i { font-size:1.6rem; } .cm-feat b { display:block; margin:8px 0 4px; } .cm-feat span { color:#6B6E7B; font-size:.85rem; }
.cm-chip { display:inline-block; font-size:.72rem; font-weight:700; padding:3px 10px; border-radius:999px; background:#E3E5EA; margin-top:4px; }
.cm-chip.r { background:#FFE0E0; color:#C23030; } .cm-chip.o { background:#FFEBD6; color:#B25E00; } .cm-chip.g { background:#DDF7E6; color:#188A45; }

.cm-loader { display:flex; align-items:center; gap:14px; padding:12px 20px; background:#0B0B0F; color:#fff; border-radius:999px; width:fit-content; font-weight:600; font-size:.9rem; }
.cm-ring { position:relative; width:34px; height:34px; animation:spin 2.4s linear infinite; }
.cm-ring span { position:absolute; left:50%; top:50%; width:4px; height:4px; margin:-2px; border-radius:50%; background:#fff;
                transform:rotate(calc(var(--i)*36deg)) translateY(-14px); animation:pulse 1.2s ease-in-out infinite; animation-delay:calc(var(--i)*-.12s); }
@keyframes spin { to { transform:rotate(360deg) } }
@keyframes pulse { 50% { opacity:.25; transform:rotate(calc(var(--i)*36deg)) translateY(-14px) scale(.5) } }
@keyframes fadeUp { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
@keyframes draw { to { stroke-dashoffset:0 } }

.stTabs [data-baseweb="tab-list"] { gap:8px; background:transparent; }
.stTabs button[data-baseweb="tab"] { background:#E3E5EA; border-radius:999px; padding:6px 18px; height:auto; transition:all .25s; }
.stTabs button[data-baseweb="tab"][aria-selected="true"] { background:#2F5BFF; }
.stTabs button[data-baseweb="tab"][aria-selected="true"] p { color:#fff; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
.stButton > button, .stDownloadButton > button, .stFormSubmitButton > button, .stLinkButton > a { border-radius:999px; font-weight:600; transition:transform .15s, box-shadow .15s; }
.stButton > button:hover, .stFormSubmitButton > button:hover { transform:translateY(-2px); box-shadow:0 6px 16px rgba(47,91,255,.25); }
[data-testid="stForm"], [data-testid="stExpander"], [data-testid="stVerticalBlockBorderWrapper"] { border-radius:18px; background:#fff; }
@media (prefers-reduced-motion: reduce) { * { animation:none !important; transition:none !important; } }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def page_header(title, crumb):
    st.markdown(f'<p class="cm-h1">{title}</p><p class="cm-crumb">{crumb}</p>', unsafe_allow_html=True)


_SPARK = ('<svg class="cm-spark" viewBox="0 0 200 34" preserveAspectRatio="none"><path d="M0 28 C20 10,35 30,60 18 S100 4,125 16 '
          'S170 30,200 6" fill="none" stroke="{c}" stroke-width="2.2" stroke-linecap="round"/></svg>')


def stat_card(title, value, pill="", kind="g", dark=False, delay=0.0):
    pill_html = f'<span class="cm-pill {kind}">{pill}</span>' if pill else ""
    return (f'<div class="cm-card {"dark" if dark else ""}" style="--d:{delay}s"><div class="t">{title}</div>'
            f'<div class="v">{value}{pill_html}</div>{_SPARK.format(c="#fff" if dark else "#0B0B0F")}</div>')


def feature_card(icon, title, text, delay=0.0):
    return f'<div class="cm-feat" style="--d:{delay}s"><div class="i">{icon}</div><b>{title}</b><span>{text}</span></div>'


@contextmanager
def loading(label="Thinking…"):
    """A little spinning-dots loader that shows while the code inside the 'with' block runs."""
    slot = st.empty()
    dots = "".join(f'<span style="--i:{i}"></span>' for i in range(10))
    slot.markdown(f'<div class="cm-loader"><div class="cm-ring">{dots}</div>{label}</div>', unsafe_allow_html=True)
    try:
        yield
    finally:
        slot.empty()


# ------------------------------------------------ JavaScript that must run in the MAIN page
def _run_in_parent(js):
    """Streamlit runs components in an iframe. To draw over the whole page we copy our JavaScript
    into the parent page (allowed because both share the same origin)."""
    safe = json.dumps(js).replace("</", "<\\/")
    components.html(f"<script>const s=parent.document.createElement('script');s.textContent={safe};"
                    f"parent.document.body.appendChild(s);s.remove();</script>", height=0)


ORBS_JS = r"""
(function(){
  const d=document; if(d.getElementById('cm-intro')) return;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const o=d.createElement('div'); o.id='cm-intro';
  o.style.cssText='position:fixed;inset:0;background:#000;z-index:2147483000;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:22px;transition:opacity .8s ease;font-family:Inter,sans-serif';
  o.innerHTML='<canvas width="440" height="440" style="width:220px;height:220px"></canvas>'+
    '<div style="color:#fff;font-size:22px;font-weight:700">Campus<span style="color:#6C8CFF">Mate</span></div>'+
    '<div id="cm-msg" style="color:#8a8d98;font-size:13px;height:16px">Waking up your dashboard…</div>';
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
      x.globalAlpha=Math.max(0,alpha*(.35+.65*(cz+1)/2)); x.fillStyle='#fff'; x.beginPath(); x.arc(220+cx*150,220+cy*150,size,0,7); x.fill();
    }
    msg.textContent=words[Math.min(3,Math.floor(Math.max(t,0)/T*4))];
    if(t<T) requestAnimationFrame(frame); else { o.style.opacity=0; setTimeout(()=>o.remove(),850); }
  }
  requestAnimationFrame(frame);
})();
"""


def orbs_intro():
    """Plays once per visit (sphere of dots -> ring -> fade into the app)."""
    if not st.session_state.get("intro_done"):
        st.session_state["intro_done"] = True
        _run_in_parent(ORBS_JS)


MASCOT_JS = r"""
(function(){
  const d=document;
  if(!window.__cmMascot){
    const box=d.createElement('div'); box.id='cm-mascot';
    box.style.cssText='position:fixed;right:18px;bottom:84px;width:100px;height:100px;z-index:9999;cursor:pointer;animation:cmfloat 3.2s ease-in-out infinite;filter:drop-shadow(0 8px 14px rgba(0,0,0,.18))';
    const face=d.createElement('div'); face.style.cssText='width:100%;height:100%;background-size:300% 300%;background-repeat:no-repeat;transition:transform .2s';
    const bub=d.createElement('div'); bub.style.cssText='position:absolute;right:88px;bottom:70px;background:#0B0B0F;color:#fff;padding:8px 12px;border-radius:14px;font:600 12px Inter,sans-serif;white-space:nowrap;opacity:0;transform:scale(.8);transition:all .25s';
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
    """Ask the mascot to react. Moods: happy love sparkle surprised starry blush sleepy dizzy laugh"""
    st.session_state["mascot"] = (mood, text)


def mascot():
    """Draws the floating mascot (call last, so it can react to what just happened)."""
    mood = st.session_state.pop("mascot", None)
    pending = f"window.__pendingMood={json.dumps(list(mood))};" if mood else ""
    _run_in_parent(pending + MASCOT_JS)
