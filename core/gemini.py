"""Google Gemini through plain web requests (no special SDK needed)."""
import base64
import json
import re

import requests
import streamlit as st

URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"


class GeminiError(Exception):
    pass


def api_key():
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = ""
    return key or st.session_state.get("gem_key", "")


def _models():
    try:
        first = st.secrets["GEMINI_MODEL"]
    except Exception:
        first = ""
    return [m for m in dict.fromkeys([first, "gemini-2.5-flash", "gemini-2.0-flash"]) if m]


def generate(contents, system=None):
    """contents = [{"role": "user"|"model", "parts": [{"text": ...}]}, ...]"""
    key = api_key()
    if not key:
        raise GeminiError("Add your Gemini API key (sidebar → API keys).")
    body = {"contents": contents}
    if system:
        body["system_instruction"] = {"parts": [{"text": system}]}
    last = ""
    for model in _models():                     # if a model name is retired (404) we try the next one
        try:
            r = requests.post(URL.format(model), headers={"x-goog-api-key": key}, json=body, timeout=90)
        except requests.RequestException as e:
            raise GeminiError(f"Could not reach Gemini: {e}")
        if r.status_code == 200:
            try:
                return "".join(p.get("text", "") for p in r.json()["candidates"][0]["content"]["parts"])
            except (KeyError, IndexError):
                raise GeminiError("Gemini returned an empty answer (it may have blocked the request).")
        last = f"{model}: {r.status_code} {r.text[:160]}"
        if r.status_code != 404:
            break
    raise GeminiError(last)


def ask(prompt, audio=None, mime="audio/wav", system=None):
    parts = [{"text": prompt}]
    if audio:                                    # sound is sent as base64 text so Gemini can listen to it
        parts.append({"inline_data": {"mime_type": mime, "data": base64.b64encode(audio).decode()}})
    return generate([{"role": "user", "parts": parts}], system)


def parse_json(text):
    try:
        return json.loads(re.search(r"\{.*\}", text, re.S).group(0))
    except (AttributeError, json.JSONDecodeError):
        raise GeminiError("Could not understand the AI reply. Please try again.")


def strip_fences(text):
    return re.sub(r"^```[a-zA-Z]*\n?|```$", "", text.strip(), flags=re.M).strip()
