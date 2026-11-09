# CampusMate: Judges' Guide

**Problem:** students juggle safety, deadlines, money, marks and scams across many apps.
**Solution:** one web app with six tools. **Language:** Python 3. **Framework:** Streamlit.

## Libraries used (and why)
| Library | Purpose |
|---|---|
| streamlit | Builds the website from Python: pages, forms, charts, chat, maps, microphone input |
| pandas | Tables (expenses, subjects/marks) |
| plotly | Interactive pie and bar charts |
| requests | Calls 4 web APIs: Telegram, Google Gemini, VirusTotal, RDAP (domain age) |
| streamlit-js-eval | Reads the browser's GPS location |
| streamlit-autorefresh | Re-runs the page every 5 min (location) / 1 min (reminders) |
| tzdata | Indian time zone (cloud servers run in UTC) |
| Graphviz (built into `st.graphviz_chart`) | Draws flowcharts from text |
| Python standard library | re, json, datetime, hashlib, difflib, ipaddress, socket, urllib |
| Frontend (inside `core/ui.py`) | CSS, and ~60 lines of JavaScript canvas for the opening animation and mascot |
**External services:** Google Gemini (AI), Telegram Bot API (alerts), VirusTotal (optional).

## Files: what each does
- `app.py`: entry point. Applies the look, plays the intro, builds the sidebar menu, runs the chosen page, draws the mascot.
- `core/ui.py`: the design from our reference dashboard, the **Thinking Orbs** intro (260 dots on a sphere → 24 morph into a ring → fade) and the **mascot** (eyes follow the mouse using a 3×3 sprite sheet; reaction sprite sheet for emotions).
- `core/gemini.py`: sends text or recorded audio to Gemini; tries a backup model if one is retired.
- `core/notify.py`: Telegram: private link code per visitor, messages, live location pin that moves every 5 min.
- `core/scam_rules.py`: rule engine. `core/link_check.py`: live checks. `core/store.py`: per-visitor memory + backup.
- `views/*.py`: one file per page.

## How each feature works
1. **Safety & SOS:** the browser gives GPS; every 5 minutes the page refreshes, takes a new reading and moves a *live location pin* in the parent's Telegram. SOS = button, or the student records "help" and **Gemini listens to the audio** (works for Hindi/Kannada words like "bachao" too). The bot sends a message + Google Maps link + live pin.
2. **Reminders:** voice or text → Gemini extracts task, date, time, and type (assignment/exam/announcement/holiday) → saved. Items due within 24 h are flagged and sent to the student's Telegram.
3. **Expenses:** amount, category, payment method; compares the month total with the limit; warning at 80%, alert when crossed.
4. **Scam detector (two layers):** (a) *rules*: each red flag adds points (fee requests, OTP asks, look-alike brand domains like `paypa1`, risky domain endings…); (b) *live checks*: follows redirects to the real destination, checks the SSL certificate, looks up domain age (new domains = risky), and asks VirusTotal. Score ≥ 55 = high risk. Every score comes with reasons, so it is explainable. A safety guard stops our server opening private/internal addresses.
5. **CGPA planner:** marks → grade → grade points. SGPA = Σ(credits × grade points) ÷ Σ credits. "SGPA lost" per subject = credits × (10 − points) ÷ total credits, so high-credit weak subjects rank first. Tips compute the marks needed for the next grade. Target planner solves the SGPA needed in remaining credits.
6. **AI study buddy:** chat with memory of the last 12 messages; notes → Gemini writes Graphviz code → drawn as a flowchart. If the AI is unavailable, a basic flowchart is still drawn from the note lines.

## Privacy & design choices
- Each visitor's data lives only in their own browser session (nothing is shared between users). Backup/restore as a JSON file.
- Keys are stored in Streamlit Secrets, never in GitHub.

## Honest limitations (say these, judges respect honesty)
- Scam detection is a first check, not a guarantee.
- Alerts work while the app is open in a browser tab; true background alerts need a server/database (future scope), as does always-on voice listening (a mobile app).
- Data resets on refresh unless the student downloads a backup (future: a database such as Supabase).
- Grade bands follow the standard VTU 10-point table and are editable; confirm against your scheme document.
