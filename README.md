# 🎓 CampusMate: safety + study + money app for students

Python + Streamlit. Features: live location & SOS (Telegram), voice reminders, expense tracker,
scam detector, VTU SGPA/CGPA planner, AI study buddy (chat + notes → flowchart).

## Folder map
```
app.py                 starts the app, sidebar menu
core/                  helpers: ui.py (look, intro, mascot) · gemini.py · notify.py (Telegram)
                       scam_rules.py · link_check.py · store.py
views/                 one file per page: home, safety, reminders, expenses, scam, cgpa, ai_buddy
static/                mascot pictures
.streamlit/config.toml theme + static file serving
requirements.txt       libraries to install
```

## STEP 1: Install tools (one time)
Python 3.11+ (tick "Add Python to PATH") · VS Code (+ Python extension) · Git.

## STEP 2: Open and run on your laptop
VS Code → File → Open Folder → this folder → Terminal → New Terminal:
```bash
python -m venv .venv
.venv\Scripts\activate            # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## STEP 3: Get your keys
| Key | Where | Needed for |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com → Get API key (free) | voice SOS, voice reminders, chat, flowcharts |
| `TELEGRAM_BOT_TOKEN` | Telegram → search **@BotFather** → `/newbot` | SOS + location + reminders to Telegram |
| `VIRUSTOTAL_API_KEY` | https://www.virustotal.com (free account) | optional extra link check |

Laptop: copy `.streamlit/secrets.toml.example` → `.streamlit/secrets.toml` and fill it in.

## STEP 4: Connect Telegram (inside the app)
Safety page → Step 1 → the parent opens the link, taps **Start** → press "I pressed Start".
Reminders page → "Get these reminders on my Telegram" does the same for the student.

## STEP 5: New GitHub repo
1. github.com → **New repository** → name `campusmate` → Public → Create (do NOT add README).
2. In the VS Code terminal:
```bash
git init
git add .
git commit -m "CampusMate"
git branch -M main
git remote add origin https://github.com/<your-username>/campusmate.git
git push -u origin main
```
`secrets.toml` is in `.gitignore`, so your keys are NOT uploaded.

## STEP 6: Make it live (Streamlit Community Cloud, free)
1. https://share.streamlit.io → sign in with GitHub → **Create app**.
2. Repository `campusmate`, branch `main`, main file path `app.py`.
3. **Advanced settings → Secrets** → paste your keys in the same format as `secrets.toml.example`.
4. Deploy. You get a link like `https://campusmate.streamlit.app`.
After any change: `git add . && git commit -m "update" && git push`, and the live site updates by itself.

## Troubleshooting
- **Orbs/mascot not showing:** hard refresh (Ctrl+Shift+R). Check `static/` was pushed to GitHub.
- **Location never appears:** click Allow in the browser; the site must be https (Streamlit Cloud is).
- **Gemini 404:** the model name changed; set `GEMINI_MODEL` in secrets to a current Flash model.
- **Telegram "Nothing found":** press Start in Telegram first, wait 5 seconds, try again.
