"""LIVE checks on a link: where it really leads, certificate, domain age, VirusTotal."""
import base64
import ipaddress
import socket
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
import urllib3

from core.scam_rules import analyze_url, registered_domain

urllib3.disable_warnings()   # we may open broken-certificate sites on purpose, only to read the headers
HEADERS = {"User-Agent": "Mozilla/5.0 (CampusMate link checker)"}


def is_public(url):
    """Safety guard: never let OUR server open private/internal addresses."""
    host = urlparse(url).hostname
    if not host:
        return False
    try:
        for info in socket.getaddrinfo(host, None):
            ip = ipaddress.ip_address(info[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
                return False
    except Exception:
        return False
    return True


def follow(url, max_hops=6):
    """Follows redirects by hand (every hop is checked). Reads headers only, never downloads the page."""
    chain, cur, ssl_ok = [url], url, True
    for _ in range(max_hops):
        if not is_public(cur):
            return {"chain": chain, "ssl_ok": ssl_ok, "error": "Could not reach this address. The site may not exist."}
        try:
            r = requests.get(cur, headers=HEADERS, timeout=8, allow_redirects=False, stream=True)
        except requests.exceptions.SSLError:
            ssl_ok = False                                    # certificate is invalid or fake
            try:
                r = requests.get(cur, headers=HEADERS, timeout=8, allow_redirects=False, stream=True, verify=False)
            except requests.RequestException as e:
                return {"chain": chain, "ssl_ok": False, "error": f"Could not open the link ({type(e).__name__})."}
        except requests.RequestException as e:
            return {"chain": chain, "ssl_ok": ssl_ok, "error": f"Could not open the link ({type(e).__name__})."}
        status, loc = r.status_code, r.headers.get("Location")
        r.close()
        if status in (301, 302, 303, 307, 308) and loc:
            cur = urljoin(cur, loc)
            chain.append(cur)
            continue
        return {"chain": chain, "final": cur, "status": status, "ssl_ok": ssl_ok}
    return {"chain": chain, "final": cur, "ssl_ok": ssl_ok, "error": "Too many redirects."}


def domain_age_days(host):
    """Age of the domain from the public RDAP registry (None if unknown)."""
    try:
        r = requests.get(f"https://rdap.org/domain/{registered_domain(host)}", headers=HEADERS, timeout=8)
        if r.status_code == 200:
            for ev in r.json().get("events", []):
                if ev.get("eventAction") == "registration":
                    made = datetime.fromisoformat(ev["eventDate"].replace("Z", "+00:00"))
                    return (datetime.now(timezone.utc) - made).days
    except Exception:
        pass
    return None


def virustotal(url, key):
    uid = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
    head = {"x-apikey": key}
    try:
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{uid}", headers=head, timeout=15)
        if r.status_code == 404:
            requests.post("https://www.virustotal.com/api/v3/urls", headers=head, data={"url": url}, timeout=15)
            return {"submitted": True}
        if r.status_code == 401:
            return {"error": "VirusTotal did not accept the key."}
        if r.status_code == 429:
            return {"error": "VirusTotal limit reached (free plan: 4 checks a minute). Wait and retry."}
        if r.status_code != 200:
            return {"error": f"VirusTotal error {r.status_code}"}
        s = r.json()["data"]["attributes"]["last_analysis_stats"]
        return {"malicious": s.get("malicious", 0), "suspicious": s.get("suspicious", 0), "total": sum(s.values())}
    except Exception as e:
        return {"error": f"Could not reach VirusTotal ({type(e).__name__})."}


def inspect(url, vt_key=""):
    """Runs every live check on one link. Returns (lines to show, extra risk points, reasons, known_threat)."""
    lines, extra, reasons, threat = [], 0, [], False
    trace = follow(url)
    final = trace.get("final", url)
    host = (urlparse(final).hostname or "").lower()
    if trace.get("error"):
        lines.append(f"🌐 {trace['error']}")
        extra += 10
        reasons.append("The link could not be opened, which is common for dead or fake pages.")
    else:
        hops = len(trace["chain"]) - 1
        lines.append(f"🔗 Real destination: **{host}**" + (f" (after {hops} redirect{'s' if hops > 1 else ''})" if hops else ""))
        if registered_domain(host) != registered_domain(urlparse(url).hostname or ""):
            extra += 10
            reasons.append(f"The link hides where it goes. It really leads to {host}.")
            reasons += [why for _, why in analyze_url(final)]
    if not trace["ssl_ok"]:
        lines.append("🔒 Certificate: **invalid**")
        extra += 25
        reasons.append("The website's security certificate is invalid.")
    elif final.startswith("https"):
        lines.append("🔒 Certificate: valid")
    age = domain_age_days(host) if host else None
    if age is None:
        lines.append("📅 Domain age: unknown")
    else:
        lines.append(f"📅 Domain age: **{age} days**")
        if age < 30:
            extra += 25
            reasons.append(f"The domain was created only {age} days ago. Scam sites are usually brand new.")
        elif age < 180:
            extra += 10
            reasons.append(f"The domain is less than 6 months old ({age} days).")
    if vt_key:
        vt = virustotal(final if not trace.get("error") else url, vt_key)
        if vt.get("error"):
            lines.append(f"🧪 VirusTotal: {vt['error']}")
        elif vt.get("submitted"):
            lines.append("🧪 VirusTotal: first time seen. It was sent for scanning, so check again in a minute.")
        else:
            lines.append(f"🧪 VirusTotal: **{vt['malicious']}** malicious, {vt['suspicious']} suspicious out of {vt['total']} engines")
            if vt["malicious"]:
                threat = True
                extra += min(80, 40 + 10 * vt["malicious"])
                reasons.append(f"{vt['malicious']} security engines on VirusTotal flag this link as dangerous.")
            elif vt["suspicious"]:
                extra += 15
                reasons.append("Some security engines on VirusTotal find this link suspicious.")
    else:
        lines.append("🧪 VirusTotal: add a key (sidebar → API keys) to turn this check on.")
    return lines, extra, reasons, threat
