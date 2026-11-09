"""Telegram bot helper. Each visitor links their OWN parent/student chat with a private one-time code,
so nothing is shared between visitors."""
import secrets

import requests
import streamlit as st


def _token():
    try:
        return st.secrets["TELEGRAM_BOT_TOKEN"]
    except Exception:
        return ""


def api(method, **params):
    """Calls the Telegram Bot API. Returns (ok, result_or_error_text)."""
    token = _token()
    if not token:
        return False, "TELEGRAM_BOT_TOKEN is missing in secrets."
    try:
        data = requests.post(f"https://api.telegram.org/bot{token}/{method}", json=params, timeout=20).json()
    except Exception as e:
        return False, str(e)
    return data.get("ok", False), data.get("result", data.get("description", ""))


def _code(role):
    if "tg_code" not in st.session_state:
        st.session_state["tg_code"] = secrets.token_hex(4)
    return f"{role[0]}{st.session_state['tg_code']}"      # e.g. "p3fa91c2d" for the parent


def chat_id(role):
    """A chat id fixed in secrets wins (handy for demos); otherwise the one this visitor linked."""
    try:
        return int(st.secrets[f"TELEGRAM_{role.upper()}_CHAT_ID"])
    except Exception:
        return st.session_state.get(f"chat_{role}")


def _link(role):
    ok, updates = api("getUpdates")
    if ok:
        for u in reversed(updates):
            m = u.get("message", {})
            if m.get("text", "").strip() == f"/start {_code(role)}":
                st.session_state[f"chat_{role}"] = m["chat"]["id"]
                return True
    return False


def link_widget(role, who):
    """Shows the connect steps. Returns True once connected."""
    if chat_id(role):
        st.success(f"✅ {who} is connected on Telegram.")
        return True
    ok, bot = api("getMe")
    if not ok:
        st.error(f"Telegram is not set up: {bot}")
        return False
    st.markdown(f"**{who}:** open this link in Telegram and tap **Start**, then press the button below.")
    st.link_button(f"Open @{bot['username']}", f"https://t.me/{bot['username']}?start={_code(role)}")
    if st.button(f"I pressed Start ({who})", key=f"link_{role}"):
        if _link(role):
            st.rerun()
        st.warning("Nothing found yet. Press Start in Telegram first, wait a few seconds and try again.")
    return False


def send_message(role, text):
    cid = chat_id(role)
    return api("sendMessage", chat_id=cid, text=text) if cid else (False, f"{role} is not connected yet")


def share_live(role, lat, lon):
    """First call sends a LIVE pin (stays on the map 4 hours); later calls just move that pin."""
    cid, mid = chat_id(role), st.session_state.get(f"live_{role}")
    if not cid:
        return False
    if mid and api("editMessageLiveLocation", chat_id=cid, message_id=mid, latitude=lat, longitude=lon)[0]:
        return True
    ok, res = api("sendLocation", chat_id=cid, latitude=lat, longitude=lon, live_period=14400)
    if ok:
        st.session_state[f"live_{role}"] = res["message_id"]
    return ok


def replies(role, n=5):
    """Last few text messages this person sent to the bot."""
    cid = chat_id(role)
    ok, updates = api("getUpdates")
    if not (ok and cid):
        return []
    texts = [u["message"]["text"] for u in updates
             if u.get("message", {}).get("chat", {}).get("id") == cid and not u["message"].get("text", "/").startswith("/")]
    return texts[-n:]
