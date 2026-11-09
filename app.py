"""CampusMate: main file. Streamlit re-runs this top to bottom on every click."""
import streamlit as st

st.set_page_config(page_title="CampusMate", page_icon="🎓", layout="wide")

from core import store, ui                                                          # noqa: E402
from views import ai_buddy, cgpa, expenses, home, reminders, safety, scam            # noqa: E402

ui.inject_css()     # dashboard styling (video 1)
ui.orbs_intro()     # Thinking-Orbs opening animation (video 2), once per visit

PAGES = {"🏠  Overview": home, "🚨  Safety & SOS": safety, "⏰  Reminders": reminders, "💸  Expenses": expenses,
         "🛡️  Scam Detector": scam, "🎓  CGPA Planner": cgpa, "🤖  AI Study Buddy": ai_buddy}

settings = store.get("settings", {})
with st.sidebar:
    st.markdown('<div class="cm-brand"><div class="cm-logo">🎓</div>CampusMate</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="cm-welcome">Welcome back,<br>{settings.get("name", "Student")}!</div><div class="cm-sub">Your day at a glance</div>', unsafe_allow_html=True)
    page = st.radio("Menu", list(PAGES), label_visibility="collapsed")
    settings["name"] = st.text_input("Your name", value=settings.get("name", "Student"))

    with st.expander("🔑 API keys (optional)"):
        st.caption("Only needed if you did not put them in secrets.")
        st.text_input("Gemini API key", type="password", key="gem_key")
        st.text_input("VirusTotal API key", type="password", key="vt_key")
    with st.expander("💾 Backup / restore my data"):
        st.caption("Your data lives only in this browser tab. Download a backup to keep it.")
        st.download_button("Download backup", store.export_json(), "campusmate_backup.json")
        up = st.file_uploader("Restore from backup", type="json")
        if up and st.session_state.get("restored") != up.file_id:
            try:
                store.import_json(up.getvalue().decode())
                st.session_state["restored"] = up.file_id
                st.rerun()
            except ValueError:
                st.error("That file is not a CampusMate backup.")

PAGES[page].render()
ui.mascot()         # drawn last so it can react to what just happened
