"""Feature 1: live location every 5 minutes + SOS (button or the spoken word 'help') -> parent's Telegram."""
import hashlib
import time

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from streamlit_js_eval import get_geolocation

from core import gemini, notify, store, ui

INTERVAL = 300  # seconds = 5 minutes


def _record(lat, lon, bucket):
    """Save the point and push it to the parent (only once per 5-minute slot)."""
    if st.session_state.get("loc_bucket") == bucket:
        return
    st.session_state["loc_bucket"] = bucket
    st.session_state["last_loc"] = {"lat": lat, "lon": lon, "time": f"{store.now():%d %b %H:%M}"}
    store.get("loc_history", []).append(st.session_state["last_loc"])
    notify.share_live("parent", lat, lon)


def _sos(reason):
    loc = st.session_state.get("last_loc")
    name = store.get("settings", {}).get("name", "Your child")
    text = f"🚨 EMERGENCY! {name} needs help ({reason}) at {store.now():%d %b %H:%M}."
    text += f"\nLast location: https://maps.google.com/?q={loc['lat']},{loc['lon']}" if loc else "\nLocation not available yet."
    ok, err = notify.send_message("parent", text)
    if loc:
        notify.share_live("parent", loc["lat"], loc["lon"])
    ui.react("surprised", "SOS sent!" if ok else "Not sent…")
    if ok:
        st.error("🚨 SOS sent to your parent on Telegram.")
    else:
        st.warning(f"SOS could not be sent: {err}. Connect your parent first (Step 1).")


def render():
    ui.page_header("Safety & Live Location", "Safety › SOS")

    st.markdown("**Step 1: connect your parent's Telegram** (one time)")
    parent_ok = notify.link_widget("parent", "Parent")

    st.markdown("**Step 2: share your live location**")
    share = st.toggle("📍 Share my location with my parent every 5 minutes")
    if share:
        st_autorefresh(interval=INTERVAL * 1000, key="loc_tick")            # re-run this page every 5 min
        bucket = int(time.time() // INTERVAL)
        geo = get_geolocation(component_key=f"geo_{bucket}")                # new key each slot => fresh GPS reading
        coords = geo.get("coords") if isinstance(geo, dict) else None
        if coords:
            _record(coords["latitude"], coords["longitude"], bucket)
            st.success("Sharing is on." + (" Your parent sees a live pin in Telegram." if parent_ok else " Connect Telegram in Step 1."))
        else:
            st.info("Waiting for location. Click **Allow** when your browser asks.")
    hist = store.get("loc_history", [])
    if hist:
        st.map(pd.DataFrame(hist[-30:]), latitude="lat", longitude="lon", size=25)
        st.caption(f"Last update: {hist[-1]['time']}")

    st.markdown("**Step 3: in danger?**")
    c1, c2 = st.columns(2)
    if c1.button("🚨 SOS: I need help", type="primary", use_container_width=True):
        _sos("SOS button")
    with c2:
        voice = st.audio_input("🎤 Or record yourself saying “help”")
    if voice:
        data = voice.getvalue()
        digest = hashlib.md5(data).hexdigest()
        if st.session_state.get("last_voice") != digest:           # handle each recording only once
            st.session_state["last_voice"] = digest
            try:
                with ui.loading("Listening…"):
                    heard = gemini.parse_json(gemini.ask(
                        'Listen to the audio. Reply ONLY with JSON {"help": true or false}. '
                        "true if the person calls for help (help, save me, bachao, kapadi, etc.).", audio=data))
                if heard.get("help"):
                    _sos("voice: help")
                else:
                    st.info("No emergency word heard.")
            except gemini.GeminiError as e:
                st.error(str(e))

    if parent_ok:
        st.divider()
        if st.button("📨 Check replies from my parent"):
            msgs = notify.replies("parent")
            for m in msgs:
                st.write("👨‍👩‍👧 " + m)
            if not msgs:
                st.info("No messages yet.")
    st.caption("Limits: the page must stay open with location allowed. Always-on background listening needs a mobile app (future scope).")
