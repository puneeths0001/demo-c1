"""Rule-based scam scoring. Every red flag adds risk points and a plain-English reason."""
import re
from difflib import SequenceMatcher
from urllib.parse import urlparse

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly", "rb.gy", "shorturl.at", "tiny.cc"}
RISKY_TLDS = {"xyz", "top", "click", "tk", "ml", "ga", "cf", "gq", "work", "zip", "icu", "buzz", "rest", "loan"}
OFFICIAL = {  # brand word -> its real domains
    "paytm": ["paytm.com"], "phonepe": ["phonepe.com"], "sbi": ["sbi.co.in", "onlinesbi.sbi"], "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com"], "google": ["google.com", "google.co.in"], "amazon": ["amazon.in", "amazon.com"],
    "linkedin": ["linkedin.com"], "microsoft": ["microsoft.com"], "instagram": ["instagram.com"], "whatsapp": ["whatsapp.com"],
    "flipkart": ["flipkart.com"], "internshala": ["internshala.com"], "naukri": ["naukri.com"], "vtu": ["vtu.ac.in"],
    "scholarships": ["scholarships.gov.in"], "paypal": ["paypal.com"], "netflix": ["netflix.com"],
}
FREE_MAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com"}
LEET = str.maketrans("013458@", "oleasba")

TEXT_RULES = [  # (regex, points, reason)
    (r"(registration|processing|security|training|kit|admission|joining|application|verification)\s*(fee|fees|deposit|charges?)", 30,
     "Asks you to PAY a fee. Real internships and scholarships never charge candidates."),
    (r"\brefundable\b", 10, "Mentions a 'refundable' payment, a common scam hook."),
    (r"no interview|without interview|direct selection|guaranteed\s*(job|placement|selection|internship|scholarship)", 20,
     "Promises selection without an interview or test."),
    (r"urgent|immediately|last chance|limited (seats|slots)|act now|within 24 hours|expires today|hurry", 10, "Uses pressure and urgency words."),
    (r"\botp\b|password|\bcvv\b|aadhaar|pan card|bank details|card number|\bupi pin\b", 30,
     "Asks for sensitive details (OTP, password, bank or ID details)."),
    (r"congratulations.{0,40}(selected|won)|lottery|lucky draw|prize|winner", 15, "Looks like a 'you won / you are selected' lure."),
    (r"verify your account|account (is )?(suspended|blocked)|\bkyc\b", 20, "Threatens account blocking to make you click."),
    (r"work from home.{0,60}(earn|₹|rs)|earn\s*(rs\.?|₹|inr)?\s*\d[\d,]*.{0,25}(per|a|/)\s*(day|hour|week)", 15, "Promises easy high earnings."),
    (r"whatsapp|telegram", 8, "Pushes you to chat on WhatsApp/Telegram instead of an official channel."),
    (r"dear (customer|user|candidate|student|applicant)", 6, "Generic greeting instead of your name."),
]


def registered_domain(host):
    p = host.split(".")
    if len(p) >= 3 and len(p[-1]) == 2 and p[-2] in {"co", "com", "org", "gov", "ac", "edu", "nic"}:
        return ".".join(p[-3:])
    return ".".join(p[-2:])


def analyze_url(url):
    """Returns a list of (points, reason)."""
    out = []
    u = urlparse(url if "://" in url else "http://" + url)
    host = (u.hostname or "").lower()
    reg = registered_domain(host)
    official = any(reg in doms for doms in OFFICIAL.values()) or host.endswith((".gov.in", ".ac.in", ".edu"))
    if u.scheme == "http":
        out.append((10, f"{host}: not using secure HTTPS."))
    if re.fullmatch(r"[\d.]+", host):
        out.append((30, f"{host}: uses a raw IP address instead of a name."))
    if "@" in u.netloc:
        out.append((25, f"{host}: has '@' in the link, which hides the real site."))
    if "xn--" in host:
        out.append((25, f"{host}: uses look-alike (punycode) characters."))
    if host.count("-") >= 3:
        out.append((10, f"{host}: has many hyphens."))
    if len(host.split(".")) >= 5:
        out.append((10, f"{host}: has too many sub-domains."))
    if reg in SHORTENERS:
        out.append((15, f"{reg}: a short link hides the real destination."))
    if host.rsplit(".", 1)[-1] in RISKY_TLDS:
        out.append((15, f"{host}: ends with a domain type often used in scams."))
    if re.search(r"\.(exe|apk|scr|zip)$", u.path.lower()):
        out.append((20, "The link downloads a program file."))
    if len(url) > 100:
        out.append((5, "The link is unusually long."))
    if not official:
        tokens = set(re.split(r"[.\-]", host.translate(LEET)))   # whole words only, so "possible" never matches "sbi"
        label = reg.split(".")[0].translate(LEET)
        for brand, doms in OFFICIAL.items():
            if brand in tokens:
                out.append((35, f"{host}: uses the name '{brand}' but is not its real site ({', '.join(doms)})."))
                break
            if len(brand) > 4 and label != brand and SequenceMatcher(None, label, brand).ratio() >= 0.82:
                out.append((35, f"{host}: looks like a misspelling of '{brand}' (typosquatting)."))
                break
    return out


def find_urls(text):
    return [u.rstrip(".,)") for u in re.findall(r"(?:https?://|www\.)[^\s<>\"']+", text)]


def analyze(text):
    """Returns (score 0-100, list of reasons)."""
    found = []
    for url in find_urls(text):
        found += analyze_url(url)
    low = text.lower()
    for pattern, pts, why in TEXT_RULES:
        if re.search(pattern, low):
            found.append((pts, why))
    for mail in re.findall(r"[\w.+-]+@([\w.-]+\.\w+)", low):
        if mail in FREE_MAIL and re.search(r"intern|hiring|recruit|\bhr\b|scholarship|offer|career", low):
            found.append((15, f"A hiring/scholarship message from a free email (@{mail}), not a company domain."))
    if text.count("!") >= 3:
        found.append((5, "Too many exclamation marks."))
    return min(100, sum(p for p, _ in found)), [r for _, r in found]
