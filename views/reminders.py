"""Feature 2: speak or type a reminder. Gemini finds the task, date and type. Due-soon alerts go to Telegram."""
import hashlib
import html
from datetime import datetime, time as dtime, timedelta

import streamlit as st
from streamlit_autorefresh import st_autorefresh

from core import gemini, notify, store, ui

KINDS = {"assignment": ("📝", "Assignment"), "exam": ("🎯", "Exam"),
         "announcement": ("📢", "Announcement"), "holiday": ("🎉", "Holiday")}


def _ai_parse(words=None, audio=None):
    today = store.now()
    prompt = (f"Today is {today:%Y-%m-%d (%A)}. A student saved a reminder "
              f"{'in the audio' if audio else 'as text: ' + words}. Reply ONLY with JSON: "
              '{"task": "short title", "date": "YYYY-MM-DD or null", "time": "HH:MM or null", '
              '"kind": "assignment|exam|announcement|holiday"}. If a date has no time use 09:00.')
    return gemini.parse_json(gemini.ask(prompt, audio=audio))


def _add(kind, task, due):
    items = store.get("reminders", [])
    items.append({"id": f"{len(items)}{int(store.now().timestamp())}", "kind": kind, "task": task,
                  "due": due.isoformat() if due else None, "notified": False})
    ui.react("love", "I'll remind you!")
    st.toast(f"Added: {task}")


def _chip(due):
    if not due:
        return '<span class="cm-chip">No date</span>'
    d = datetime.fromisoformat(due)
    left = d - store.now()
    cls, tag = ("r", "Overdue") if left < timedelta(0) else ("o", "Within 24h") if left < timedelta(hours=24) else ("g", "Upcoming")
    return f'<span class="cm-chip {cls}">{d:%a %d %b, %I:%M %p} · {tag}</span>'


def render():
    ui.page_header("Reminders", "Study › Voice reminders")
    st_autorefresh(interval=60_000, key="rem_tick")          # check deadlines every minute while the page is open
    items = store.get("reminders", [])

    c1, c2 = st.columns(2)
    with c1:
        with st.form("rem_form", clear_on_submit=True):
            text = st.text_input("Type a reminder", placeholder="Maths assignment due Friday 5 pm")
            kind = st.selectbox("Type", list(KINDS), format_func=lambda k: f"{KINDS[k][0]} {KINDS[k][1]}")
            d1, d2 = st.columns(2)
            date = d1.date_input("Deadline (optional)", value=None)
            tm = d2.time_input("Time", value=dtime(9, 0))
            if st.form_submit_button("Add reminder", type="primary") and text.strip():
                due = datetime.combine(date, tm) if date else None
                task = text.strip()
                if not due and gemini.api_key():                 # no date picked: let Gemini find one in the sentence
                    try:
                        data = _ai_parse(words=task)
                        task = data.get("task") or task
                        if data.get("date"):
                            due = datetime.strptime(f"{data['date']} {data.get('time') or '09:00'}", "%Y-%m-%d %H:%M")
                    except (gemini.GeminiError, ValueError):
                        pass
                _add(kind, task, due)
    with c2:
        audio = st.audio_input("🎤 Or speak it (“DBMS exam on 24 November at 10 am”)")
        if audio:
            data = audio.getvalue()
            digest = hashlib.md5(data).hexdigest()
            if st.session_state.get("last_rem_voice") != digest:
                st.session_state["last_rem_voice"] = digest
                try:
                    with ui.loading("Understanding what you said…"):
                        res = _ai_parse(audio=data)
                    due = None
                    if res.get("date"):
                        due = datetime.strptime(f"{res['date']} {res.get('time') or '09:00'}", "%Y-%m-%d %H:%M")
                    _add(res.get("kind") if res.get("kind") in KINDS else "assignment", res.get("task", "Reminder"), due)
                except (gemini.GeminiError, ValueError) as e:
                    st.error(f"Could not understand that: {e}")

    tabs = st.tabs(["All"] + [f"{i} {n}" for i, n in KINDS.values()])
    for tab, which in zip(tabs, [None] + list(KINDS)):
        with tab:
            mine = sorted([r for r in items if which in (None, r["kind"])], key=lambda r: (r["due"] is None, r["due"] or ""))
            if not mine:
                st.caption("Nothing here yet.")
            for r in mine:
                a, b = st.columns([8, 1], vertical_alignment="center")
                a.markdown(f"{KINDS[r['kind']][0]} **{html.escape(r['task'])}**  \n{_chip(r['due'])}", unsafe_allow_html=True)
                if b.button("✓", key=f"done_{which}_{r['id']}", help="Done"):
                    items.remove(r)
                    ui.react("starry", "Nice work!")
                    st.rerun()

    soon = [r for r in items if r["due"] and not r["notified"] and timedelta(0) < datetime.fromisoformat(r["due"]) - store.now() < timedelta(hours=24)]
    if soon:
        st.warning(f"{len(soon)} item(s) due in the next 24 hours.")
    with st.expander("📲 Get these reminders on my Telegram"):
        if notify.link_widget("student", "You") and soon:
            ok, _ = notify.send_message("student", "⏰ CampusMate reminders:\n" + "\n".join(f"• {r['task']} ({datetime.fromisoformat(r['due']):%d %b %I:%M %p})" for r in soon))
            if ok:
                for r in soon:
                    r["notified"] = True
                st.toast("Reminders sent to your Telegram")
    st.caption("Alerts are sent while this page is open. Alerts with the app closed need a background server (future scope).")
