"""Feature 3: expense tracker with category, payment method and a monthly limit."""
import pandas as pd
import plotly.express as px
import streamlit as st

from core import store, ui

CATEGORIES = ["Food", "Travel", "Books", "Recharge", "Rent", "Shopping", "Entertainment", "Other"]
METHODS = ["UPI", "Cash", "Debit card", "Credit card", "Net banking"]


def render():
    ui.page_header("Expense Tracker", "Money › Expenses")
    settings = store.get("settings", {})
    rows = store.get("expenses", [])

    settings["limit"] = st.number_input("Monthly limit (₹)", min_value=0, value=int(settings.get("limit", 5000)), step=500)
    limit = settings["limit"]

    with st.form("exp_form", clear_on_submit=True):
        a, b, c, d = st.columns(4)
        date = a.date_input("Date", store.now().date(), format="DD/MM/YYYY")
        amount = b.number_input("Amount (₹)", min_value=0.0, step=10.0)
        cat = c.selectbox("Spent on", CATEGORIES, accept_new_options=True)
        method = d.selectbox("Paid by", METHODS)
        if st.form_submit_button("Add expense", type="primary") and amount > 0:
            rows.append({"date": str(date), "amount": float(amount), "category": cat, "method": method})
            ui.react("love", "Saved!")
            st.rerun()

    month = store.now().strftime("%Y-%m")
    spent = sum(r["amount"] for r in rows if r["date"].startswith(month))
    m1, m2, m3 = st.columns(3)
    m1.markdown(ui.stat_card("Spent this month", f"₹{spent:,.0f}", dark=True), unsafe_allow_html=True)
    m2.markdown(ui.stat_card("Limit", f"₹{limit:,.0f}", delay=0.1), unsafe_allow_html=True)
    m3.markdown(ui.stat_card("Left", f"₹{limit - spent:,.0f}", delay=0.2), unsafe_allow_html=True)
    st.write("")
    if limit:
        st.progress(min(spent / limit, 1.0), text=f"{spent / limit:.0%} of your limit used")
        if spent > limit:
            st.error(f"⚠️ Limit crossed by ₹{spent - limit:,.0f}. Cut spending for the rest of the month.")
            ui.react("dizzy", "Over budget!")
        elif spent > 0.8 * limit:
            st.warning("You have used more than 80% of your monthly limit.")

    if not rows:
        st.info("No expenses yet. Add your first one above.")
        return
    df = pd.DataFrame(rows)
    p, q = st.columns(2)
    p.plotly_chart(px.pie(df, values="amount", names="category", hole=.55, title="Where the money went"), use_container_width=True)
    q.plotly_chart(px.bar(df.groupby("method", as_index=False)["amount"].sum(), x="method", y="amount", title="By payment method"), use_container_width=True)

    st.markdown("**All expenses** (tick 🗑 and press Delete to remove)")
    show = df.iloc[::-1].copy()
    show.insert(0, "🗑", False)
    edited = st.data_editor(show, hide_index=True, use_container_width=True, disabled=["date", "amount", "category", "method"], key="exp_table")
    if st.button("Delete ticked rows") and edited["🗑"].any():
        drop = set(edited.index[edited["🗑"]])
        st.session_state["expenses"] = [r for i, r in enumerate(rows) if i not in drop]
        st.rerun()
