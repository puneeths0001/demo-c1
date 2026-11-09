"""Per-visitor memory. Everything lives in st.session_state, so one student never sees another's data.
Because it resets on refresh, the sidebar offers Backup (download) / Restore (upload) as a JSON file."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

import streamlit as st

KEYS = ["expenses", "reminders", "subjects", "settings"]


def now():
    """Current Indian time (cloud servers run in UTC)."""
    return datetime.now(ZoneInfo("Asia/Kolkata")).replace(tzinfo=None)


def get(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]


def export_json():
    return json.dumps({k: st.session_state[k] for k in KEYS if k in st.session_state}, indent=2, default=str)


def import_json(text):
    data = json.loads(text)
    for k in KEYS:
        if k in data:
            st.session_state[k] = data[k]
