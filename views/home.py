"""Overview page: four stat cards, next deadlines, spending chart and the feature grid."""
import html
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

from core import store, ui


def month_spent():
    month = store.now().strftime("%Y-%m")
    return sum(e["amount"] for e in store.get("expenses", []) if str(e["date"]).startswith(month))


def render():
    ui.page_header("Overview", "Home › Today")
    settings = store.get("settings", {})
    limit = float(settings.get("limit", 5000))
    spent = month_spent()
    todo = sorted([r for r in store.get("reminders", []) if r["due"]], key=lambda r: r["due"])
    loc = st.session_state.get("last_loc")

    cards = [
        ui.stat_card("Spent this month", f"₹{spent:,.0f}", f"{spent / limit:.0%}" if limit else "", "r" if limit and spent > limit else "g", dark=True),
        ui.stat_card("Budget left", f"₹{max(limit - spent, 0):,.0f}", delay=0.1),
        ui.stat_card("Pending reminders", str(len(store.get("reminders", []))), delay=0.2),
        ui.stat_card("Last location shared", loc["time"] if loc else "—", "live" if loc else "", "b", delay=0.3),
    ]
    for col, card in zip(st.columns(4), cards):
        col.markdown(card, unsafe_allow_html=True)
    st.write("")

    a, b = st.columns(2)
    with a:
        with st.container(border=True):
            st.markdown("**Next deadlines**")
            for r in todo[:4]:
                due = datetime.fromisoformat(r["due"])
                st.markdown(f"{html.escape(r['task'])}  \n<span class='cm-chip'>{due:%a %d %b, %I:%M %p}</span>", unsafe_allow_html=True)
            if not todo:
                st.caption("Nothing with a deadline yet. Add one in Reminders.")
    with b:
        with st.container(border=True):
            st.markdown("**Spending by category**")
            exp = store.get("expenses", [])
            if exp:
                df = pd.DataFrame(exp)
                st.plotly_chart(px.pie(df, values="amount", names="category", hole=.6, height=220).update_layout(margin=dict(t=0, b=0, l=0, r=0)),
                                use_container_width=True)
            else:
                st.caption("No expenses yet.")

    st.markdown("#### What CampusMate does")
    feats = [("🚨", "Safety SOS", "Say “help” and your parent gets your live location."),
             ("⏰", "Voice reminders", "Speak a deadline once. We remind you before it is due."),
             ("💸", "Expense tracker", "See where money goes and when you cross your limit."),
             ("🛡️", "Scam detector", "Paste a link or offer and get a risk score with proof."),
             ("🎓", "CGPA planner", "Find which subjects pull your CGPA down."),
             ("🤖", "AI study buddy", "Chat, or turn messy notes into a flowchart.")]
    for i, row in enumerate((feats[:3], feats[3:])):
        for col, (icon, t, text) in zip(st.columns(3), row):
            col.markdown(ui.feature_card(icon, t, text, delay=0.1 * i), unsafe_allow_html=True)
