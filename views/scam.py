"""Feature 4: rules + LIVE checks for fake links, emails, internships and scholarships."""
import streamlit as st

from core import link_check, scam_rules, ui


def _vt_key():
    try:
        return st.secrets["VIRUSTOTAL_API_KEY"]
    except Exception:
        return st.session_state.get("vt_key", "")


def render():
    ui.page_header("Scam Detector", "Safety › Fake links & offers")
    st.write("Paste a link, an email, or an internship / scholarship offer.")
    text = st.text_area("Paste here", height=190, placeholder="Congratulations! You are selected. Pay a registration fee at http://...")

    if st.button("🔍 Check now", type="primary") and text.strip():
        score, reasons = scam_rules.analyze(text)                    # step 1: warning-sign rules
        extra, threat, cards = 0, False, []
        for url in scam_rules.find_urls(text)[:3]:                   # step 2: live checks on each link
            full = url if url.startswith("http") else "http://" + url
            with ui.loading(f"Checking {full[:50]}…"):
                lines, pts, why, bad = link_check.inspect(full, _vt_key())
            extra += pts
            reasons += why
            threat = threat or bad
            cards.append((full, lines))

        score = min(100, score + extra)
        if threat:
            score = max(score, 70)
        level = "Low risk" if score < 25 else "Medium risk" if score < 55 else "High risk"
        a, b = st.columns(2)
        a.markdown(ui.stat_card("Risk score", f"{score} / 100", dark=True), unsafe_allow_html=True)
        b.markdown(ui.stat_card("Verdict", "Known threat" if threat else level, delay=0.1), unsafe_allow_html=True)
        st.write("")
        st.progress(score / 100)
        if threat or score >= 55:
            st.error("Do not click, reply or pay. Show it to a teacher or your college placement cell.")
            ui.react("surprised", "Careful!")
        elif score >= 25:
            st.warning("Be careful. Check the sender on the official website before doing anything.")
        else:
            st.success("No known threats and no strong warning signs. That is not proof the link is safe.")
            ui.react("happy", "Looks OK")
        for url, lines in cards:
            with st.container(border=True):
                st.write(f"**Live check: {url}**")
                for line in lines:
                    st.write(line)
        if reasons:
            st.markdown("#### Why")
            for r in dict.fromkeys(reasons):
                st.write("• " + r)
    st.caption("No tool can prove a link is 100% safe. This shows live signals and evidence. Never pay to get an internship or scholarship.")
