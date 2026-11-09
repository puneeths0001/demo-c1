"""Feature 5: marks -> grades -> SGPA / CGPA, where to improve, and a target planner (VTU 10-point scale)."""
import pandas as pd
import plotly.express as px
import streamlit as st

from core import store, ui

POINTS = {"O": 10, "A+": 9, "A": 8, "B+": 7, "B": 6, "C": 5, "P": 4, "F": 0}
DEFAULT_FROM = {"O": 90, "A+": 80, "A": 70, "B+": 60, "B": 55, "C": 50, "P": 40}   # editable in the page


def grade_of(marks, scale):
    for g in POINTS:                       # best grade first
        if marks >= scale.get(g, 0):
            return g
    return "F"


def next_grade(g):
    keys = list(POINTS)
    i = keys.index(g)
    return keys[i - 1] if i > 0 else None


def compute(df, scale):
    """Adds Grade, Points and 'SGPA lost' columns. Returns (table, sgpa, total_credits)."""
    t = df.dropna(subset=["Credits", "Marks"]).copy()
    t = t[t["Credits"] > 0]
    if t.empty:
        return t, 0.0, 0.0
    t["Grade"] = t["Marks"].map(lambda m: grade_of(m, scale))
    t["Points"] = t["Grade"].map(POINTS)
    total = float(t["Credits"].sum())
    t["Lost"] = t["Credits"] * (10 - t["Points"]) / total       # SGPA you lose because of this subject
    return t, float((t["Credits"] * t["Points"]).sum() / total), total


def render():
    ui.page_header("SGPA / CGPA Planner", "Study › Marks (VTU)")
    st.caption("10-point scale · SGPA = Σ(credits × grade points) ÷ Σ credits")
    scale = {"F": 0}
    with st.expander("Grade scale: marks → grade (editable, check your scheme document)"):
        cols = st.columns(4)
        for i, g in enumerate(DEFAULT_FROM):
            scale[g] = cols[i % 4].number_input(f"{g} from", 0, 100, DEFAULT_FROM[g], key=f"sc_{g}")

    base = pd.DataFrame(store.get("subjects", [{"Subject": "Maths", "Credits": 4, "Marks": 68}, {"Subject": "Physics", "Credits": 3, "Marks": 82},
                                               {"Subject": "Programming", "Credits": 4, "Marks": 75}, {"Subject": "English", "Credits": 2, "Marks": 85}]))
    st.write("Enter your **final marks out of 100**. Use the **+** row at the bottom to add subjects.")
    edited = st.data_editor(base, num_rows="dynamic", use_container_width=True, key="cg_editor",
                            column_config={"Subject": st.column_config.TextColumn(required=True),
                                           "Credits": st.column_config.NumberColumn(min_value=1, max_value=10, step=1, required=True),
                                           "Marks": st.column_config.NumberColumn("Final marks", min_value=0, max_value=100, step=1, required=True)})
    if st.button("💾 Keep these subjects"):
        st.session_state["subjects"] = edited.dropna().to_dict("records")
        ui.react("starry", "Saved!")

    table, sgpa, total = compute(edited, scale)
    if table.empty:
        st.info("Add at least one subject with credits and marks.")
        return
    avg = float((table["Credits"] * table["Marks"]).sum() / total)
    a, b = st.columns(2)
    a.markdown(ui.stat_card("Your SGPA", f"{sgpa:.2f}", dark=True), unsafe_allow_html=True)
    b.markdown(ui.stat_card("Average marks (by credits)", f"{avg:.1f}", delay=0.1), unsafe_allow_html=True)
    st.write("")

    st.markdown("#### 📉 Where to improve")
    worst = table.sort_values("Lost", ascending=False)
    st.caption("Bar = SGPA points this subject is costing you. Big credits + low grade = biggest loss.")
    st.plotly_chart(px.bar(worst, x="Lost", y="Subject", orientation="h", color="Lost", color_continuous_scale=["#2F5BFF", "#FF5A5A"],
                           labels={"Lost": "SGPA lost"}).update_layout(coloraxis_showscale=False, yaxis=dict(autorange="reversed")),
                    use_container_width=True)

    tips = []
    for _, r in table.iterrows():
        nxt = next_grade(r["Grade"])
        if nxt:
            need = max(0, scale[nxt] - r["Marks"])
            gain = r["Credits"] * (POINTS[nxt] - r["Points"]) / total
            tips.append((r["Subject"], nxt, need, gain))
    wins = sorted([t for t in tips if t[2] > 0], key=lambda t: t[3] / t[2], reverse=True)[:3]
    for sub, nxt, need, gain in wins:
        st.success(f"**{sub}**: just **{need:.0f} more marks** lifts it to **{nxt}** and adds **+{gain:.2f}** to your SGPA.")
    top = worst.iloc[0]
    if top["Lost"] > 0:
        st.info(f"Biggest loss: **{top['Subject']}** ({top['Credits']:.0f} credits) costs you {top['Lost']:.2f} SGPA points.")

    st.markdown("#### 🎯 Overall CGPA & target")
    c1, c2, c3 = st.columns(3)
    old_cgpa = c1.number_input("CGPA before this semester", 0.0, 10.0, 7.5, 0.01)
    old_cr = c2.number_input("Credits done before", 0, 300, 40)
    target = c3.number_input("Target CGPA", 0.0, 10.0, 8.5, 0.1)
    cgpa = (old_cgpa * old_cr + sgpa * total) / (old_cr + total)
    st.markdown(ui.stat_card("New CGPA", f"{cgpa:.2f}", f"≈ {(cgpa - 0.75) * 10:.1f}%", "b"), unsafe_allow_html=True)
    st.caption("Percentage uses the VTU formula (CGPA − 0.75) × 10. Confirm with your college circular.")
    left = st.number_input("Credits still to complete (after this semester)", 0, 300, 40)
    if left:
        need = (target * (old_cr + total + left) - cgpa * (old_cr + total)) / left
        if need > 10:
            st.error(f"To reach {target} you would need an SGPA of {need:.2f} (above 10). Lower the target.")
        else:
            st.info(f"To finish on CGPA **{target}**, average an SGPA of **{max(need, 0):.2f}** over your remaining {left} credits.")
