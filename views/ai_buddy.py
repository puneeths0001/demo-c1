"""Feature 6: AI chat + notes -> flowchart (Graphviz) using Google Gemini."""
import re

import streamlit as st

from core import gemini, ui

SYSTEM = ("You are CampusMate, a friendly study assistant for Indian engineering (VTU) students. "
          "Explain simply with short examples. Keep answers concise.")


def _flow_prompt(notes, rank):
    return (f"Turn these study notes into a clear flowchart in Graphviz DOT. Reply with DOT code only, starting with 'digraph'. "
            f"Use rankdir={rank}; node [shape=box, style=\"rounded,filled\", fillcolor=\"#EAF0FF\", fontname=\"Helvetica\", fontcolor=\"#0B0B0F\"]; "
            f"edge [color=\"#6B6E7B\"]. Labels under 6 words, diamonds for decisions, at most 18 nodes, group the main ideas.\n\nNOTES:\n{notes}")


def _fallback_dot(notes, rank):
    """No AI key? Chain the note lines into a basic flowchart so the demo still works."""
    lines = [l.strip(" -•*\t") for l in re.split(r"[\n.]+", notes) if l.strip()][:14]
    nodes = "\n".join(f'n{i} [label="{l[:46].replace(chr(34), chr(39))}"];' for i, l in enumerate(lines))
    edges = "\n".join(f"n{i} -> n{i + 1};" for i in range(len(lines) - 1))
    return (f'digraph {{ rankdir={rank}; node [shape=box, style="rounded,filled", fillcolor="#EAF0FF", fontname="Helvetica"];\n{nodes}\n{edges}\n}}')


def render():
    ui.page_header("AI Study Buddy", "Study › AI")
    chat_tab, flow_tab = st.tabs(["💬 Chat", "🧠 Notes → Flowchart"])

    with chat_tab:
        hist = st.session_state.setdefault("chat", [])
        for m in hist:
            with st.chat_message(m["role"]):
                st.write(m["content"])
        if q := st.chat_input("Ask me anything about your studies…"):
            hist.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.write(q)
            with st.chat_message("assistant"):
                try:
                    with ui.loading("Thinking…"):
                        contents = [{"role": "user" if m["role"] == "user" else "model", "parts": [{"text": m["content"]}]} for m in hist[-12:]]
                        ans = gemini.generate(contents, SYSTEM)
                    ui.react("sparkle", "Got it!")
                except gemini.GeminiError as e:
                    ans = f"Sorry, I could not answer: {e}"
                st.write(ans)
            hist.append({"role": "assistant", "content": ans})

    with flow_tab:
        notes = st.text_area("Paste your notes", height=200, placeholder="TCP handshake: client sends SYN. Server replies SYN-ACK. Client sends ACK. Connection established.")
        direction = st.radio("Layout", ["Top to bottom", "Left to right"], horizontal=True)
        if st.button("Make flowchart", type="primary") and notes.strip():
            rank = "TB" if direction == "Top to bottom" else "LR"
            try:
                with ui.loading("Drawing your flowchart…"):
                    dot = gemini.strip_fences(gemini.ask(_flow_prompt(notes, rank)))
                if "digraph" not in dot:
                    raise gemini.GeminiError("The AI did not return a diagram.")
            except gemini.GeminiError as e:
                st.warning(f"AI unavailable ({e}). Showing a basic flowchart instead.")
                dot = _fallback_dot(notes, rank)
            st.session_state["dot"] = dot
            ui.react("starry", "Revision ready!")
        if dot := st.session_state.get("dot"):
            st.graphviz_chart(dot, use_container_width=True)
            st.download_button("⬇ Download DOT file", dot, "flowchart.dot")
            with st.expander("See the Graphviz code"):
                st.code(dot)
